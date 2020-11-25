# coding=utf-8
import Kit
import pymysql
from Config import get_config


def main():
    app_config = get_config()
    mysql_config = app_config['MYSQL']
    mysql_config["port"] = int(mysql_config["port"])
    print(mysql_config)
    conn = pymysql.connect(**mysql_config)

    time_clock = 1601571610
    username_set = set()
    while time_clock < Kit.unix_time():
        username_set = check_count(conn, time_clock, username_set)
        time_clock += 3600


def check_count(conn, time_now, username_set):
    # 计算统计时间
    now_hour = int(time_now)
    last_hour = now_hour - 3600
    now_hour = Kit.unix2timestamp(now_hour, "%Y-%m-%d %H:00:00")
    last_hour = Kit.unix2timestamp(last_hour, "%Y-%m-%d %H:00:00")
    print("Check log between {} and {}".format(last_hour, now_hour))

    # 查询日志数据
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `log` WHERE `time` BETWEEN %s AND %s "
    cursor.execute(query=sql, args=[last_hour, now_hour])
    log_data = cursor.fetchall()
    sql = "SELECT * FROM `count` WHERE `cid` = (SELECT max(`cid`) FROM `count`)"
    cursor.execute(query=sql)
    user_num = int(cursor.fetchone()["user_num"])

    # 统计日志信息
    user_count = 0
    sign_count = 0
    for log in log_data:
        if log["function"] == "user_login" and log["message"] == "用户登录成功":
            if log["username"] not in username_set:
                user_count += 1
                username_set.add(log["username"])
        if log["function"] == "user_logout" and log["message"] == "用户退出成功":
            username_set.remove(log["username"])
            user_count -= 1
        if log["function"] == "user_check" and log["message"] in ["操作成功", "今天已经填报了"]:
            sign_count += 1

    # 写入统计信息
    date = Kit.unix2timestamp(time_now)
    time_range = "{}-{}".format(last_hour[11:13], now_hour[11:13])
    sql = "REPLACE INTO `count`(`date`, `range`, `user_num`, `sign_num`) VALUES(%s,%s,%s,%s)"
    cursor.execute(query=sql, args=[date, time_range, user_num + user_count, sign_count])
    conn.commit()

    return username_set


if __name__ == '__main__':
    main()
