#delete msg file and create empty new file 
rm -vf /media/qc_check_msg.txt
touch /media/qc_check_msg.txt

cd /media

#check current sw version 
if [ "$(cat /etc/sw_version)" != "1.0.5" ]; then 
    echo wrong sw version "$(cat /etc/sw_version)"
    echo "FW VERSION NG" >> /media/qc_check_msg.txt
    exit 0
fi

#check filter tuning
python3 /media/checkFilter.py

#exit the test here if the filter failed
exit=$?
if [ "$exit" -ne "0" ]; then
    echo filter failed
    echo "FILTER NG" >> /media/qc_check_msg.txt 
    cat /tmp/filter_failed_voices.txt >> /media/qc_check_msg.txt
    exit 0
fi

#clear & load patches
rm -vrf /udata/delia/presets/*
unzip /media/delia_presets_backup.zip -d /udata/delia/

#check patches
python3 /media/fileCheck.py --preset 
exit=$?
if [ "$exit" -ne "0" ]; then
    echo presets failed
    echo "PRESETS NG" >> /media/qc_check_msg.txt 
    exit 0
fi

#set patch select to 1, 1 & delete scratch patch files
cp -v /media/config.json /udata/delia/config.json
rm -vf /udata/delia/current_preset_a.json
rm -vf /udata/delia/current_preset_b.json
rm -vf /udata/delia/prev_preset.json

#load wavetables & check
unzip -o /media/DELIA_WAVETABLES.zip -d /udata/delia/wavetables/
python3 /media/fileCheck.py --wt
exit=$?
if [ "$exit" -ne "0" ]; then
    echo Wavetables failed
    echo "WAVETAVLES NG" >> /media/qc_check_msg.txt 
    exit 0
fi

#check other files 
python3 /media/fileCheck.py -
exit=$?
if [ "$exit" -ne "0" ]; then
    echo system files failed
    echo "FILES NG" >> /media/qc_check_msg.txt 
    exit 0
fi
echo "TEST OK" >> /media/qc_check_msg.txt