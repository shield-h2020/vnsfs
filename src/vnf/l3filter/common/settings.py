# TCP port of the REST API server
rest_api_port = 9999
# LAN interface towards the internal (user) network
lan_interface = "eth1"
# WAN interface towards the external (gateway) network
wan_interface = "eth2"
# Name of the custom forward chain in the FILTER table
vnsf_forward_chain = "vnsf-forward-chain"
# Burst limit in rate limiting rules of iptables
iptables_limit_burst = "20"
