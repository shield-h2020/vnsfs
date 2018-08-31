#!/bin/bash

iptables -t nat -A OUTPUT -p tcp --dport 80 -d 192.168.122.133 -j DNAT --to-destination 192.168.122.218
