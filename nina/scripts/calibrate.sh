set -e
option=$1
echo $option
if [[ $option == "filter" ]]
then 
echo "run filter"
python3 -u /home/root/nina/synthia_vst.vst3/Contents/RunCalibration.py --filter > /udata/nina/calibration/cal.log
sync /udata/nina/calibration/*
sync /dev/mmcblk0p4
sleep 1
sync
echo "done"
exit

elif [[ $option == "mix-vca" ]]
then
echo "run mix "
python3 -u /home/root/nina/synthia_vst.vst3/Contents/RunCalibration.py --vca-mix > /udata/nina/calibration/cal.log
sync /udata/nina/calibration/*
sync /dev/mmcblk0p4
echo "1" > /udata/nina/calibration/1_1_mix_cal.txt
sleep 1
sync
echo "done"
exit
fi
echo "run all"
return_code=$(python3 /home/root/nina/synthia_vst.vst3/Contents/RunCalibration.py --check-temp)
if [[ "$return_code" -eq 1 ]]; then
    exit $return_code
fi
python3 -u /home/root/nina/synthia_vst.vst3/Contents/RunCalibration.py --factory-cal > /udata/nina/calibration/cal.log
sync /udata/nina/calibration/*
sync /dev/mmcblk0p4
sleep 1
echo "done"