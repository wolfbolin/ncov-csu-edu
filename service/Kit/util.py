# coding=utf-8
import time
import pymysql
import requests


# Print tools
def _print(message, code=None, tag=None, end=None):
    if tag is None:
        message = '[{}] {}'.format(tag, message)
    if code is not None:
        message = '\033[0;{}m{}\033[0m'.format(code, message)
    print(message, end=end)


def print_red(message, tag="ERROR", end=None):
    _print(message, 31, tag, end)  # 红色


def print_green(message, tag="DONE", end='\n'):
    _print(message, 32, tag, end)  # 绿色


def print_yellow(message, tag="WARNING", end='\n'):
    _print(message, 33, tag, end)  # 黄色


def print_blue(message, tag="BEG", end='\n'):
    _print(message, 34, tag, end)  # 深蓝色


def print_purple(message, tag="MID", end='\n'):
    _print(message, 35, tag, end)  # 紫色


def print_azure(message, tag="END", end='\n'):
    _print(message, 36, tag, end)  # 浅蓝色


def print_white(message, tag="INFO", end='\n'):
    _print(message, 37, tag, end)  # 白色


def print_none(message, tag="DEBUG", end='\n'):
    _print(message, None, tag, end)  # 默认


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
