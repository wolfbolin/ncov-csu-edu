# coding=utf-8
import pymysql


def get_key_val(conn, key):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `val` FROM `kvdb` WHERE `key`=%s"
    cursor.execute(query=sql, args=[key])
    res = cursor.fetchone()
    if res is None:
        return ""
    else:
        return res["val"]




