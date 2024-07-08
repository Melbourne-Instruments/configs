#!/usr/bin/env bash

ARG1="${1:-nina-pi-dv8}"
echo $ARG1

ssh -o StrictHostKeyChecking=no root@$ARG1.local "tar  -czvf /udata/patches_backup.tgz  /udata/nina/presets; exit;"
scp -o StrictHostKeyChecking=no root@$ARG1.local:/udata/patches_backup.tgz ~/Desktop

echo "done"