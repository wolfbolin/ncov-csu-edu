# coding=utf-8
import json
import time
import base64
import string
import random
import requests
import datetime
from flask import jsonify
from functools import wraps
from Cryptodome.Cipher import AES
from flask import current_app as app


def check_service_time(func):
    @wraps(func)
    def check_hostname(*args, **kwargs):
        # 分时关闭服务
        zero_time = timestamp2datetime(str_time("%Y-%m-%d"), "%Y-%m-%d")
        time_now_ = datetime.datetime.now()
        dt_time = time_now_ - zero_time
        time_now_ = dt_time.seconds

        if time_now_ < 3600 * 7 or time_now_ > 3600 * 23 + 60 * 55:
            return jsonify({
                "status": "error",
                "message": "服务临时关闭，流量保护<23:55 - 8:00>"
            })
        return func(*args, **kwargs)

    return check_hostname


# Encrypt tools
def aes_encrypt(text, password):
    # 初始化参数
    encrypt_mode = AES.MODE_ECB
    # 填充文本与秘钥
    fill_block_size = AES.block_size - len(text) % AES.block_size
    encrypt_text = text + fill_block_size * chr(fill_block_size)
    # 进行加密操作
    encrypt_lock = AES.new(password.encode("utf-8"), encrypt_mode)
    ciphered_text = encrypt_lock.encrypt(encrypt_text.encode("utf-8"))
    return base64.b64encode(ciphered_text).decode("utf-8")


def aes_decrypt(data, password):
    # 初始化参数
    encrypt_mode = AES.MODE_ECB
    # 解码文本数据
    encrypt_data = base64.b64decode(data.encode("utf-8"))
    # 进行加密操作
    encrypt_lock = AES.new(password.encode("utf-8"), encrypt_mode)
    ciphered_text = encrypt_lock.decrypt(encrypt_data)
    # 移除填充文本
    unpad = lambda s: s[0:-ord(s[-1])]
    return unpad(ciphered_text.decode("utf-8"))


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


def time_now():
    return datetime.datetime.now()


def unix_time(unit=1):
    return int(time.time() * unit)


def str_time(pattern='%Y-%m-%d %H:%M:%S', timing=None):
    if timing is None:
        timing = time.time()
    return time.strftime(pattern, time.localtime(timing))


def timestamp2datetime(time_string, pattern='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(time_string, pattern)


def timestamp2unix(time_string, pattern='%Y-%m-%d %H:%M:%S'):
    time_array = time.strptime(time_string, pattern)
    return int(time.mktime(time_array))


def unix2timestamp(u_time, pattern='%Y-%m-%d %H:%M:%S'):
    return time.strftime(pattern, time.localtime(u_time))


def datetime2unix(timing):
    return int(time.mktime(timing.timetuple()))


def rand_time(rand_hour=None):
    if rand_hour is None:
        rand_hour = random.randint(0, 6)
    rand_min = random.randint(1, 59)
    return "{:02d}:{:02d}".format(rand_hour, rand_min)


def random_string(length, chars=string.digits + string.ascii_letters):
    return ''.join(random.choice(chars) for _ in range(length))


def write_log(level, function, username, result, status, message, to_stream=True):
    extra = json.loads(app.config["ELK"]["extra"])
    log_data = {
        "function": function,
        "username": username,
        "result": result,
        "status": status,
        "message": message
    }
    app.elk_logger.log(level, json.dumps(log_data), extra=extra)
    if to_stream:
        app.logger.log(level, json.dumps(log_data, ensure_ascii=False))
