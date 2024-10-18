set -e
echo "kill python"
id=$(pidof python3)
kill -9 $id
echo "done"
