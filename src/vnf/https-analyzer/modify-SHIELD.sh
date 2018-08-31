#!/bin/bash
# USAGE: sudo bash modify-SHIELD.sh target_key replacement_value
CONFIG="/etc/default/netflow-SHIELD"

# INITIALIZE CONFIG IF IT'S MISSING
if [ ! -e "${CONFIG}" ] ; then
    # Set default variables values
    sudo touch $CONFIG
    echo "Config file not found, creating a new one with the following default variables"
    echo "# Softflowd configuration
INTERFACE=\"ens7\"
SOFT_OPTIONS=\"-n 127.0.0.1:9995 -v 9 -t tcp=60s\"

# Nfcapd configuration
DIR=\"/var/test_netflow\"
NFCAPD_OPTIONS=\"-w -T all\"

# d-collector configuration for Ingestion stage in Apache-Spot
INGEST_TOPIC=\"SPOT-INGEST-TEST-TOPIC\"
TRAFFIC=\"flow\"

# Tstat configuration
MODE=\"forensic\"
NETWORK=\"/home/cognet/tid-rf.pkl\"

# Chopper configuration for Machine Learning stage in Apache-Spot
ML_TOPIC=\"SPOT-ML-TEST-TOPIC\"
TIME_LIMIT=5" | sudo tee --append $CONFIG
fi

# LOAD THE CONFIG FILE
source $CONFIG

sudo sed -i "s#^\($1\s*=\s*\"\).*\$#\1$2\"#" $CONFIG
echo "Modify $1 key with $2 value"
#sed -c -i "s#\($TARGET_KEY *= *\).*#\1$REPLACEMENT_VALUE#" $CONFIG_FILE
