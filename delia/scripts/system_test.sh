#!/usr/bin/env bash
python3 /home/root/delia/scripts/system_test.py
pass=$?
sync -f /media
sync
exit $pass