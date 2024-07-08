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

#run the script that does the bank merge
#python3 ./overwriteBank.py $target
python3 /home/root/nina/scripts/mergeBank.py nocheck $target

sync


