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
g_query_key = {"username", "phone", "order_str"}
g_order_key = {"username", "phone", "donation", "attach", "item_list"}


@deal_blue.route('/menu')
def deal_volume():
    volume_info = []
    for item in app.config["MENU"]:
        volume_info.append({
            "key": item,
            "name": g_item_index[item],
            "volume": int(app.config["MENU"][item])
        })
    return {
        "status": "success",
        "data": volume_info
    }


@deal_blue.route('/order', methods=["POST"])
def deal_create():
    # 获取订单信息
    deal_info = request.get_json()
    if deal_info is None or set(deal_info.keys()) != g_order_key:
        return {
            "status": "error",
            "message": "交易数据不完整",
        }
    if not isinstance(deal_info["item_list"], list):
        return {
            "status": "error",
            "message": "交易数据不完整",
        }

    # 记录交易日志
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "INSERT `order_log`(phone, username, function, content) VALUES(%s,%s,%s,%s)"
    cursor.execute(sql, args=[deal_info["phone"], deal_info["username"], "recv_deal", json.dumps(deal_info)])
    conn.commit()

    # 计算交易金额
    volume = 0
    order_item = []
    for item in deal_info["item_list"]:
        if item not in app.config["MENU"]:
            continue
        order_item.append(item)
        if item == "donation":
            volume += int(deal_info["donation"])
        else:
            volume += int(app.config["MENU"][item])

    # 检查交易用户
    sql = "SELECT * FROM `user` WHERE `username`=%s AND `phone`=%s"
    cursor.execute(sql, args=[deal_info["username"], deal_info["phone"]])
    user_info = cursor.fetchone()
    if user_info is None:
        return jsonify({
            "status": "error",
            "message": "用户不存在，请先登录",
        })

    # 创建用户订单
    url = "https://core.wolfbolin.com/payment/alipay"
    data = {
        "app": "csu_sign",
        "subject": "友情赞助",
        "volume": str(volume)
    }
    if app.config["RUN_ENV"] == "develop":
        data["app"] = "test"

    res = requests.post(url, json=data)
    if res.status_code != 200:
        return jsonify({
            "status": "error",
            "message": "创建订单失败",
        })
    res = json.loads(res.text)
    if res["code"] != 92000:
        return jsonify({
            "status": "error",
            "message": res["status"],
        })
    order_info = res["data"]

    # 记录订单信息
    sql = "INSERT `order`(`order`, `phone`, `username`, `item_list`, `volume`, `status`, `attach`) " \
          "VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql, args=[order_info["order_str"], deal_info["phone"], deal_info["username"],
                              json.dumps(order_item), volume, "CREATED", deal_info["attach"]])
    conn.commit()

    return {
        "status": "success",
        "data": order_info
    }


@deal_blue.route('/order', methods=["GET"])
def trade_query():
    # 获取订单信息
    deal_info = dict(request.args)
    if deal_info is None or set(deal_info.keys()) != g_query_key:
        return {
            "status": "error",
            "message": "订单数据不完整",
        }

    # 读取订单信息
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `order` WHERE `username`=%s AND `phone`=%s AND `order`=%s"
    cursor.execute(sql, args=[deal_info["username"], deal_info["phone"], deal_info["order_str"]])
    order_record = cursor.fetchone()
    if order_record is None:
        return jsonify({
            "status": "error",
            "message": "订单不存在，请查证",
        })
    if order_record["status"] in ("SUCCESS", "FINISH", "CLOSE"):
        return jsonify({
            "status": "success",
            "order_status": order_record["status"]
        })

    order_data = check_order(deal_info["order_str"])

    # 更新数据库状态
    sql = "UPDATE `order` SET `status`=%s WHERE `order`=%s"
    cursor.execute(sql, args=[order_data["order_status"], deal_info["order_str"]])
    conn.commit()

    # 调整用户功能
    if order_data["order_status"] == "SUCCESS":
        # 调整用户功能
        item_list = json.loads(order_record["item_list"])
        for item in item_list:
            if item == "donation":
                sql = "UPDATE `user` SET `donor`='Yes' WHERE `username`=%s"
                cursor.execute(sql, args=[order_record["username"]])
            if item == "message":
                sql = "UPDATE `user` SET `sms`='Yes' WHERE `username`=%s"
                cursor.execute(sql, args=[order_record["username"]])
            if item == "random":
                sql = "UPDATE `user` SET `rand`='Yes' WHERE `username`=%s"
                cursor.execute(sql, args=[order_record["username"]])
            conn.commit()

    return jsonify({
        "status": "success",
        "order_status": order_data["order_status"]
    })


@deal_blue.route('/order/check')
def check_user_order():
    # 获取请求信息
    user_info = dict(request.args)
    if user_info is None or set(user_info.keys()) != {"username", "phone"}:
        return {
            "status": "error",
            "message": "请求不完整",
        }

    # 获取订单信息
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `order` WHERE `username`=%s AND `phone`=%s"
    cursor.execute(sql, args=[user_info["username"], user_info["phone"]])
    order_list = cursor.fetchall()

    # 逐项检查订单
    for order in order_list:
        if order["status"] == "CREATE":
            order_data = check_order(order["order"])
            order["status"] = order_data["order_status"]

            # 更新本地缓存
            sql = "UPDATE `order` SET `status`=%s WHERE `order`=%s"
            cursor.execute(sql, args=[order_data["order_status"], order["order"]])
            conn.commit()

        if order["status"] == "SUCCESS":
            # 调整用户功能
            item_list = json.loads(order["item_list"])
            for item in item_list:
                if item == "donation":
                    sql = "UPDATE `user` SET `donor`='Yes' WHERE `username`=%s"
                    cursor.execute(sql, args=[order["username"]])
                if item == "message":
                    sql = "UPDATE `user` SET `sms`='Yes' WHERE `username`=%s"
                    cursor.execute(sql, args=[order["username"]])
                if item == "random":
                    sql = "UPDATE `user` SET `rand`='Yes' WHERE `username`=%s"
                    cursor.execute(sql, args=[order["username"]])
                conn.commit()

    info_list = []
    for order in order_list:
        info_list.append({
            "id": order["order"],
            "item": json.loads(order["item_list"]),
            "status": order["status"],
            "time": Kit.unix2timestamp(Kit.datetime2unix(order["updated_time"])),
            "created": Kit.datetime2unix(order["created_time"]),
            "updated": Kit.datetime2unix(order["updated_time"]),
        })

    return jsonify({
        "status": "success",
        "data": info_list
    })


def check_order(order_str):
    # 查询订单状态
    url = "https://core.wolfbolin.com/payment/alipay"  # Change for pro
    params = {
        "app": "csu_sign",
        "order_str": order_str
    }
    if app.config["RUN_ENV"] == "develop":
        params["app"] = "test"

    res = requests.get(url, params=params)
    if res.status_code != 200:
        return {
            "order_status": "Unknown",
        }
    res = json.loads(res.text)
    return res["data"]
