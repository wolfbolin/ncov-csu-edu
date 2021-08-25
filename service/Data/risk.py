# coding=utf-8
import logging

import Kit
import json
import pymysql
import requests
from flask import jsonify
from flask import request
from Data import data_blue
from flask import current_app as app


@data_blue.route('/risk', methods=["GET"])
def fetch_risk():
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `region_risk`"
    cursor.execute(sql)

    return jsonify({
        "status": "success",
        "risk_list": cursor.fetchall(),
        "update_time": Kit.get_key_val(conn, "risk_update_time")
    })


@data_blue.route('/risk', methods=["POST"])
def risk_update():
    # 验证消息来源
    risk_data = request.get_json()
    if risk_data["token"] != app.config["BASE"]["risk_token"]:
        return jsonify({
            "status": "error",
            "message": "认证失败"
        })

    # 更新风险信息
    conn = app.mysql_pool.connection()
    cursor = conn.cursor()
    sql = "DELETE FROM `region_risk` WHERE `level`!='有风险'"
    cursor.execute(sql)

    sql = "REPLACE `region_risk`(`province`,`city`,`block`,`level`) VALUES (%s,%s,%s,%s)"

    high_region_list = []
    for item in risk_data["high_risk"]:
        high_region_list.append("{}-{}-{}".format(item[0], item[1], item[2]))
        cursor.execute(sql, args=[item[0], item[1], item[2], "高风险"])
    high_region_list.sort()

    medium_region_list = []
    for item in risk_data["medium_risk"]:
        medium_region_list.append("{}-{}-{}".format(item[0], item[1], item[2]))
        cursor.execute(sql, args=[item[0], item[1], item[2], "中风险"])
    medium_region_list.sort()

    sql = "UPDATE `kvdb` SET `val`=%s WHERE `key`='risk_update_time'"
    cursor.execute(sql, args=[risk_data["update_time"]])
    conn.commit()

    Kit.write_log(logging.INFO, "risk_update", "system", "success", "Risk area update",
                  "High num: {}. Medium num: {}".format(len(high_region_list), len(medium_region_list)))

    # 发送数据更新提示
    msg_text = "**高风险地区**\n\n"
    msg_text += "\n\n".join(high_region_list)
    msg_text += "\n\n---\n\n"
    msg_text += "**中风险地区**\n\n"
    msg_text += "\n\n".join(medium_region_list)
    msg_text += "\n\n---\n\n"
    msg_text += "更新日期：{}\n\n".format(risk_data["update_time"])
    msg_data = {
        "title": "疫情风险地区更新",
        "source": "CSU-Sign",
        "text": msg_text
    }

    if app.config["RUN_ENV"] == "develop":
        msg_data["user"] = "wolfbolin"
        requests.post("https://core.wolfbolin.com/message/sugar/text", json=msg_data)
    else:
        msg_listener = Kit.get_key_val(conn, "risk_data_listener")
        msg_listener = json.loads(msg_listener)
        for (user, token) in msg_listener.items():
            Kit.write_log(logging.INFO, "risk_update", user, "success", "Send risk message", "Send to {}".format(user))
            msg_data["user"] = user
            params = {"token": token}
            requests.post("https://core.wolfbolin.com/message/sugar/text", json=msg_data, params=params)

    return jsonify({"status": "success"})
