## Test package installation

eva_server &> eva.txt &
sleep 10
head -n20 eva.txt

# check if server started
grep "serving" eva.txt
test_code=$?
if [ $test_code -ne 0 ];
then
    echo "Server did not start"
    exit $test_code
fi

eva_client &> client.txt &
if [ $test_code -ne 0 ];
then
    echo "Client did not start"
    exit $test_code
fi

head -n20 client.txt
exit 0