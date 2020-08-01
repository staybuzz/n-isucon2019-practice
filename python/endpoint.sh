#!/usr/bin/env bash

while :
do
        curl db:3306 > /dev/null 2>&1
        if [ "$?" == "0" ]; then
                break
        fi
        echo "Wait for db initialization."
        sleep 10
done

python ./app.py
