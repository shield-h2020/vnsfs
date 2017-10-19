#!/usr/bin/env bash

lan_iface="eth1"
wan_iface="eth2"


function trimWhitespaces {
        echo "$(echo -e "${1}" | tr -d '[[:space:]]')"
}


ovs-vsctl add-br br0
ovs-vsctl add-port br0 $lan_iface
ovs-vsctl add-port br0 $wan_iface


lan_id=$(ovs-ofctl dump-ports-desc br0 | grep $lan_iface | awk -F "(" '{print $1}')
wan_id=$(ovs-ofctl dump-ports-desc br0 | grep $wan_iface | awk -F "(" '{print $1}')

lan_id=$(trimWhitespaces $lan_id)
wan_id=$(trimWhitespaces $wan_id)


ovs-ofctl add-flow br0 priority=1,in_port=$lan_id,dl_type=0x800,\
actions=output:$wan_id

ovs-ofctl add-flow br0 priority=1,in_port=$wan_id,dl_type=0x800,\
actions=output:$lan_id
