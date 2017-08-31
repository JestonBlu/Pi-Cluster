#!/bin/sh
ip addr add 192.168.1.1/24 broadcast 192.168.1.255 dev eth0
systemctl start dhcpd4@eth0.service
