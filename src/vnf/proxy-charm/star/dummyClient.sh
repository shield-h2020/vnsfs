#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Illegal number of parameters"
    echo 'USAGE: command $proxyCert $caCert $fullCsr $file'
    echo '       File refers to the cert destination'
    exit 1
fi

proxyCert=$1
caCert=$2
fullCsr=$3
saveAt=$4

#step 1
#returns the final parameters used by the DNO plus the Location
step1=$(curl --cacert $proxyCert -H Content-Type: application/json -X POST -d $fullCsr https://certProxy:443/star/registration)
echo "returning value of step1: $step1"
var=$(echo "$step1" | sed -n 2p | cut -d ":" -f 2,3)


echo "URI is: $var End of uri."

#step 2
#returns {status, lifetime, certificate's final URI}

step2=$(curl --cacert $proxyCert $var)
echo "Step2 is: $step2"

#step 3
#returns final URI, then retrieves the cert  from step2's last field

step3=$(echo "$step2" | cut -d ' ' -f 3 | cut -d "}" -f 1)
echo "Step 3 is: $step3"

sleep 5
curl -I --cacert $caCert $step3

#Use the sudo version if you are not logged in as root
#curl --cacert $caCert $step3 | sudo tee $saveAt
curl --cacert $caCert $step3 | tee $saveAt


echo "end of Client"
