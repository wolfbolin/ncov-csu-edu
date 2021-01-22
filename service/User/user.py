# coding=utf-8
import json
import Kit
import pymysql
from flask import abort
from flask import jsonify
from flask import request
from User import user_blue
from flask import current_app as app


@user_blue.route('/open', methods=["GET"])
def open_login():
    # 分时关闭服务
    time_now = int(Kit.str_time("%H"))
    if time_now == 0:
        return jsonify({
            "status": "error",
            "message": "流量过载，请凌晨一点后再试"
        })

    # 服务关闭标记
    conn = app.mysql_pool.connection()
    flag = Kit.get_key_val(conn, "shutdown_login")
    if flag != "open":
        return jsonify({
            "status": "error",
            "message": "登录服务临时关闭"
        })

    return jsonify({
        "status": "success",
        "message": "开放登录"
    })


@user_blue.route('/login', methods=["POST"])
def user_login():
    # 分时关闭服务
    time_now = int(Kit.str_time("%H"))
    if time_now == 0:
        return jsonify({
            "status": "error",
            "message": "流量过载，请凌晨一点后再试"
        })

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
    sql = "INSERT `user`(`cookies`, `username`, `nickname`, `phone`, `time`) " \
          "VALUES (%s, %s, %s, %s, rand_time()) ON DUPLICATE KEY UPDATE " \
          "`cookies`=VALUES(`cookies`),`nickname`=VALUES(`nickname`),`phone`=VALUES(`phone`),`online`='Yes'"
    cursor.execute(query=sql, args=[cookies, user_info["username"], user_info["nickname"], user_info["phone"]])
    conn.commit()

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


@user_blue.route('/task', methods=["GET"])
def get_task_info():
    # 检查请求数据
    username = request.args.get("username", "").strip()
    phone = request.args.get("phone", "").strip()

    # 检查并获取任务
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `nickname`, `time`, `rand`, `sms` FROM `user` WHERE `username`=%s AND `phone`=%s AND `online`='Yes'"
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
        }
    })


@user_blue.route('/task', methods=["PUT"])
def update_task_info():
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

    return jsonify({
        "status": "success",
        "message": "任务信息更新成功"
    })


@user_blue.route('/sign', methods=["POST"])
def user_sign():
    # 检查请求数据
    user_info = request.get_data(as_text=True)
    user_info = json.loads(user_info)
    if set(user_info.keys()) != {"username", "phone"}:
        return abort(400)

    # 查询打卡用户信息
    app.logger.info("Sign for vip user {}".format(user_info["username"]))
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `user` WHERE `username`=%s AND `phone`=%s AND `online`='Yes'"
    cursor.execute(sql, args=[user_info["username"], user_info["phone"]])
    user_info = cursor.fetchone()
    risk_area = Kit.get_risk_area(conn)
    app.executor.submit(Kit.user_sign_task, app.config, user_info, risk_area)

    return jsonify({
        "status": "success",
        "message": "Check user: {}".format(user_info["username"])
    })


@user_blue.route('/list')
def user_list():
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
