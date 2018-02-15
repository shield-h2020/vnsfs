#!/bin/sh

DEV="eth1"
#PoliceRate="2mbit"
#PoliceRate=$1
#Burst="90k"
#filter_rule="src 143.233.227.71"

echo "Deleting pre existing qdisc"

tc qdisc del dev $DEV root 2> /dev/null > /dev/null
tc qdisc del dev $DEV ingress 2> /dev/null > /dev/null

echo -n "Adding ingress qdisc ffff:"
tc qdisc add dev $DEV handle ffff: ingress
echo "DONE"

#echo -n "Setting up a filter for policing traffic, " $filter_rule
#echo -n "at" $PoliceRate

#tc filter add dev $DEV parent ffff: protocol ip prio 1 u32 match ip $filter_rule police rate $PoliceRate burst $Burst drop flowid :1

#tc filter add dev eth0 parent ffff: protocol ip prio 1 u32 match ip src 143.233.227.71 police rate 2mbit burst 1k drop flowid :1

#echo "DONE"

#echo " You made it now send some traffic and enjoy real-time policing with the following command"

#echo "watch -d -n1 tc -s filter show dev $DEV parent ffff:"

