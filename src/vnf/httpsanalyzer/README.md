# netflow-SHIELD

## Overview

System service for integrating both raw and processed traffic in Apache Spot cluster.
This service is composed by two different parts:

* Raw traffic: It captures the netflow traffic with [softflowd](https://www.mindrot.org/projects/softflowd/) and [nfcapd](http://nfdump.sourceforge.net/) services. Softflowd works as a probe and tracks traffic flows recorded by listening on a network interface. A probe can be either on a router, switch or on a "mirror" port on which the traffic from the router/switch is sent to. In this case the probe is on a "mirror" port. These flows are read via nfcapd, the netflow capture daemon of the nfdump tools, and write it in files on a disk.
Then, the [d-collector](https://github.com/spacehellas/incubator-spot/blob/SHIELD_H2020/spot-ingest/d-collector/README.md) module is used to send all the captured netflow traffic to the Apache Spot cluster via a Kafka bus.
> The [worker](https://github.com/spacehellas/incubator-spot/blob/SHIELD_H2020/spot-ingest/worker/README.md) module must be used to complete the functionality of the d-collector module. Nevertheless, this module is not part of this service because it should be integrated in one of the Apache Spot virtual machines. The worker will save the data in the correct location of the Hive database and HDFS filesystem making it available for the Apache Spot Machine Learning module (LDA algorithm).


* Processed traffic: It captures the netflow traffic with [tstat](http://tstat.polito.it/logos.shtml) tool. It is a passive sniffer able to provide several insight on the traffic patterns at both the network and the transport levels. This tool is used in two different modes:
 * Forensic: This mode uses the official tstat code (tstat-3.1.1). It records one entry flow per completed transaction. The data is used to be processed is allocated in the file *log_tcp_complete*.

 * Realtime: This mode uses a modified tstat code (tstat_hacked). It records multiple entry flows per only one transaction. This implies the file is much larger than the in the previous mode. The data is used to be processed is allocated in the file *log_tcp_temp_complete*.

 Then, both modes use a python script called *chopper-SHIELD.py*. It processes the output data from tstat and classify them via a machine learning algorithm. The machine learning result is sent in CSV format to the Apache Spot via a Kafka bus (different from the Kafka bus for raw data). The CSV fields are mostly the same ones as the output fields of the Apache Spot spot-ml module or the input for the spot-oa module ([spot-oa column](https://github.com/mpereaji/incubator-spot/blob/Spot-Schemas/spot-setup/APACHE-SPOT-SCHEMA.md#flow-spot-nfdump)). The chopper-SHIELD.py script adds two more fields which correspond with the tag and the tag name for the classified traffic.

 > It should be created a modified [worker](https://github.com/spacehellas/incubator-spot/blob/SHIELD_H2020/spot-ingest/worker/README.md) module that will be able to parse the output fields for this stage and save them in the correct location of the Hive database and HDFS filesystem in the Apache Spot. The data will be available for the Apache Spot Operational Analytics-Visualization module.


## Getting Started

### Prerequisites

* softflowd
* spot-nfdump
* d-collector
* tstat

#### softflowd configuration

The software doesn’t run automatically, we have to configure it to listen on a particular interface. To configure it edit `/etc/default/softflowd` file and define the INTERFACE and OPTIONS variables as follows:

```
INTERFACE="ens7"                             # Network interface
OPTIONS="-n 127.0.0.1:9995 -v 9 -t tcp=60s"
```

#### spot-nfdump installation

For the netflow-SHIELD service is used the modified [nfdump](https://github.com/Open-Network-Insight/spot-nfdump) tool used in the Apache Spot service instead of the official nfdump service. The instructions to install it can be found in http://spot.incubator.apache.org/doc/.

```
$ sudo apt-get install build-essential -y
$ git clone https://github.com/Open-Network-Insight/spot-nfdump.git
$ cd spot-nfdump
$ ./install_nfdump.sh
```

#### d-collector configuration

As it can be seen in the [d-collector](https://github.com/spacehellas/incubator-spot/tree/SHIELD_H2020/spot-ingest/d-collector#configuration) oficial documentation, the *.d-collector.json* file should be configured before executing the service. The configuration used for netflow-SHIELD service is the following one:

```
{
    "kerberos": {
        "kinit": "/usr/bin/kinit",
        "principal": "user",
        "keytab": "/opt/security/user.keytab"
    },
    "pipelines": {
        "flow": {
            "file_watcher": {
                "collector_path": "/var/test_netflow",
                "recursive": "true",
                "supported_files": ["nfcapd.[0-9]{14}", "nfcapd.*.old"]
            },
           "local_staging": "/tmp",
           "process_opts": ""
        }
    },
    "producer": {
        "bootstrap_servers": ["kafka:9092"],
        "max_request_size": 4194304
    }
}
```

It should be notice that the **kafka** server in the boostrap_servers corresponds with the the kafka instance in the Apache Spot cluster. It is defined in the `/etc/hosts`. In this case the kafka server is the cloudera-host2-spot-edge. However, this option should be **configured** as corresponds for each case.

The **collector_path** variable should be the same one as the `DIR` variable described in the next section. The *collector_path* is the monitored directory by the d-collector, to detect new generated files and send it to the Kafka bus. For this reason, it should be the same one as the directory where nfcapd saves the collected netflow files.



### netflow-SHIELD configuration

The netflow-SHIELD configuration file is placed in `/etc/default/netflow-SHIELD`. The variables used to configure the service are explained hereunder:

* Softflowd configuration

  * `INTERFACE`: Network interface where softflowd should be listening to (e.g.: `ens7`).
  * `SOFT_OPTIONS`: Additional [flags](https://www.freebsd.org/cgi/man.cgi?query=softflowd&sektion=8&manpath=freebsd-release-ports) to run softflowd service (default: `-n 127.0.0.1:9995 -v 9 -t tcp=60s`).


* Nfcapd configuration

 * `DIR`: Directory where nfcapd stores the collected netflow files (default: `/var/test_netflow`).
 * `NFCAPD_OPTIONS`: Additional flags to properly run spot-nfdump service (default: `-w -T all`).


* D-collector configuration

 * `INGEST_TOPIC`: Kafka bus name to send the *raw* netflow data to Apache Spot cluster (default: `SPOT-INGEST-TEST-TOPIC`).
 * `TRAFFIC`: One of the pipelines configured in *.d-collector.json*. In this case, the flow type is the only one configured. Therefore, this variable only can be `flow`.


* Tstat configuration

 * `MODE`: Mode in which tstat should work. As it was explained before, the only two available modes are: `forensic` and `realtime` (default: `forensic`).
 * `NETWORK`: Path where the trained network for machine learning is placed.

* Chopper-SHIELD configuration
 * `ML_TOPIC`: Kafka bus name to send the *proccesed* netflow data to Apache Spot cluster (default: `SPOT-ML-TEST-TOPIC`).
 * `TIME_LIMIT`: Time in **seconds** that *chopper-SHIELD.py* should wait from the last line read until check if tstat generate a new directory. This variable is needed because tstat has a time interval in which it collects the traffic. Once this time expires, it generates another file in other directory with different name in which it saves the traffic. If *chopper-SHIELD.py* does not check if tstat generates other directories, the netflow-SHIELD service would not process all the traffic collected by tstat (default: `5`).

Example:

```
# Softflowd configuration
INTERFACE="ens7"
SOFT_OPTIONS="-n 127.0.0.1:9995 -v 9 -t tcp=60s"

# Nfcapd configuration
DIR="/var/test_netflow"
NFCAPD_OPTIONS="-w -T all"

# d-collector configuration for Ingestion stage in Apache-Spot
INGEST_TOPIC="SPOT-INGEST-TEST-TOPIC"
TRAFFIC="flow"

# Tstat configuration
MODE="forensic"
NETWORK="/home/cognet/tid-rf.pkl"

# Chopper configuration for Machine Learning stage in Apache-Spot
ML_TOPIC="SPOT-ML-TEST-TOPIC"
TIME_LIMIT=5
```

### netflow-SHIELD installation

The netflow-SHIELD service is integrated as a system service. For doing this it is necessary to create a file in `/etc/systemd/system/netflow-SHIELD.service`:

```
[Unit]
Description = Netflow-SHIELD daemon

[Service]
Type = forking
ExecStart = /usr/local/bin/netflow-SHIELD.sh start
ExecStop = /usr/local/bin/netflow-SHIELD.sh stop

[Install]
WantedBy = multi-user.target
```

As it can be seen it is needed a bash script located in `/usr/local/bin` called `netflow-SHIELD.sh`. This is the real script in charge of starting and stopping all the required processes that comprise the netflow-SHIELD service.

Once both files are created, it is necessary to reload the systemctl configuration:

```
$ sudo systemctl daemon-reload
```

### Running netflow-SHIELD

As netflow-SHIELD is part of the systemctl services, it can be started and stoped as follows:

```
$ sudo systemctl start netflow-SHIELD
```

```
$ sudo systemctl stop netflow-SHIELD
```
