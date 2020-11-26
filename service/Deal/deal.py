# coding=utf-8
import Kit
import json
import pymysql
import requests
from flask import jsonify
from flask import request
from Deal import deal_blue
from flask import current_app as app

g_item_index = {
    "donation": "友情捐助",
    "random_time": "随机时间",
    "sms_message": "短信通知",
}


@deal_blue.route('/volume')
def deal_volume():
    volume_info = []
    for item in app.config["VOLUME"]:
        volume_info.append({
            "key": item,
            "name": g_item_index[item],
            "volume": int(app.config["VOLUME"][item])
        })
    return {
        "status": "success",
        "data": volume_info
    }
