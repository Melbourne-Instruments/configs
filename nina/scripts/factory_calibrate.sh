set -e
echo "check temp"
return_code=$(python3 /home/root/nina/synthia_vst.vst3/Contents/RunCalibration.py --check-temp)
if [[ "$return_code" -eq 1 ]]; then
    exit $return_code
fi

echo "run soak test"
python3 ~/nina/scripts/soakTest.py &
python3 ~/nina/scripts/ledTest.py &

sleep 1
~/nina/scripts/log_temp.sh &
sleep 1
python3 -u /home/root/nina/synthia_vst.vst3/Contents/RunCalibration.py --factory-cal > /udata/nina/calibration/cal.log
sync /udata/nina/calibration/*
sync /dev/mmcblk0p4
sleep 1

echo "kill python"
id=$(pidof python3)
kill -9 $id
echo "start knobs slow"
python3 ~/nina/scripts/soakTest.py slow &

echo "1" > /udata/nina/calibration/soak_test_has_run.txt

sync
echo "done"