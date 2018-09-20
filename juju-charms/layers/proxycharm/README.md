# Overview

This repository contains the [Juju] layer that represents a charm for a VNSF Proxy.

# What is a proxy charm?

A proxy charm is a limited type of charm that does not interact with software running on the same host, such as controlling and configuring a remote device (a static VM image, a router/switch, etc.). It cannot take advantage of some of Juju's key features, such as [scaling], [relations], and [leadership].

Proxy charms are primarily a stop-gap, intended to prototype quickly, with the end goal being to develop it into a full-featured charm, which installs and executes code on the same machine as the charm is running.

# Usage

```bash
# Clone this repository
cd juju-charms

# Setup environment variables
source juju-env.sh

cd layers/proxycharm
charm build

# Examine the built charm
cd ../../builds/proxycharm
ls
actions       config.yaml  icon.svg    metadata.yaml     tests
actions.yaml  copyright    layer.yaml  reactive          tox.ini
bin           deps         lib         README.md         wheelhouse
builds        hooks        Makefile    requirements.txt

```

The `charm build` process combines this `proxycharm` layer with each layer that it
has included in the `metadata.yaml` file, along with their various dependencies.

This built charm is what will then be used by the SO to communicate with the
VNF.

# Configuration

The `proxycharm` charm has several configuration properties that can be set via
the SO:

- ssh-hostname
- ssh-username
- ssh-password
- ssh-private-key

The ssh-* keys are included by the `sshproxy` layer, and enable the charm to
connect to the VNF image.

Once those values are set, the `sshproxy.configured` state flag will be toggled.

# Reactive states

The layers will set the following states:

- `sshproxy.configured` This state is set when SSH credentials have been supplied to the charm.
- `proxycharm.configured` This state is set after verifying the ssh credentials and running the API that will manage the actions called to the charm.

# Actions

In `reactive/proxycharm.py`, you can add more logic to execute commands over SSH. The actual proxycharm has the following actions:

-	`get-policies` -> Get the MSPL policies.
-	`set-policies` -> Set the MSPL policies.
-	`delete-policy` -> Delete a specific MSPL policy.
-	`delete-policies` -> Delete all MSPL policies.
-	`add-url` -> Adds any number of URLs to the alert/monitor list.
-	`delete-url` -> Deletes any number of URLs in alert/monitor list.
-	`start` ->  Starts the API (restful service).
-	`stop` -> Stops the API (restful service).
- `restart` -> Restarts the API (restful service).
- `start-proxy` -> Starts the man in the middle proxy.
- `stop-proxy` -> Stops the man in the middle proxy.
- `restart-proxy` -> Restarts the man in the middle proxy.
- `start-collector` -> Starts the collector.
- `stop-collector` -> Stops the collector.
- `restart-collector` -> Restarts the collector.

For setting, adding and deleting policies, we must pass an xml from the client, which follows the MSPL format schema.
For example:

```
$ curl -X POST -H "Content-Type: text/plain" -d @XML_file http://IP_ADRESS:8080/set-policies
$	curl http://IP_ADRESS:8080/get-policies
```

Using OSM r4 interface, after instantiating, go to NS Instances -> Actions-> Exec NS Primitive.
A new window will appear, with four fields (Primitive / VNF Member index / Name / Value).
The first two are always complusory, you must write the name of the action and VNF Member index.
The other two are Primitive parameters, used for example in a `set-policies`.

To run an action from the OSM terminal:

```
$ juju run-action mycharm/0 actionname
```

## Known Limitations and Issues

### Security issues

- Password and key-based authentications are supported, with the caveat that
both (password and private key) are stored plaintext within the Juju controller.
