import pymysql
from Config import get_config
from User.user_info import base_info_update


def main():
    config = get_config("connect")
    config.get('MYSQL')["port"] = int(config.get('MYSQL')["port"])
    # 连接数据库
    conn = pymysql.connect(**config['MYSQL'])
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `username`,`cookies` FROM `user` WHERE `online`='Yes'"
    cursor.execute(sql)
    user_list = cursor.fetchall()
    print(len(user_list))

    for user in user_list:
        cookies = user["cookies"]
        if cookies == "":
            cookies = "{}"
        base_info_update(conn, user["username"], cookies)


if __name__ == '__main__':
    main()
