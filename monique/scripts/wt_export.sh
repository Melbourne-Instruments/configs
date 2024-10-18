#!/usr/bin/env bash
set -e

MOUNT=$(findmnt -n -o SOURCE --target /media | tail -n 1)
python3 /home/root/delia/scripts/backupUserWt.py
sync
sync -f
cd /tmp/wt_backup
if zip -vr1 /tmp/delia_wavetables.zip  . ; then 
    scp /tmp/delia_wavetables.zip /media/
fi

sync -f /media/*
echo $MOUNT
sync $MOUNT
sync -f $MOUNT
sleep 1
echo "done"

