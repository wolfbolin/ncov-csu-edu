#!/bin/bash
cur_time=$(date "+%H:%M")
if [[ "10:00" < ${cur_time} ]];then
    exit
fi
curl -s "http://$1/api/data/poster?token=$2"
