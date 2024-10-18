#!/usr/bin/env bash
set -e
rm -rf /tmp/user_wavetables
mkdir  /tmp/user_wavetables
# execute `process` once for each file
tmp=/media/delia_wavetables_backup.zip

if test -f "$tmp"; then
    echo "$tmp exists."
else 
    echo "no wt to unzip"
    exit 0
fi

unzip /media/delia_wavetables_backup.zip -d /tmp/user_wavetables
rm -f $(find /tmp/user_wavetables -name ".*")

python3 ~/delia/scripts/loadUserWt.py

sync /udata/delia/wavetables/*
sync /dev/mmcblk0p4
sync
sync -f /udata/delia/wavetables/*
sync -f /dev/mmcblk0p4
sync -f 
sleep 1
echo "done"