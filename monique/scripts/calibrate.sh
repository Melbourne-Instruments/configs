set -e
option=$1
echo $option
if [[ $option == "filter" ]]
then 
echo "run filter"
python3 -u /home/root/delia/delia_vst.vst3/Contents/RunCalibration.py --filter > /udata/delia/calibration/cal.log
sync /udata/delia/calibration/*
sync -f /udata/delia/calibration/*
sync /dev/mmcblk0p4
sync -f  /dev/mmcblk0p4
sleep 1
sync
sync -f 
echo "done"
exit

elif [[ $option == "mix-vca" ]]
then
echo "run mix "
python3 -u /home/root/delia/delia_vst.vst3/Contents/RunCalibration.py --vca-main > /udata/delia/calibration/cal.log
sync /udata/delia/calibration/*
sync -f /udata/delia/calibration/*
sync /dev/mmcblk0p4
sync -f /dev/mmcblk0p4
echo "1" > /udata/delia/calibration/1_1_mix_cal.txt
sleep 1
sync
sync -f 
echo "done"
exit
fi
echo "run all"
return_code=$(python3 /home/root/delia/delia_vst.vst3/Contents/RunCalibration.py --check-temp)
if [[ "$return_code" -eq 1 ]]; then
    exit $return_code
fi
python3 -u /home/root/delia/delia_vst.vst3/Contents/RunCalibration.py --factory-cal > /udata/delia/calibration/cal.log
sync /udata/delia/calibration/*
sync -f /udata/delia/calibration/*
sync -f /dev/mmcblk0p4
sleep 1
echo "done"