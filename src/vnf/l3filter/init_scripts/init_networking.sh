#!/bin/bash

if [ $# -ne 1 ]
  then
    echo "[ERROR] Not enough arguments supplied"
    exit 1
fi

WAN_INTERFACE=$1
echo "[DEBUG] WAN interface is $WAN_INTERFACE"

# Default route must be removed before creating a new one
sudo ip route del default
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F
sudo iptables -t nat -X
sudo iptables -t mangle -F
sudo iptables -t mangle -X
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
echo "[DEBUG] Flushed iptables configuration."

wan_subnet=$(ip route | grep $WAN_INTERFACE | awk '{print $1}')
wan_ip=$(ifconfig $WAN_INTERFACE 2>/dev/null | awk '/inet addr:/ {print $2}'| sed 's/addr://')
echo "[DEBUG] WAN subnet is $wan_subnet and IP is $wan_ip"
wan_available_ips=$(nmap -sn $wan_subnet -oG - | awk '$4=="Status:" && $5=="Up" {print $2}')
for ip in $wan_available_ips
do
  if [ $ip != $wan_ip ] && [ $(echo $ip | cut -f 4 -d.) != "1" ]; then
    wan_next_hop=$ip
  fi
done

sudo ip route add default via $wan_next_hop dev $WAN_INTERFACE
echo "[DEBUG] Setted default route via $wan_next_hop for $WAN_INTERFACE"
