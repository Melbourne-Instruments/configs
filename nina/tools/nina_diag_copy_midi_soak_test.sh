#!/usr/bin/env bash
echo hello
elk_system_utils --remount-as-rw
cp -v /media/run_script.service /lib/systemd/system/
rm /udata/test.log
cp -v /media/nina_test.sh /udata/
systemctl start run_script.service
systemctl enable run_script.service

sync /
