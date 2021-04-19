#!/bin/bash
cur_time=$(date "+%H:%M")
if [[ "11:59" < ${cur_time} ]];then
    exit
fi
curl https://covid19.csu-edu.cn/api/data/sign
