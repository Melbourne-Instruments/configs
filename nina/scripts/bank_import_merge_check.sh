#!/usr/bin/env bash
set -e
for i; do
    echo $i
done
i=$1
target=$2
echo "source $i"
echo "dest $target"
MOUNT=$(findmnt -n -o SOURCE --target /media | tail -n 1)

#remove files from old imports
rm -rf /tmp/nina_bank_import
mkdir -p /tmp/nina_bank_import

#extract the files to import to the tmp import folder
tmp=/media/$i
echo $tmp
if test -f "$tmp"; then
    echo "$tmp exists, load this"
    unzip  $tmp -d /tmp/nina_bank_import/
else
    echo "no patches to unzip"
fi

#run the script that does the bank merge
#python3 ./overwriteBank.py $target
python3 /home/root/nina/scripts/mergeBank.py check $target
sync


