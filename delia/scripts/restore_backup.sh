#!/usr/bin/env bash
set -e
echo "start restore backup"
~/delia/scripts/backup.sh
~/delia/scripts/loadWt.sh

#find the pi serial number and make a variable which is the expected cal file name
serial_no="$(cat /sys/firmware/devicetree/base/serial-number)"
cal_file="calibration_$serial_no.zip"

#try to copy cal files to /tmp, silent fail
if test -f /media/$cal_file; then
    cp /media/$cal_file /tmp/
fi

rm -rf /tmp/udata
MOUNT=$(findmnt -n -o SOURCE --target /media | tail -n 1)
mkdir -p /tmp/udata/delia
# execute `process` once for each file
tmp=/media/delia_presets_backup.zip

if test -f "$tmp"; then
    echo "$tmp exists, load this"
    unzip $tmp -d /tmp/udata/delia
    rm -f $(find /tmp/udata/delia/ -name ".*")
    python3 ~/delia/scripts/mergePresets.py
    python3 ~/delia/scripts/presetUpdate.py
    sync /udata/delia/presets/*
    sync /dev/mmcblk0p4
    sync
    sync -f /udata/delia/presets/*
    sync -f /dev/mmcblk0p4
    sync -f 
else
    echo "no presets to unzip"
fi

#if the calibration backup exists, then check if the cal is missing on device. if so, then restore the cal files. We check the serial number matches to make sure the correct cal files are being loaded
echo serial: $serial_no
if test -f /tmp/$cal_file; then
    echo "cal backup exists, load if needed"
    if test ! -f "/udata/delia/calibration/voice_0.cal"; then
        echo " cal is missing, restore cal"
        mkdir -p /tmp/calibration
        rm -rf /tmp/calibration/*
        unzip /tmp/$cal_file -d /tmp/calibration/
        cp -v /tmp/calibration/udata/delia/calibration/* /udata/delia/calibration/
    fi
fi

sync

sleep 1
echo "done"