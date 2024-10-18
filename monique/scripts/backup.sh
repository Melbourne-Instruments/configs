#!/usr/bin/env bash
set -e

if [[ -f "/udata/delia/num_preset_backups.txt" ]]; then
    value=`cat /udata/delia/num_preset_backups.txt`
else
    value="0001"
fi

v2="$(($value + 1))"
num=$( printf '%04d' $v2 )
echo "$num" > /udata/delia/num_preset_backups.txt

echo "$value"
cd /udata/delia
if ! zip -vr9 /tmp/delia_presets_backup_$value.zip $(cd /udata/delia/ && find ./presets  | grep -E \d*[_]{1}.*json | grep -v -E \d*[_]{1}BLANK\.json | cut -c 3-) ; then
    echo "likely no presets to zip"
    exit 0
fi
MOUNT=$(findmnt -n -o SOURCE --target /media | tail -n 1)
scp /tmp/delia_presets_backup_$value.zip /media/

python3 /home/root/delia/scripts/backupUserWt.py

#get the RPI serial number and use it in the cal file backup
serial_no="$(cat /sys/firmware/devicetree/base/serial-number)"
echo serial: $serial_no

#if there is calibration data, then back it up
if test -f "/udata/delia/calibration/voice_0.cal"; then
    if ! zip -vr9 /tmp/calibration_$serial_no.zip /udata/delia/calibration ; then
        echo "cal backup failed"
    fi
    scp /tmp/calibration_$serial_no.zip /media/
fi

cd /tmp/wt_backup
if zip -vr1 /tmp/delia_wavetables_backup_$value.zip  . ; then
    scp /tmp/delia_wavetables_backup_$value.zip /media/
else
    echo "no wavetables to zip"
fi

sync /media/*
sync -f /media/*
echo $MOUNT
sync $MOUNT
sync -f $MOUNT
sleep 1
echo "done"