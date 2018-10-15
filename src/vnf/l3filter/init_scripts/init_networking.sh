#!/bin/bash

if [ $# -ne 3 ]
  then
    echo "[ERROR] Not enough arguments supplied"
    exit 1
fi

IN_IFACE=$1
OUT_IFACE=$2
BR_NAME=$3

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

# If in_interface and out_interface not configured, do so
if ! grep -qF "auto $IN_IFACE" /etc/network/interfaces.d/50-cloud-init.cfg && ! grep -qF "auto $OUT_IFACE" /etc/network/interfaces.d/50-cloud-init.cfg; then
  sudo sh -c "echo 'auto ${IN_IFACE}\niface ${IN_IFACE} inet dhcp\nauto ${OUT_IFACE}\niface ${OUT_IFACE} inet dhcp'  >> /etc/network/interfaces.d/50-cloud-init.cfg"
  sudo sh -c '/etc/init.d/networking restart'
  echo "[DEBUG] Copied ingress-egress interface configuration. Network restarted"
fi

# If bridge not existent, create it
if [ ! -d "/sys/devices/virtual/net/$BR_NAME/" ]; then
  sudo brctl addbr $BR_NAME
  sudo brctl addif $BR_NAME $IN_IFACE $OUT_IFACE
  sudo ifconfig $BR_NAME up
  echo "[DEBUG] Bridge between ingress-egress interfaces configured and up."
fi

sudo modprobe br_netfilter
echo "[DEBUG] Loading kernel module for iptables setting on a bridge."
