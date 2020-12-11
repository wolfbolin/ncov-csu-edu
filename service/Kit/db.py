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
    sql = "SELECT DISTINCT `province`, `city`, `level` FROM `region_risk` WHERE `level` != '低风险地区'"
    cursor.execute(sql)

    risk_area = {}
    for area in cursor.fetchall():
        province = area["province"] + "省"
        risk_area.setdefault(province, {})
        risk_area[province].setdefault(area["city"], {})
        risk_area[province][area["city"]] = area["level"]

    return risk_area
