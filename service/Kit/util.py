# coding=utf-8
import time
import pymysql
import requests


def unix_time(unit=1):
    return int(time.time() * unit)


def str_time(pattern='%Y-%m-%d %H:%M:%S', timing=None):
    if timing is None:
        timing = time.time()
    return time.strftime(pattern, time.localtime(timing))


def timestamp2unix(time_string, pattern='%Y-%m-%d %H:%M:%S'):
    time_array = time.strptime(time_string, pattern)
    return int(time.mktime(time_array))


def unix2timestamp(u_time, pattern='%Y-%m-%d %H:%M:%S'):
    return time.strftime(pattern, time.localtime(u_time))


def send_sms_message(sms_token, user_name, user_phone, result):
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
        "token": sms_token
    }
    res = requests.post(url=url, json=data, params=params)
    print("Send SMS Result: {}".format(res.text.strip()))


def write_log(conn, function, username, status, message, run_err):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "INSERT `log`(`function`, `username`, `result`, `message`, `error`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query=sql, args=[function, username, status, message, run_err])
    conn.commit()
