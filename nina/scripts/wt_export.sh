#!/usr/bin/env bash
set -e

MOUNT=$(findmnt -n -o SOURCE --target /media | tail -n 1)
python3 /home/root/nina/scripts/backupUserWt.py
sync
cd /tmp/wt_backup
if zip -vr1 /tmp/nina_wavetables.zip  . ; then 
    scp /tmp/nina_wavetables.zip /media/
fi

sync /media/*
echo $MOUNT
sync $MOUNT
sleep 1
echo "done"

