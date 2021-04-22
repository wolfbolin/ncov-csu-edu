#!/bin/bash
cur_time=$(date "+%H:%M")
if [[ "10:00" < ${cur_time} ]];then
    exit
fi
curl https://covid19.csu-edu.cn/api/data/poster
