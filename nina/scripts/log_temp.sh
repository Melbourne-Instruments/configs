#!/usr/bin/env bash
while true
do
    cat /sys/class/thermal/thermal_zone0/temp >> /udata/thermal_log.txt
    sleep 10
done