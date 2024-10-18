#!/usr/bin/env bash
set -e
python3 /home/root/delia/scripts/wtPrune.py
sync
sync -f