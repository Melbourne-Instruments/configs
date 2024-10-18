set -e
echo "run soak test"
echo "delete cal files related to the vst & audio"
rm -vf /udata/delia/calibration/voice_5.cal
rm -vf /udata/delia/calibration/voice_3.cal
rm -vf /udata/delia/calibration/voice_1_filter.model
rm -vf /udata/delia/calibration/voice_5_filter.model
rm -vf /udata/delia/calibration/voice_1.cal
rm -vf /udata/delia/calibration/filter_cal_status.txt
rm -vf /udata/delia/calibration/vca_cal_status.txt
rm -vf /udata/delia/calibration/voice_2_filter.model
rm -vf /udata/delia/calibration/voice_0.cal
rm -vf /udata/delia/calibration/voice_4.cal
rm -vf /udata/delia/calibration/voice_0_filter.model
rm -vf /udata/delia/calibration/voice_4_filter.model
rm -vf /udata/delia/calibration/soak_test_has_run.txt
rm -vf /udata/delia/calibration/voice_2.cal
rm -vf /udata/delia/calibration/voice_3_filter.model
rm -vf /udata/delia/calibration/cal.log

sync /udata/delia/calibration
sync /dev/mmcblk0p4

echo "start motor/led test"
python3 ~/delia/scripts/soakTest.py &
python3 ~/delia/scripts/ledTest.py &

sleep 1
python3 -u /home/root/delia/delia_vst.vst3/Contents/RunCalibration.py --vca-main >> /udata/delia/calibration/cal.log
python3 -u /home/root/delia/delia_vst.vst3/Contents/RunCalibration.py --vca-filter >> /udata/delia/calibration/cal.log
sync /udata/delia/calibration/*
sync /dev/mmcblk0p4
sync -f /udata/delia/calibration/*
sync -f /dev/mmcblk0p4
sleep 1

echo "kill python"
id=$(pidof python3)
kill -9 $id
echo "start knobs slow"
python3 ~/delia/scripts/soakTest.py slow &

echo "1" > /udata/delia/calibration/soak_test_has_run.txt

sync
sync -f
echo "done"