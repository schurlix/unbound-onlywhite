#!/bin/sh
logdir=/var/log/exampy
filename=$(date -Iseconds)
/usr/local/bin/nmap -sn -n 192.168.0.0/24 > ${logdir}/${filename}
