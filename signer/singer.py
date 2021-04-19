# coding=utf-8
import re
import Kit
import json
import pymysql
import requests
from requests import utils


def read_risk_area(conn):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT DISTINCT `province`, `city`, `level` FROM `region_risk`"
    cursor.execute(sql)

    risk_area = {}
    for area in cursor.fetchall():
        risk_area.setdefault(area["province"], {})
        risk_area[area["province"]].setdefault(area["city"], {})
        risk_area[area["province"]][area["city"]] = area["level"]

    return risk_area


def user_sign(config, conn, user_info, risk_area, elk_logger):
    # 初始化网络连接
    session = requests.Session()
    cookies = json.loads(user_info["cookies"])
    cookies_jar = requests.utils.cookiejar_from_dict(cookies)
    session.cookies = cookies_jar

    # 执行签到任务
    result, status, message = user_sign_core(session, risk_area)

    # 连接数据库
    cursor = conn.cursor()

    # 检查数据更新
    session_cookies = session.cookies.get_dict()
    if session_cookies != cookies and len(session_cookies.keys()) != 0:
        Kit.print_purple("User {} cookies update".format(user_info["username"]))
        new_cookies = json.dumps(session_cookies)
        sql = "UPDATE `user` SET `cookies` = %s WHERE `username` = %s"
        cursor.execute(query=sql, args=[new_cookies, user_info["username"]])

    # 写入用户打卡位置
    if result is True:
        sql = "INSERT `location`(date,user,location) VALUES(%s,%s,%s)"
        cursor.execute(sql, args=[Kit.str_time("%Y-%m-%d"), user_info["username"], message])

    conn.commit()

    # 向用户发送短信
    if user_info["sms"] == "Yes":
        sms_message = (result, status, message)
        send_sms_message(config["BASE"]["sms_token"], user_info["nickname"], user_info["phone"], sms_message)

    # 上报打卡日志
    extra = json.loads(config["ELK"]["extra"])
    log_data = {
        "function": "user_sign",
        "username": user_info["username"],
        "result": "success" if result else "error",
        "status": status,
        "message": message
    }
    elk_logger.info(json.dumps(log_data), extra=extra)


def send_sms_message(sms_token, user_name, user_phone, result):
    # 位置信息
    if result[0] is True:
        location = json.loads(result[2])
        location = "{}-{}".format(location["province"], location["city"])
    else:
        location = "暂无"

    url = "https://core.wolfbolin.com/message/sms/send/%s" % user_phone
    data = {
        "phone": user_phone,
        "template": 805977,
        "params": [
            user_name,
            Kit.str_time("%H:%M"),
            str(result[1]),
            location
        ]
    }
    params = {
        "token": sms_token
    }
    res = requests.post(url=url, json=data, params=params)
    Kit.print_purple("Send SMS to {}".format(user_phone))


def user_sign_core(session, risk_area):
    """
    完成打卡数据获取与打卡全流程
    :param session: 网络连接session
    :param risk_area: 风险区域信息
    :return: 打卡成功(Boolean) 响应描述 响应信息
    """
    # 获取历史数据
    url = "https://wxxy.csu.edu.cn/ncov/wap/default/index"
    try:
        http_result = session.get(url, proxies={"https": None})
    except requests.exceptions.ReadTimeout:
        run_err = "requests.exceptions.ReadTimeout:[%s]" % url
        Kit.print_red(run_err)
        return False, "自动登录失败", run_err
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        Kit.print_red(run_err)
        return False, "自动登录失败", run_err

    # 历史数据解析
    regex = r'oldInfo: (.*),'
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return False, "缺少历史数据", "Missing history data"
    sign_data = json.loads(re_result.group(1))

    # 模板数据解析
    regex = r'var def = (.*);'
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return False, "缺少模版数据", "Missing template data"

    # 定位数据解析
    def_string = re_result.group(1)
    def_data = json.loads(def_string)
    api_string = def_data["geo_api_info"].replace(r'\"', '"')
    if len(api_string.strip()) == 0:
        return False, "缺少定位数据", "Missing location data"

    # 位置信息回填
    api_data = json.loads(api_string)
    # sign_data["geo_api_info"] = str(api_string)
    # sign_data["address"] = api_data["formattedAddress"]
    # sign_data["area"] = "{} {} {}".format(api_data["addressComponent"]["province"],
    #                                       api_data["addressComponent"]["city"],
    #                                       api_data["addressComponent"]["district"])
    # sign_data["province"] = api_data["addressComponent"]["province"]
    # sign_data["city"] = api_data["addressComponent"]["city"]
    # if sign_data["province"] in ('北京市', '上海市', '重庆市', '天津市'):
    #     sign_data["city"] = sign_data["province"]

    # 位置信息留存
    location = {
        "country": api_data["addressComponent"]["country"],
        "province": api_data["addressComponent"]["province"],
        "city": api_data["addressComponent"]["city"],
        "district": api_data["addressComponent"]["district"],
        "township": api_data["addressComponent"]["township"]
    }
    if location["province"] in ('北京市', '上海市', '重庆市', '天津市'):
        location["city"] = location["district"]
        location["district"] = location["township"]

    # 检查打卡位置
    risk_data = risk_area.get(location["province"], {})
    risk_data = risk_data.get(location["city"], None)
    if risk_data is not None:
        return True, "中高风险地区".format(risk_data), json.dumps(location, ensure_ascii=False)

    # 重发数据完成签到
    url = "https://wxxy.csu.edu.cn/ncov/wap/default/save"
    try:
        http_result = session.post(url, data=sign_data, proxies={"https": None})
    except requests.exceptions.ReadTimeout:
        run_err = "requests.exceptions.ReadTimeout:[%s]" % url
        Kit.print_red(run_err)
        return False, "自动签到失败", run_err
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        Kit.print_red(run_err)
        return False, "自动签到失败", run_err

    sign_res = json.loads(http_result.text)
    if sign_res["e"] == 0:
        return True, sign_res["m"], json.dumps(location, ensure_ascii=False)
    elif sign_res["e"] == 1 and sign_res["m"] == "今天已经填报了":
        return True, sign_res["m"], json.dumps(location, ensure_ascii=False)
    return False, sign_res["m"], "Unknown situation"
