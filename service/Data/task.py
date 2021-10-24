# coding=utf-8
import Kit
import time
import json
import random
import pymysql
import logging
from flask import abort
from flask import request
from Data import data_blue
from flask import current_app as app
from cmq.queue import Message as CMQ_Message
from cmq.account import Account as CMQ_Account
from cmq.cmq_exception import CMQExceptionBase


@data_blue.route('/balance')
def balance_task():
    # 本地数据校验
    client_ip = request.headers.get("X-Real-IP", "0.0.0.0")
    if client_ip != "127.0.0.1":
        return abort(400, "Reject IP:{}".format(client_ip))

    # 重新分配时间
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "UPDATE `user` SET `time` = rand_time() WHERE `rand` != 'Yes'"
    cursor.execute(sql)
    conn.commit()

    return "Affected rows: {}".format(cursor.rowcount)


@data_blue.route('/poster')
@data_blue.route('/poster/<string:check_time>')
def sign_task_post(check_time=None):
    conn = app.mysql_pool.connection()
    admin_token = request.args.get("token", "")
    verify_token = Kit.get_key_val(conn, "token")
    if admin_token != verify_token:
        return abort(400)

    sms_control = request.args.get("sms", "Yes")
    if check_time is None:
        time_now = Kit.str_time("%H:%M")
    else:
        unix_time = Kit.timestamp2unix("2020-01-01 " + check_time + ":00")
        time_now = Kit.unix2timestamp(unix_time, pattern="%H:%M")
    app.logger.info("Service check time {}".format(time_now))

    # 连接至数据库
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if time_now.endswith(":00"):
        # 读取本时间段内随机时间用户
        sql = "SELECT * FROM `user` WHERE `online`='Yes' AND `rand`='Yes' AND `time` LIKE %s"
        cursor.execute(sql, args=[time_now.split(":")[0] + ":%"])
        user_list = cursor.fetchall()
    else:
        # 读取时间点需要打卡用户
        sql = "SELECT * FROM `user` WHERE `online`='Yes' AND `rand`='No' AND `time`=%s"
        cursor.execute(sql, args=[time_now])
        user_list = cursor.fetchall()

    # 连接至消息队列中间件
    user_config = {
        "host": app.config["CMQ"]["endpoint"],
        "secretId": app.config["CMQ"]["secret_id"],
        "secretKey": app.config["CMQ"]["secret_key"],
        "debug": False,
    }

    # 计算时间延迟并发布任务
    for count in range(3):
        retry = False
        queue_client = CMQ_Account(**user_config)
        queue_client.logger.setLevel(logging.CRITICAL)
        queue_client.cmq_client.logger.setLevel(logging.CRITICAL)
        sign_queue = queue_client.get_queue(app.config["CMQ"]["queue_name"])
        for user_data in user_list:
            # 设置短信发送参数
            if sms_control == "No":
                user_data["sms"] = "No"
            # 设置随机时间参数
            if user_data["rand"] == "Yes":
                if time_now.split(":")[0] == "00":
                    delay = random.randint(600, 3600)
                else:
                    delay = random.randint(0, 3600)
            else:
                delay = 0
            # 设置打卡重试计数
            user_data["trace"] = 0
            # 打包消息（共用消息队列）
            message = CMQ_Message(
                json.dumps(
                    {
                        "type": "task",
                        "data": user_data,
                        "user": user_data["username"]
                    }
                )
            )

            try:
                msg_res = sign_queue.send_message(message, delayTime=delay)
            except CMQExceptionBase as e:
                Kit.write_log(logging.ERROR, "sign_task_post", user_data["username"],
                              "error", "Send to CMQ failed", str(e))
                time.sleep(1)
                retry = True
                break
            Kit.write_log(logging.INFO, "sign_task_post", user_data["username"], "success", "Send sign task to CMQ",
                          "ID:{} Delay:{}".format(msg_res.msgId, delay), to_stream=False)
        if retry:
            continue
        break

    app.logger.info("Post {} task to CMQ".format(len(user_list)))

    return "Post message num: {}".format(len(user_list))
