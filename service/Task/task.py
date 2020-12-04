# coding=utf-8
import Kit
import json
import random
import pymysql
import requests
from flask import abort
from flask import jsonify
from flask import request
from Task import task_blue
from requests import utils
from flask import current_app as app


@task_blue.route('/balance')
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


@task_blue.route('/assign')
def assign_task():
    # 本地数据校验
    client_ip = request.headers.get("X-Real-IP", "0.0.0.0")
    if client_ip != "127.0.0.1":
        return abort(400, "Reject IP:{}".format(client_ip))

    app.logger.info("正在分配当日打卡任务")

    # 锁定数据表
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "LOCK TABLES `user` READ, `task` WRITE"
    cursor.execute(sql)
    app.logger.info("锁定数据表完成")

    try:
        # 写入定时用户
        sql = "REPLACE INTO `task` SELECT `username`,`time` as `task_time`, '00:00' as `sign_time`, " \
              "'waiting' as `status`, CURDATE() as `date` FROM `user` WHERE `online`='Yes';"
        cursor.execute(sql)
        app.logger.info("用户任务写入完成")

        # 写入随机时间
        sql = "UPDATE `task` SET `task_time` = CONCAT(LEFT(`task_time`,2), ':', LPAD(FLOOR(1+rand()*59),2,0)) " \
              "WHERE `username` IN (" \
              "SELECT `username` FROM `user` WHERE `online`='Yes' AND `rand`='Yes'" \
              ") AND `date` = CURDATE()"
        cursor.execute(sql)
        app.logger.info("随机时间写入完成")
        conn.commit()
    finally:
        # 释放数据表
        sql = "UNLOCK TABLES"
        cursor.execute(sql)
        app.logger.info("释放数据表完成")

    return jsonify({
        "status": "success",
        "message": "Assign finish"
    })


@task_blue.route('/sign')
@task_blue.route('/sign/<string:check_time>')
def check_list(check_time=None):
    if check_time is None:
        time_now = Kit.str_time("%H:%M")
    else:
        unix_time = Kit.timestamp2unix("2020-01-01 " + check_time + ":00")
        time_now = Kit.unix2timestamp(unix_time, pattern="%H:%M")
    app.logger.info("Check time point at {}".format(time_now))
    # 查询当前时间需要打开的用户
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = """
    SELECT
        `task`.`username` AS `username`,
        `task`.`task_time` AS `task_time`,
        `user`.`nickname` AS `nickname`,
        `user`.`cookies` AS `cookies`,
        `user`.`online` AS `online`,
        `user`.`phone` AS `phone`,
        `user`.`sms` AS `sms`
    FROM
        `task`
        INNER JOIN `user` ON `task`.`username` = `user`.`username`
    WHERE
        `task`.`task_time` = %s 
        AND `task`.`date` = CURDATE()
    """
    cursor.execute(query=sql, args=[time_now + ':00'])
    user_task_list = cursor.fetchall()
    # 提交用户打卡任务到进程池
    for user_info in user_task_list:
        if user_info["online"] != "Yes":
            sql = "UPDATE `task` SET `status`=%s, `sign_time`=%s WHERE `username`=%s AND `date` = CURDATE()"
            cursor.execute(sql, args=["logout", Kit.str_time("%H:%M:%S"), user_info["username"]])
            conn.commit()
            continue
        app.executor.submit(user_sign_in, app.config, user_info, app.config["BASE"]["sms_token"])
    app.logger.info("Check point {} with {} task".format(time_now, len(user_task_list)))

    return jsonify({
        "status": "success",
        "message": "Check time: {}".format(time_now)
    })


def user_sign_in(config, user_info, sms_token):
    # 连接数据库
    try:
        # 连接数据库
        conn = pymysql.connect(**config['MYSQL'])
        cursor = conn.cursor()
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
            Kit.print_blue("User {} cookies update".format(user_info["username"]))
            new_cookies = json.dumps(session_cookies)
            sql = "UPDATE `user` SET `cookies` = %s WHERE `username` = %s"
            cursor.execute(query=sql, args=[new_cookies, user_info["username"]])
            conn.commit()

        if user_info["sms"] == "Yes":
            Kit.send_sms_message(sms_token, user_info["nickname"], user_info["phone"], str(data))

        # 任务完成
        Kit.write_log(conn, 'user_check', user_info["username"], status, data, run_err)
        sql = "UPDATE `task` SET `status`=%s, `sign_time`=%s WHERE `username`=%s AND `date` = CURDATE()"
        cursor.execute(sql, args=["success" if status else "error", Kit.str_time("%H:%M:%S"), user_info["username"]])
        conn.commit()
    except BaseException as e:
        Kit.print_red(e)


@task_blue.route('/count')
def check_count():
    # 本地数据校验
    client_ip = request.headers.get("X-Real-IP", "0.0.0.0")
    if client_ip != "127.0.0.1":
        return abort(400, "Reject IP:{}".format(client_ip))

    # 计算统计时间
    now_hour = Kit.unix_time()
    last_hour = now_hour - 3600
    now_hour = Kit.unix2timestamp(now_hour, "%Y-%m-%d %H:00:00")
    last_hour = Kit.unix2timestamp(last_hour, "%Y-%m-%d %H:00:00")
    print("Check log between {} and {}".format(last_hour, now_hour))

    # 查询历史数据
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `log` WHERE `time` BETWEEN %s AND %s "
    cursor.execute(query=sql, args=[last_hour, now_hour])
    log_data = cursor.fetchall()
    sql = "SELECT COUNT(*) as user_num FROM `user`"
    cursor.execute(query=sql)
    user_num = int(cursor.fetchone()["user_num"])

    # 统计日志信息
    sign_count = 0
    for log in log_data:
        if log["function"] == "user_check" and log["message"] in ["操作成功", "今天已经填报了"]:
            sign_count += 1

    # 写入统计信息
    date = Kit.unix2timestamp(Kit.unix_time())
    time_range = "{}-{}".format(last_hour[11:13], now_hour[11:13])
    sql = "INSERT INTO `count`(`date`, `range`, `user_num`, `sign_num`) VALUES(%s,%s,%s,%s)"
    cursor.execute(query=sql, args=[date, time_range, user_num, sign_count])
    conn.commit()

    return "Done"
