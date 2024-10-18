#!/usr/bin/env bash
set -e
for i; do
    echo $i
done

bank_added_num=$(python3 /home/root/delia/scripts/addBank.py)
echo "created bank $bank_added_num"

sync
sync -f

#return the number of the added bank
exit $bank_added_num