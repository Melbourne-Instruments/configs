#!/usr/bin/env bash
set -e
for i; do
    echo $i
done

#just delete every file in the selected bank
rm -vf /udata/nina/presets/patches/$i/*
sync
