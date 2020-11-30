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
    url = "http://core.wolfbolin.com/payment/alipay"
    data = {
        "app": "csu_sign",
        "subject": "健康打卡服务费",
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

    # 查询订单状态
    url = "http://core.wolfbolin.com/payment/alipay"  # Change for pro
    params = {
        "app": "csu_sign",
        "order_str": deal_info["order_str"]
    }
    if app.config["RUN_ENV"] == "develop":
        params["app"] = "test"

    res = requests.get(url, params=params)
    if res.status_code != 200:
        return jsonify({
            "status": "error",
            "message": "订单状态查询失败",
        })
    res = json.loads(res.text)

    # 更新数据库状态
    sql = "UPDATE `order` SET `status`=%s WHERE `order`=%s"
    cursor.execute(sql, args=[res["data"]["order_status"], deal_info["order_str"]])
    conn.commit()

    return jsonify({
        "status": "success",
        "order_status": res["data"]["order_status"]
    })
