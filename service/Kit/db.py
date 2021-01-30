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


def get_risk_area(conn):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT DISTINCT `province`, `city`, `level` FROM `region_risk`"
    cursor.execute(sql)

    risk_area = {}
    for area in cursor.fetchall():
        risk_area.setdefault(area["province"], {})
        risk_area[area["province"]].setdefault(area["city"], {})
        risk_area[area["province"]][area["city"]] = area["level"]

    return risk_area
