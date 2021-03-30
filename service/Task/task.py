# coding=utf-8
import Kit
import pymysql
from flask import abort
from flask import jsonify
from flask import request
from Task import task_blue
from flask import current_app as app
from User.user_info import user_sign_task


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

    try:
        # 写入定时用户
        sql = "REPLACE INTO `task` SELECT `username`,`time` as `task_time`, '00:00' as `sign_time`, " \
              "'Unknown' as `location`, 'waiting' as `status`, CURDATE() as `date` FROM `user` WHERE `online`='Yes';"
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
    except pymysql.Error:
        app.logger.error("任务分配过程，数据库写入异常")

    return jsonify({
        "status": "success",
        "message": "Assign finish"
    })


@task_blue.route('/sign')
@task_blue.route('/sign/<string:check_time>')
def check_list(check_time=None):
    sms_flag = request.args.get("sms", "Yes")
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
        if sms_flag == "No":
            user_info["sms"] = "No"
        if user_info["online"] != "Yes":
            sql = "UPDATE `task` SET `status`=%s, `sign_time`=%s WHERE `username`=%s AND `date` = CURDATE()"
            cursor.execute(sql, args=["logout", Kit.str_time("%H:%M:%S"), user_info["username"]])
            conn.commit()
            continue
        risk_area = Kit.get_risk_area(conn)
        app.executor.submit(user_sign_task, app.config, user_info, risk_area)
    app.logger.info("Check point {} with {} task".format(time_now, len(user_task_list)))

    return jsonify({
        "status": "success",
        "message": "Check time: {}".format(time_now)
    })
