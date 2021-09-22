# coding=utf-8
import os
import Kit
import json
import base64
import logging
import pymysql
import requests
from flask import abort
from flask import jsonify
from flask import request
from User import user_blue
from requests import utils
from flask import current_app as app
from User.user_info import user_sso_login
from User.user_info import base_info_update
from User.user_info import user_sso_login_step2


@user_blue.route('/login', methods=["POST"])
@Kit.check_service_time
def user_login():
    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "password", "nickname", "phone"}:
        return abort(400)
    if 6 <= len(user_info["username"]) <= 14 and len(user_info["password"]) != 0 and \
            4 <= len(user_info["nickname"]) <= 16 and len(user_info["phone"]) == 11:
        user_info["username"] = user_info["username"].strip()
        user_info["nickname"] = user_info["nickname"].strip()
        user_info["phone"] = user_info["phone"].strip()
    else:
        return abort(400)
    app.logger.info("User try to login: {}".format(user_info["username"]))

    # 查询并写入数据
    conn = app.mysql_pool.connection()
    flag = Kit.get_key_val(conn, "shutdown_login")
    if flag != "open":
        return jsonify({
            "status": "error",
            "message": "登录服务临时关闭"
        })

    # 简单反Dos攻击
    cursor = conn.cursor()
    sql = "INSERT `event`(`user`,`event`) VALUES(%s,'user_login')"
    cursor.execute(query=sql, args=[user_info["username"]])
    conn.commit()

    sql = "SELECT COUNT(*) FROM `event` WHERE " \
          "`user` = %s AND `event` = 'user_login' AND " \
          "`time` > DATE_SUB(NOW(),INTERVAL 1 HOUR)"
    cursor.execute(query=sql, args=[user_info["username"]])
    log_num = int(cursor.fetchone()[0])
    if log_num > 5:
        Kit.write_log(logging.WARNING, 'user_login', user_info["username"], "warning", "Login failed", "反复操作被拒绝")
        return jsonify({
            "status": "error",
            "message": "您在一小时内操作次数过多，已被暂停服务"
        })
    sql = "DELETE FROM `event` WHERE `time` < DATE_SUB(NOW(),INTERVAL 2 HOUR)"
    cursor.execute(query=sql)

    # 验证用户账号信息并获取session
    status, data, message = user_sso_login(user_info["username"], user_info["password"])
    if status == "Failed":
        Kit.write_log(logging.WARNING, 'user_login', user_info["username"], "warning", str(data), str(message))
        return jsonify({
            "status": "error",
            "message": str(message)
        })
    elif status == "Captcha":
        login_session = {
            "username": user_info["username"],
            "auth_url": data[0],
            "cookies": json.dumps(data[1].cookies.get_dict()),
            "salt": data[2],
            "exec_": data[3],
            "image_name": data[4],
            "unix_time": Kit.unix_time()
        }
        return jsonify({
            "status": "waiting",
            "message": str(message),
            "login_data": Kit.aes_encrypt(json.dumps(login_session), app.config["BASE"]["aes_key"]),
            "captcha": base64.b64encode(data[5]).decode("utf-8"),
        })

    # 写入登录日志
    Kit.write_log(logging.INFO, 'user_login', user_info["username"], "success", "Login with password", message)

    return user_login_check(conn, user_info, data)


@user_blue.route('/login/captcha', methods=["POST"])
@Kit.check_service_time
def user_login_step2():
    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "password", "nickname", "phone", "login_data"}:
        return abort(400)
    if 6 <= len(user_info["username"]) <= 14 and len(user_info["password"]) != 0 and \
            4 <= len(user_info["nickname"]) <= 16 and len(user_info["phone"]) == 11:
        user_info["username"] = user_info["username"].strip()
        user_info["nickname"] = user_info["nickname"].strip()
        user_info["phone"] = user_info["phone"].strip()
    else:
        return abort(400)

    # 检查加密传输信息
    login_data = Kit.aes_decrypt(user_info["login_data"]["session"], app.config["BASE"]["aes_key"])
    login_data = json.loads(login_data)
    if login_data["username"] != user_info["username"]:
        return jsonify({
            "status": "error",
            "message": "无法确认您的身份"
        })
    if Kit.unix_time() - int(login_data["unix_time"]) > 120:
        return jsonify({
            "status": "error",
            "message": "验证码已过期失效"
        })

    # 尝试记录验证码
    image_path = "{}/captcha/{}.jpg".format(app.config["BASE"]["abspath"], login_data["image_name"])
    new_name = "{}-{}".format(user_info["login_data"]["captcha"], login_data["image_name"].split("-")[0])
    captcha_path = "{}/captcha/{}.jpg".format(app.config["BASE"]["abspath"], new_name)
    os.rename(image_path, captcha_path)

    # 尝试还原登录现场
    session = requests.Session()
    session.headers.update({"Accept-Language": "zh-CN,zh;q=0.9"})
    cookies = json.loads(login_data["cookies"])
    cookies_jar = requests.utils.cookiejar_from_dict(cookies)
    session.cookies = cookies_jar
    app.logger.info("User try to login(captcha): {}".format(user_info["username"]))

    # 尝试输入验证码登录
    login_data["captcha"] = user_info["login_data"]["captcha"]
    status, data, message = user_sso_login_step2(login_data["auth_url"], session,
                                                 user_info["username"], user_info["password"], login_data)
    if status == "Failed":
        Kit.write_log(logging.WARNING, 'user_login', user_info["username"], "warning", str(data), str(message))
        return jsonify({
            "status": "error",
            "message": str(message)
        })

    # 写入登录日志
    Kit.write_log(logging.INFO, 'user_login', user_info["username"], "success", "Login with captcha", message)

    conn = app.mysql_pool.connection()
    return user_login_check(conn, user_info, data)


