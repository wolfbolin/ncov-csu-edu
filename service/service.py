# coding=utf-8
import os
import json
import Util
import pymysql
import logging
from flask import abort
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
from Config import get_config
from dbutils.pooled_db import PooledDB

# 获取配置
app_config = get_config()
base_path = os.path.split(os.path.abspath(__file__))[0]

# 初始化应用
app = Flask(__name__)
app.config.from_mapping(app_config)
CORS(app, supports_credentials=True,
     resources={r"/*": {"origins": app_config["BASE"]["web_host"]}})

# 服务日志
file_logger = logging.getLogger('file_log')
file_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(filename='{}/log/run.log'.format(base_path), encoding="utf-8")
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# 初始化连接池
for key in app.config.get('POOL').keys():
    app.config.get('POOL')[key] = int(app.config.get('POOL')[key])
app.config.get('MYSQL')["port"] = int(app.config.get('MYSQL')["port"])
pool_config = app.config.get('POOL')
mysql_config = app.config.get('MYSQL')
app.mysql_pool = PooledDB(creator=pymysql, **mysql_config, **pool_config)


@app.route('/')
@app.route('/api/')
def hello_world():
    app.logger.info('Trigger "Hello,world!"')
    return "Hello, world!"


@app.route('/api/user/login', methods=["POST"])
def user_login():
    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "password", "nickname", "phone", "time"}:
        return abort(400)
    if 8 <= len(user_info["username"]) <= 14 and len(user_info["password"]) != 0 and \
            4 <= len(user_info["nickname"]) <= 16 and len(user_info["phone"]) == 11 and \
            len(user_info["time"]) != 0:
        unix_time = Util.timestamp2unix("2020-01-01 " + user_info["time"] + ":00")
        user_info["time"] = Util.unix2timestamp(unix_time, pattern="%H:%M")
    else:
        return abort(400)
    app.logger.info("User try to login: {}".format(user_info["username"]))

    # 查询并写入数据
    conn = app.mysql_pool.connection()
    # 验证用户账号信息并获取session
    status, data, run_err = Util.user_login(user_info["username"], user_info["password"])
    if status is False:
        Util.write_log(conn, user_info["username"], status, data, run_err)
        return jsonify({
            "status": "error",
            "message": str(data)
        })
    cookies = json.dumps(data.cookies.get_dict())
    Util.write_log(conn, user_info["username"], status, "用户登录成功", run_err)

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
def get_user_list():
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `username`, `nickname`, `phone`, `time` FROM `user`"
    cursor.execute(query=sql)
    result = []
    for item in cursor.fetchall():
        item["username"] = item["username"][:4] + "*" * (len(item["username"]) - 6) + item["username"][-2:]
        item["phone"] = item["phone"][:3] + "*" * 4 + item["phone"][-4:]
        result.append(item)
    return {
        "status": "success",
        "message": "列表读取成功",
        "data": result
    }


@app.route('/api/user/logout', methods=["POST"])
def user_logout():
    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "phone"}:
        return abort(400)
    if 8 <= len(user_info["username"]) <= 14 and len(user_info["phone"]) == 11:
        pass
    else:
        return abort(400)
    app.logger.info("User try to  logout: {}".format(user_info["username"]))

    # 检查并删除任务
    conn = app.mysql_pool.connection()
    cursor = conn.cursor()
    sql = "DELETE FROM `user` WHERE `username`=%s AND `phone`=%s"
    cursor.execute(query=sql, args=[user_info["username"], user_info["phone"]])
    conn.commit()
    rowcount = cursor.rowcount
    if rowcount >= 1:
        return jsonify({
            "status": "success",
            "message": "签到任务添加成功"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "用户不存在或信息错误"
        })


@app.route('/api/check')
@app.route('/api/check/<string:check_time>')
def check_list(check_time=None):
    if check_time is None:
        time_now = Util.str_time("%H:%M")
    else:
        unix_time = Util.timestamp2unix("2020-01-01 " + check_time + ":00")
        time_now = Util.unix2timestamp(unix_time, pattern="%H:%M")
    app.logger.info("Check time point at {}".format(time_now))
    conn = app.mysql_pool.connection()
    # 查询当前时间需要打开的用户
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `user` WHERE `time`=%s"
    cursor.execute(query=sql, args=[time_now])
    user_list = cursor.fetchall()
    for user_info in user_list:
        cookies = json.loads(user_info["cookies"])
        status, data, run_err = Util.user_clock(cookies)
        if user_info["sms"] == "Yes":
            Util.send_sms_message(user_info["nickname"], user_info["phone"], str(data))
        Util.write_log(conn, user_info["username"], status, data, run_err)
    app.logger.info("Check point {} with {} task, Done".format(time_now, len(user_list)))

    return jsonify({
        "status": "success",
        "message": "Check time: {}".format(time_now)
    })


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
