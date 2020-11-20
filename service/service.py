# coding=utf-8
import os
import json
import Kit
import pymysql
import logging
import requests
import sentry_sdk
from flask import abort
from flask import Flask
from flask import jsonify
from flask import request
from requests import utils
from flask_cors import CORS
from Config import get_config
from dbutils.pooled_db import PooledDB
from concurrent.futures import ThreadPoolExecutor
from sentry_sdk.integrations.flask import FlaskIntegration

# 获取配置
app_config = get_config()
base_path = os.path.split(os.path.abspath(__file__))[0]

# Sentry
sentry_sdk.init(
    dsn=app_config['SERVICE']['dsn'],
    integrations=[FlaskIntegration()],
    environment=app_config["RUN_ENV"]
)

# 初始化应用
app = Flask(__name__)
app.config.from_mapping(app_config)
CORS(app, supports_credentials=True,
     resources={r"/*": {"origins": app_config["BASE"]["web_host"]}})

# 服务日志
file_logger = logging.getLogger('file_log')
file_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(filename='{}/log/run.log'.format(base_path), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:<%(levelname)s> %(message)s'))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# 初始化连接池
for key in app.config.get('POOL').keys():
    app.config.get('POOL')[key] = int(app.config.get('POOL')[key])
app.config.get('MYSQL')["port"] = int(app.config.get('MYSQL')["port"])
pool_config = app.config.get('POOL')
mysql_config = app.config.get('MYSQL')
app.mysql_pool = PooledDB(creator=pymysql, **mysql_config, **pool_config)

# 初始化异步线程与谅解
app.mysql_conn = app.mysql_pool.connection()
app.executor = ThreadPoolExecutor(max_workers=int(app_config["SERVICE"]["workers"]))


@app.route('/')
@app.route('/api/')
def hello_world():
    app.logger.info('Trigger "Hello,world!"')
    return "Hello, world!"


@app.route('/api/user/login', methods=["POST"])
def user_login():
    # 临时关闭服务
    time_now = int(Kit.str_time("%H"))
    if time_now == 0:
        return jsonify({
            "status": "error",
            "message": "流量过载，请凌晨一点后再试"
        })

    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "password", "nickname", "phone", "time"}:
        return abort(400)
    if 6 <= len(user_info["username"]) <= 14 and len(user_info["password"]) != 0 and \
            4 <= len(user_info["nickname"]) <= 16 and len(user_info["phone"]) == 11 and \
            len(user_info["time"]) != 0:
        unix_time = Kit.timestamp2unix("2020-01-01 " + user_info["time"] + ":00")
        user_info["time"] = Kit.unix2timestamp(unix_time, pattern="%H:%M")
        user_info["username"] = user_info["username"].strip()
        user_info["nickname"] = user_info["nickname"].strip()
        user_info["phone"] = user_info["phone"].strip()
    else:
        return abort(400)
    app.logger.info("User try to login: {}".format(user_info["username"]))

    # 查询并写入数据
    conn = app.mysql_pool.connection()
    # 简单反Dos攻击
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM `log` WHERE `time` > DATE_SUB(NOW(),INTERVAL 1 HOUR) " \
          "AND `function` = 'user_login' AND `username` = %s"
    cursor.execute(query=sql, args=[user_info["username"]])
    log_num = int(cursor.fetchone()[0])
    if log_num > 2:
        Kit.write_log(conn, 'user_login', user_info["username"], False, "反复操作被拒绝",
                      "The user operates {} times in an hour".format(log_num))
        return jsonify({
            "status": "error",
            "message": "您在一小时内操作次数过多，已被暂停服务"
        })

    # 验证用户账号信息并获取session
    status, data, run_err = Kit.user_login(user_info["username"], user_info["password"])
    if status is False:
        Kit.write_log(conn, 'user_login', user_info["username"], status, data, run_err)
        return jsonify({
            "status": "error",
            "message": str(data)
        })
    cookies = json.dumps(data.cookies.get_dict())
    Kit.write_log(conn, 'user_login', user_info["username"], status, "用户登录成功", run_err)

    # 登录成功写入session
    cursor = conn.cursor()
    sql = "REPLACE `user`(`cookies`, `username`, `nickname`, `phone`, `time`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query=sql, args=[cookies, user_info["username"], user_info["nickname"],
                                    user_info["phone"], user_info["time"]])
    conn.commit()

    return jsonify({
        "status": "success",
        "message": "签到信息添加成功"
    })


