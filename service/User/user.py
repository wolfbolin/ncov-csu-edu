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
    sql = "REPLACE `user`(`cookies`, `username`, `nickname`, `phone`, `time`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query=sql, args=[cookies, user_info["username"], user_info["nickname"],
                                    user_info["phone"], Kit.rand_time()])
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


@user_blue.route('/task', methods=["GET"])
def user_task():
    # 检查请求数据
    username = request.args.get("username", "").strip()
    phone = request.args.get("phone", "").strip()

    # 检查并删除任务
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `nickname`, `time`, `sms` FROM `user` WHERE `username`=%s AND `phone`=%s"
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
            "smsOpt": res["sms"],
        }
    })


@user_blue.route('/list')
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


@user_blue.route('/count')
def user_count():
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = """
    SELECT
        `date`,
        `user_num` 
    FROM
        `count` 
    WHERE
        `range` = '23-00' 
    ORDER BY
        `date` DESC 
        LIMIT 30
    """
    cursor.execute(query=sql)
    user_data = cursor.fetchall()
    user_data_key = []
    user_data_val = []
    for it in user_data:
        user_data_key.append(str(it["date"])[5:])
        user_data_val.append(it["user_num"])

    sql = """
    SELECT
        `date`,
        `range`,
        `sign_num` 
    FROM
        `count` 
    WHERE
        `date` >= DATE_SUB(CURDATE(), INTERVAL 7 DAY ) 
        AND `sign_num` > 0
    """
    cursor.execute(query=sql)
    sign_data = cursor.fetchall()
    sign_index = {}
    sign_matrix = []
    for item in sign_data:
        sign_index.setdefault(item["range"], {})
        sign_index[item["range"]][str(item["date"])[5:]] = item["sign_num"]

    sign_date_list = set()
    sign_range_list = set()
    for x, sign_range in enumerate(sign_index.keys()):
        sign_range_list.add(sign_range)
        for y, sign_date in enumerate(sign_index[sign_range].keys()):
            sign_date_list.add(sign_date)
            sign_matrix.append([x, y, sign_index[sign_range][sign_date]])

    return jsonify({
        "status": "success",
        "user_data": [user_data_key[::-1], user_data_val[::-1]],
        "sign_data": [sorted(list(sign_range_list)), sorted(list(sign_date_list)), sign_matrix]
    })