def user_login_check(conn, user_info, session):
    cookies = json.dumps(session.cookies.get_dict())
    # 登录成功写入session
    cursor = conn.cursor()
    sql = "INSERT `user`(`cookies`, `username`, `nickname`, `phone`, `time`) " \
          "VALUES (%s, %s, %s, %s, rand_time()) ON DUPLICATE KEY UPDATE " \
          "`cookies`=VALUES(`cookies`),`nickname`=VALUES(`nickname`),`phone`=VALUES(`phone`),`online`='Yes'"
    cursor.execute(query=sql, args=[cookies, user_info["username"], user_info["nickname"], user_info["phone"]])
    conn.commit()

    # 检查用户登录态与基本信息
    base_info_update(conn, user_info["username"], cookies)

    return jsonify({
        "status": "success",
        "message": "签到信息添加成功"
    })


@user_blue.route('/logout', methods=["POST"])
def user_logout():
    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "phone"}:
        return abort(400)
    if 6 <= len(user_info["username"]) <= 14 and len(user_info["phone"]) == 11:
        user_info["username"] = user_info["username"].strip()
        user_info["phone"] = user_info["phone"].strip()
    else:
        return abort(400)
    app.logger.info("User try to logout: {}".format(user_info["username"]))

    # 检查并删除任务
    conn = app.mysql_pool.connection()
    cursor = conn.cursor()
    sql = "UPDATE `user` SET `online`='No',`cookies`='' WHERE `username`=%s AND `phone`=%s AND `online`='Yes'"
    cursor.execute(query=sql, args=[user_info["username"], user_info["phone"]])
    conn.commit()
    rowcount = cursor.rowcount
    if rowcount >= 1:
        Kit.write_log(logging.INFO, 'user_logout', user_info["username"], "success", "Logout success", "用户登出打卡服务成功")
        return jsonify({
            "status": "success",
            "message": "用户取消任务成功"
        })
    else:
        Kit.write_log(logging.INFO, 'user_logout', user_info["username"], "warning", "Login failed", "用户不存在或信息错误")
        return jsonify({
            "status": "error",
            "message": "用户不存在或信息错误"
        })


@user_blue.route('/task', methods=["GET"])
def get_task_info():
    # 检查请求数据
    username = request.args.get("username", "").strip()
    phone = request.args.get("phone", "").strip()

    # 检查并获取任务
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `nickname`, `online`, `time`, `rand`, `sms` FROM `user` WHERE `username`=%s AND `phone`=%s " \
          "AND (`online`='Yes' OR `online`='Lost')"
    cursor.execute(sql, args=[username, phone])
    res = cursor.fetchone()
    if res is None:
        return jsonify({
            "status": "error",
            "message": "用户不存在或信息错误"
        })

    return jsonify({
        "status": "success",
        "data": {
            "nickname": res["nickname"],
            "taskTime": res["time"],
            "randOpt": res["rand"],
            "smsOpt": res["sms"],
            "status": res["online"],
        }
    })


@user_blue.route('/task', methods=["PUT"])
def update_user_info():
    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "phone", "time"}:
        return abort(400)

    task_time = int(user_info["time"])
    if task_time > 9 or task_time < 0:
        return jsonify({
            "status": "error",
            "message": "时间范围溢出"
        })
    task_time = "{:02d}:00".format(task_time)

    # 检查并更新任务
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "UPDATE `user` SET `time`=%s WHERE `username`=%s AND `phone`=%s AND `online`='Yes' AND `rand`='Yes'"
    cursor.execute(sql, args=[task_time, user_info["username"], user_info["phone"]])
    if cursor.rowcount == 0:
        return jsonify({
            "status": "error",
            "message": "用户信息错误或没有变化"
        })
    conn.commit()

    Kit.write_log(logging.INFO, 'update_user_info', user_info["username"], "success", "Set time success", "任务信息更新成功")
    return jsonify({
        "status": "success",
        "message": "任务信息更新成功"
    })


@user_blue.route('/list')
def user_page_list():
    # 读取分页信息
    page_now = int(request.args.get("page_now", 1))
    page_size = int(request.args.get("page_size", 50))

    # 读取数据库数据
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT COUNT(*) as num FROM `user` WHERE `online`='Yes'"
    cursor.execute(query=sql)
    item_num = cursor.fetchone()["num"]
    sql = "SELECT `username`, `nickname`, `phone`, `time` FROM `user` WHERE `online`='Yes' LIMIT %s OFFSET %s"
    cursor.execute(query=sql, args=[page_size, (page_now - 1) * page_size])
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


@user_blue.route('/donor')
def donor_user():
    conn = app.mysql_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT `nickname` FROM `user` WHERE `donor`='Yes'"
    cursor.execute(sql)
    donor_list = cursor.fetchall()
    donor_list = [it[0] for it in donor_list]
    return jsonify({
        "status": "success",
        "data": donor_list
    })
