# coding=utf-8
import time
import pymysql
import requests
from flask import current_app as app


def str_time(pattern='%Y-%m-%d %H:%M:%S', timing=None):
    if timing is None:
        timing = time.time()
    return time.strftime(pattern, time.localtime(timing))


def timestamp2unix(time_string, pattern='%Y-%m-%d %H:%M:%S'):
    time_array = time.strptime(time_string, pattern)
    return int(time.mktime(time_array))


def unix2timestamp(u_time, pattern='%Y-%m-%d %H:%M:%S'):
    return time.strftime(pattern, time.localtime(u_time))


def send_sms_message(user_name, user_phone, result):
    url = "http://core.wolfbolin.com/message/sms/send/%s" % user_phone
    data = {
        "phone": user_phone,
        "template": 634328,
        "params": [
            user_name,
            "COVID-19签到",
            str_time("%H:%M"),
            str(result)
        ]
    }
    params = {
        "token": app.config["BASE"]["sms_token"]
    }
    res = requests.post(url=url, json=data, params=params)
    app.logger.info("SMS Result:", res.text.strip())


def write_log(conn, username, status, message, run_err):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "INSERT `log`(`username`, `result`, `message`, `error`) " \
          "VALUES (%s, %s, %s, %s)"
    cursor.execute(query=sql, args=[username, status, message, run_err])
    conn.commit()
