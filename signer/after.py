# coding=utf-8
import Kit
import json
import requests


def handle_sign_result(config, conn, flow_data, elk_logger):
    cursor = conn.cursor()
    user_info = flow_data["user_info"]
    log_data = {
        "function": "handle_sign_result",
        "username": user_info["username"],
        "result": "success",
        "status": [flow_data["result"]],
        "message": "Handle flow data after sign"
    }

    if flow_data["result"] == "lost_status":
        cursor = conn.cursor()
        sql = "UPDATE `user` SET `online`='Lost' WHERE `username`=%s"
        cursor.execute(sql, args=[user_info["username"]])
        log_data["status"].append("user_logout")
    elif flow_data["result"] in ["success", "stop_sign", "risk_area"]:
        # 更新用户 Cookie
        if user_info["cookies_update"] == "Yes":
            new_cookies = user_info["cookies_data"]
            sql = "UPDATE `user` SET `cookies` = %s WHERE `username` = %s"
            cursor.execute(query=sql, args=[new_cookies, user_info["username"]])
            log_data["status"].append("cookies_update")

        # 向用户发送短信通知
        if user_info["sms"] == "Yes":
            send_sms_message(config, user_info, flow_data["result"], flow_data["status"])
            log_data["status"].append("send_message")

        # 记录用户打卡位置
        sql = "INSERT `location`(date,user,location) VALUES(%s,%s,%s)"
        cursor.execute(sql, args=[Kit.str_time("%Y-%m-%d"), user_info["username"], status])
        log_data["status"].append("insert_location")
    else:
        log_data["status"].append("unknown_flow")

    extra = json.loads(config["ELK"]["extra"])
    elk_logger.info(json.dumps(log_data), extra=extra)


def send_sms_message(config, user_info, result, location):
    sms_token = config["BASE"]["sms_token"]
    # 位置信息
    if result in ["success", "stop_sign", "risk_area"]:
        location = json.loads(location)
        location = "{}-{}".format(location["province"], location["city"])
    else:
        location = "未知"

    url = "https://core.wolfbolin.com/message/sms/send/%s" % user_info["phone"]
    data = {
        "phone": user_info["phone"],
        "template": 1076591,
        "params": [
            user_info["nickname"],
            Kit.str_time("%H:%M"),
            str(result[2]),
            location
        ]
    }
    if user_info["vip"] == "Yes":
        data["template"] = 1076596
    params = {
        "token": sms_token
    }
    requests.post(url=url, json=data, params=params)
    Kit.print_purple("{} Send SMS to {}".format(Kit.str_time(), user_info["phone"]))