@app.route('/api/user/list')
def user_list():
    # 读取分页信息
    page_now = int(request.args.get("page_now", 1))
    page_size = int(request.args.get("page_size", 50))

    # 读取数据库数据
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT COUNT(*) as num FROM `user`"
    cursor.execute(query=sql)
    item_num = cursor.fetchone()["num"]
    sql = "SELECT `username`, `nickname`, `phone`, `time` FROM `user` LIMIT %s OFFSET %s"
    cursor.execute(query=sql, args=[page_size, page_now - 1])
    result = []
    for item in cursor.fetchall():
        if len(item["username"]) <= 6:
            item["username"] = item["username"][:1] + "*" * (len(item["username"]) - 3) + item["username"][-2:]
        else:
            item["username"] = item["username"][:4] + "*" * (len(item["username"]) - 6) + item["username"][-2:]
        item["phone"] = item["phone"][:3] + "*" * 4 + item["phone"][-4:]
        result.append(item)
    return {
        "status": "success",
        "message": "列表读取成功",
        "data": {
            "user_list": result,
            "item_num": item_num,
            "page_now": page_now,
            "page_size": page_size,
        }
    }


@app.route('/api/user/logout', methods=["POST"])
def user_logout():
    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "phone"}:
        return abort(400)
    if 8 <= len(user_info["username"]) <= 14 and len(user_info["phone"]) == 11:
        user_info["username"] = user_info["username"].strip()
        user_info["phone"] = user_info["phone"].strip()
    else:
        return abort(400)
    app.logger.info("User try to logout: {}".format(user_info["username"]))

    # 检查并删除任务
    conn = app.mysql_pool.connection()
    cursor = conn.cursor()
    sql = "DELETE FROM `user` WHERE `username`=%s AND `phone`=%s"
    cursor.execute(query=sql, args=[user_info["username"], user_info["phone"]])
    conn.commit()
    rowcount = cursor.rowcount
    if rowcount >= 1:
        Kit.write_log(conn, 'user_logout', user_info["username"], True, "用户退出成功", "success")
        return jsonify({
            "status": "success",
            "message": "用户取消任务成功"
        })
    else:
        Kit.write_log(conn, 'user_logout', user_info["username"], False, "用户退出失败", "User does not exist")
        return jsonify({
            "status": "error",
            "message": "用户不存在或信息错误"
        })


@app.route('/api/check')
@app.route('/api/check/<string:check_time>')
def check_list(check_time=None):
    if check_time is None:
        time_now = Kit.str_time("%H:%M")
    else:
        unix_time = Kit.timestamp2unix("2020-01-01 " + check_time + ":00")
        time_now = Kit.unix2timestamp(unix_time, pattern="%H:%M")
    app.logger.info("Check time point at {}".format(time_now))
    conn = app.mysql_pool.connection()
    # 定时重置数据库连接
    if Kit.unix_time() % 300 == 0:
        app.mysql_conn.close()
        app.mysql_conn = conn
    # 查询当前时间需要打开的用户
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `user` WHERE `time`=%s"
    cursor.execute(query=sql, args=[time_now])
    user_task_list = cursor.fetchall()
    # 提交用户打卡任务到进程池
    for user_info in user_task_list:
        app.executor.submit(user_sign_in, app.mysql_conn, user_info, app.config["BASE"]["sms_token"])
    app.logger.info("Check point {} with {} task".format(time_now, len(user_task_list)))

    return jsonify({
        "status": "success",
        "message": "Check time: {}".format(time_now)
    })


def user_sign_in(conn, user_info, sms_token):
    # 初始化连接
    session = requests.Session()
    cookies = json.loads(user_info["cookies"])
    cookies_jar = requests.utils.cookiejar_from_dict(cookies)
    session.cookies = cookies_jar
    # 执行签到
    status, data, run_err = Kit.user_clock(session)
    # 检查更新
    session_cookies = session.cookies.get_dict()
    if session_cookies != cookies and len(session_cookies.keys()) != 0:
        app.logger.info("User {} cookies update".format(user_info["username"]))
        new_cookies = json.dumps(session_cookies)
        cursor = conn.cursor()
        sql = "UPDATE `user` SET `cookies` = %s WHERE `username` = %s"
        cursor.execute(query=sql, args=[new_cookies, user_info["username"]])

    if user_info["sms"] == "Yes":
        Kit.send_sms_message(sms_token, user_info["nickname"], user_info["phone"], str(data))
    Kit.write_log(conn, 'user_check', user_info["username"], status, data, run_err)


@app.errorhandler(400)
def http_forbidden(msg):
    app.logger.warning("{}: <HTTP 400> {}".format(request.url, msg))
    return jsonify({
        "status": "error",
        "message": "请求数据异常，请检查",
    })


@app.errorhandler(500)
def http_forbidden(msg):
    app.logger.warning("{}: <HTTP 400> {}".format(request.url, msg))
    return jsonify({
        "status": "error",
        "message": "服务器状态异常，请联系开发者",
    })


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='127.0.0.1', port=12880, debug=True)
    exit()
