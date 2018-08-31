#!/bin/bash
# /usr/local/bin/netflow-SHIELD.sh

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/bin

NAME=netflow-SHIELD
# softflowd
SOFTFLOWD_NAME=softflowd
SOFTFLOWD_DAEMON=/usr/sbin/softflowd
SOFTFLOWD_PID=/var/run/$SOFTFLOWD_NAME.pid
# netflow
NFCAPD_NAME=nfcapd
NFCAPD_DAEMON=/usr/local/bin/nfcapd
NFCAPD_PID=/var/run/$NFCAPD_NAME.pid
# d-collector
DCOLLECTOR_NAME=d-collector
DCOLLECTOR_DAEMON=/usr/local/bin/d-collector
DCOLLECTOR_PID=/var/run/$DCOLLECTOR_NAME.pid
# chopper
CHOPPER_NAME=chopper-SHIELD
CHOPPER_DAEMON="/usr/bin/python chopper-SHIELD.py"
CHOPPER_PID=/var/run/$CHOPPER_NAME.pid

DEFAULT=/etc/default/$NAME

## Include netflow-SHIELD defaults if available
# Softflowd
INTERFACE=
SOFT_OPTIONS=
# Nfcapd
DIR="/var/test_netflow"
NFCAPD_OPTIONS=
# d-collector
INGEST_TOPIC="SPOT-INGEST-TEST-TOPIC"
TRAFFIC="flow"
# Tstat
MODE="forensic"
NETWORK=
# chopper
ML_TOPIC="SPOT-ML-TEST-TOPIC"
TIME_LIMIT=5

[ -r "$DEFAULT" ] && . "$DEFAULT"

ACTION=$1
#shift
#while [ "$1" != "" ]; do
#    case $1 in
#        -t | --traffic )
#          shift
#          MODE=$1
#          ;;
#        -n | --network )
#          shift
#          NETWORK=$1
#          ;;
#        *)
#        break
#        ;;
#    esac
#    shift
#done
#Usage: sudo sh netflow-SHIELD.sh start/stop [-t traffic -n network]

if [ "$MODE" == "realtime" ]; then
    TSTAT_NAME=tstat_hacked
    TSTAT_FILE=log_tcp_temp_complete
elif [ "$MODE" == "forensic" ]; then
    TSTAT_NAME=tstat-3.1.1
    TSTAT_FILE=log_tcp_complete
fi

TSTAT_DIR=$TSTAT_NAME
TSTAT_DAEMON=$TSTAT_DIR/tstat/tstat
TSTAT_PID=/var/run/"$TSTAT_NAME".pid

# Include
# Source function library.
. /lib/lsb/init-functions

case "$ACTION" in
    start)
       log_daemon_msg "Starting $NAME"
       # Send netflow traffic in csv format to Apache-Spot
       start-stop-daemon --background --start --make-pidfile --pidfile $SOFTFLOWD_PID --name $SOFTFLOWD_NAME --startas $SOFTFLOWD_DAEMON -- -i "$INTERFACE" $SOFT_OPTIONS
       log_daemon_msg "Starting nfcapd"
       start-stop-daemon --background --start --make-pidfile --pidfile $NFCAPD_PID --name $NFCAPD_NAME --startas $NFCAPD_DAEMON -- -l "$DIR" $NFCAPD_OPTIONS
       log_daemon_msg "Sending nfcapd file to apache spot"
       start-stop-daemon --background --start --make-pidfile --pidfile $DCOLLECTOR_PID --name $DCOLLECTOR_NAME --startas $DCOLLECTOR_DAEMON -- --topic "$INGEST_TOPIC" -t "$TRAFFIC"
       # Process netflow traffic with chopper.py and send it to Apache-Spot
       log_daemon_msg "Starting Tstat..."
       start-stop-daemon --background --start --chdir "/home/cognet/" --make-pidfile --pidfile $TSTAT_PID --name $TSTAT_NAME --startas $TSTAT_DAEMON -- -tu -T $TSTAT_DIR/tstat-conf/runtime.conf -G $TSTAT_DIR/tstat-conf/globals.conf -l -i $INTERFACE > /home/cognet/log_capture.txt
       date=$(date +'%Y_%m_%d_%H_%M')
       #sleep 10
       path="stdin/$date.out"
       log_daemon_msg "Starting chopper..."
       start-stop-daemon --background --start --chdir "/home/cognet/" --make-pidfile --pidfile $CHOPPER_PID --name $CHOPPER_NAME --startas $CHOPPER_DAEMON -- $MODE -k "$ML_TOPIC" -t "$path/$TSTAT_FILE" -n "$NETWORK" -l "$TIME_LIMIT"
       log_end_msg $?
       ;;
    stop)
       log_daemon_msg "Stopping $NAME"
       start-stop-daemon --stop --pidfile $SOFTFLOWD_PID  --remove-pidfile
       start-stop-daemon --stop --pidfile $NFCAPD_PID  --remove-pidfile
       start-stop-daemon --stop --pidfile $DCOLLECTOR_PID  --remove-pidfile
       start-stop-daemon --stop --pidfile $TSTAT_PID  --remove-pidfile
       start-stop-daemon --stop --pidfile $CHOPPER_PID  --remove-pidfile
       rm -rf /home/cognet/stdin
       rm -rf $DIR/*
       log_end_msg $?
       ;;
    *)
       echo "Usage: $0 {start|stop}"
esac

exit 0
