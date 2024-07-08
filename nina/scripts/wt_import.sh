#!/usr/bin/env bash
set -e

#remove files from previous imports
rm -rf /tmp/user_wavetables
rm -f /tmp/wavetable_error.txt
mkdir  /tmp/user_wavetables

#unzip the wavetables to import to a temp directory
tmp=/media/nina_wavetables.zip

if test -f "$tmp"; then
    echo "$tmp exists."
else
    echo "no wt to unzip"
    exit 0
fi
unzip /media/nina_wavetables.zip -d /tmp/user_wavetables

#remove any . files or __MACOSX folder (from osX)
rm -f $(find /tmp/user_wavetables -name ".*")
rm -rf $(find /tmp/user_wavetables -name "__MACOSX")

#run script that copies files to the wavetable directory
python3 ~/nina/scripts/loadUserWt.py
sync /udata/nina/wavetables/*
sync /dev/mmcblk0p4
sync
sleep 1
echo "done"