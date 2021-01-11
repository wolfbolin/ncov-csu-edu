# coding=utf-8
import Kit
import json
import pymysql
from flask import abort
from flask import request
from flask import jsonify
from Task import task_blue
from flask import current_app as app


@task_blue.route('/count/log', methods=["POST"])
def check_log_data():
    # 本地数据校验
    client_ip = request.headers.get("X-Real-IP", "0.0.0.0")
    if client_ip != "127.0.0.1":
        return abort(400, "Reject IP:{}".format(client_ip))

    # 计算统计时间
    now_hour = Kit.unix_time()
    last_hour = now_hour - 3600
    now_hour = Kit.unix2timestamp(now_hour, "%Y-%m-%d %H:00:00")
    last_hour = Kit.unix2timestamp(last_hour, "%Y-%m-%d %H:00:00")
    app.logger.info("Check log between {} and {}".format(last_hour, now_hour))

    # 查询历史数据
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `log` WHERE `time` BETWEEN %s AND %s "
    cursor.execute(query=sql, args=[last_hour, now_hour])
    log_data = cursor.fetchall()
    sql = "SELECT COUNT(*) as user_num FROM `user` WHERE `online`='Yes'"
    cursor.execute(query=sql)
    user_num = int(cursor.fetchone()["user_num"])

    # 统计日志信息
    sign_num_count = 0
    for log in log_data:
        if log["function"] == "user_check" and log["message"] in ["操作成功", "今天已经填报了"]:
            sign_num_count += 1

    # 写入统计信息
    date_now = Kit.unix2timestamp(Kit.unix_time())
    range_now = "{}-{}".format(last_hour[11:13], now_hour[11:13])
    sql = "INSERT INTO `count`(`date`, `range`, `user_num`, `sign_num`, `location_tree`) VALUES(%s,%s,%s,%s,'')"
    cursor.execute(query=sql, args=[date_now, range_now, user_num, sign_num_count])
    conn.commit()

    return "Done"


@task_blue.route('/count/task', methods=["POST"])
def check_task_data():
    # 本地数据校验
    client_ip = request.headers.get("X-Real-IP", "0.0.0.0")
    if client_ip != "127.0.0.1":
        return abort(400, "Reject IP:{}".format(client_ip))

    # 确定统计时间
    # 每次只统计上一分钟所在天的数据
    range_now = "00-24"
    time_hour = Kit.unix_time() - 120
    date_now = Kit.str_time("%Y-%m-%d", time_hour)
    app.logger.info("Check task between '00' and 'now'")

    # 查询历史数据
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `task` WHERE `date`=%s"
    cursor.execute(query=sql, args=[date_now])
    task_data = cursor.fetchall()

    # 统计位置信息
    location_tree = {"name": "*", "child": {}}
    for region in task_data:
        if region["location"] == "Unknown":
            continue

        location = json.loads(region["location"])
        country_child = set_location_count(location, location_tree["child"], "country")
        province_child = set_location_count(location, country_child, "province")
        city_child = set_location_count(location, province_child, "city")
        set_location_count(location, city_child, "district")
    sql = "INSERT INTO `count`(`date`,`range`,`location_tree`) VALUES (%s,%s,%s) " \
          "ON DUPLICATE KEY UPDATE `location_tree`=VALUES(`location_tree`)"
    cursor.execute(sql, args=[date_now, range_now, json.dumps(location_tree, ensure_ascii=False)])
    conn.commit()

    return "Done"


def set_location_count(location, node, key):
    node.setdefault(location[key], {"name": location[key], "count": 0, "child": {}})
    node[location[key]]["count"] += 1
    return node[location[key]]["child"]


@task_blue.route('/count/location')
def get_location():
    # 获取数据日期
    date = request.args.get("date", Kit.str_time("%Y-%m-%d"))

    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `count` WHERE `date`=%s AND `range`='00-24'"
    cursor.execute(sql, args=[date])
    data = cursor.fetchone()
    if data is None:
        return jsonify({
            "status": "success",
            "update_date": date,
            "data": {"中国": {"child": {}}}
        })

    return jsonify({
        "status": "success",
        "update_date": date,
        "data": json.loads(data["location_tree"])
    })


@task_blue.route('/count/user')
def get_user_count():
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

    return jsonify({
        "status": "success",
        "user_data": [user_data_key[::-1], user_data_val[::-1]]
    })


@task_blue.route('/count/sign')
def get_sign_count():
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
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
        "sign_data": [sorted(list(sign_range_list)), sorted(list(sign_date_list)), sign_matrix]
    })
