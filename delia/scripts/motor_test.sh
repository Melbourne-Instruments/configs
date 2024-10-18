set -e
echo "run motor test"
python3 ~/delia/scripts/soakTest.py &
python3 ~/delia/scripts/ledTest.py &

echo "1" > /udata/delia/calibration/motor_test_has_run.txt

sync
sync -f
echo "done"
