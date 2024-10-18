#!/usr/bin/env bash
echo "run bank export"
set -e
for i; do
    echo $i
done

bank_name_no_number=${i:4}
echo $bank_name_no_number

patch_path="/udata/delia/presets/"

#make directory for patches if it doesn't exist
mkdir -p /tmp/DELIA_BANK_$bank_name_no_number

#remove anything that could be left inside
rm -f /tmp/DELIA_BANK_$bank_name_no_number/*

#copy every file that matches patch pattern and doesn't match BLANK.json pattern
cp $(find $patch_path$i  | grep -E \d*[_]{1}.*json | grep -v -E \d*[_]{1}BLANK\.json) /tmp/DELIA_BANK_$bank_name_no_number

#run script to scan and copy needed wavetables to folder
python3 /home/root/delia/scripts/wtExportBank.py $bank_name_no_number

#x86
#python3 ./wtExportBank.py $i

#make the zip of patches and exit with no error if there are no files
rm -f /tmp/DELIA_BANK_$bank_name_no_number.zip
cd /tmp/DELIA_BANK_$bank_name_no_number
if ! zip -vr9 /tmp/DELIA_BANK_$bank_name_no_number.zip ./; then
    echo "likely no presets to zip"
    exit 0
fi

#find the mount point so we can sync it just to be safe
MOUNT=$(findmnt -n -o SOURCE --target /media | tail -n 1)
cp -v /tmp/DELIA_BANK_$bank_name_no_number.zip /media/

sync /media/*
sync -f /media/*
echo $MOUNT
sync $MOUNT
sync -f $MOUNT
sleep 1
echo "done"
