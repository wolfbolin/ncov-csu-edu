# coding=utf-8
import Kit
import pymysql
from flask import jsonify
from Data import data_blue
from flask import current_app as app


@data_blue.route('/risk', methods=["GET"])
def fetch_risk():
    conn = app.mysql_pool.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `region_risk`"
    cursor.execute(sql)

    return jsonify({
        "status": "success",
        "risk_list": cursor.fetchall(),
        "update_time": Kit.get_key_val(conn, "risk_update_time")
    })
