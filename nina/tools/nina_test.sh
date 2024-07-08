#!/usr/bin/env bash
echo hello >> /udata/test.log

echo "sleeping for 30 min" >> /udata/test.log
sleep 3600

echo check if sushi is runing  >> /udata/test.log
id=$(pidof sushi)
echo $id
if [ -n "$id" ]; then
    
    echo "sushi running, kill everything" >> /udata/test.log
    kill -9 $id;
    
    id=$(pidof nina_ui)
    echo $id
    if [ -n "$id" ]; then
        echo "kill ui" >> /udata/test.log
        kill -9 $id;
    fi
    
    id=$(pidof nina_gui)
    echo $id
    if [ -n "$id" ]; then
        echo "kill gui" >> /udata/test.log
        kill -9 $id;
    fi
    echo rebooting.... >> /udata/test.log
    
    reboot now
else
    echo sushi has crashed >> /udata/test.log
fi
