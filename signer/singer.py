# coding=utf-8
import re
import Kit
import json
import pymysql
import requests
from requests import utils


def read_risk_area(conn):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT DISTINCT `province`, `city`, `block`, `level` FROM `region_risk`"
    cursor.execute(sql)

    risk_area = {}
    for area in cursor.fetchall():
        risk_area.setdefault(area["province"], {})
        risk_area[area["province"]].setdefault(area["city"], {})
        risk_area[area["province"]][area["city"]].setdefault(area["block"], {})
        risk_area[area["province"]][area["city"]][area["block"]] = area["level"]

    return risk_area


def handle_sign_task(config, risk_area, user_info, elk_logger):
    # 执行自动打卡逻辑
    result, status, message = user_sign(user_info, risk_area)

    # 上报执行结果与数据
    log_data = {
        "function": "user_sign_task",
        "username": user_info["username"],
        "result": result,
        "status": status,
        "message": message
    }
    elk_logger.info(json.dumps(log_data), extra=json.loads(config["ELK"]["extra"]))

    # 处理后续流程计划
    if result in ["content_error", "response_error"]:
        return None
    elif result == "connect_error":
        user_info["trace"] += int(1)
        # 尝试放入队列进行重试
        if user_info["vip"] == "Yes" and user_info["trace"] < 10 \
                or user_info["vip"] != "Yes" and user_info["trace"] < 3:
            return {
                "type": "task",
                "data": user_info,
                "user": user_info["username"]
            }

    flow_data = {
        "result": result,
        "status": status,
        "message": message,
        "user_info": user_info
    }
    return {
        "type": "done",
        "data": flow_data,
        "user": user_info["username"]
    }


def user_sign(user_info, risk_area):
    # 初始化网络连接
    session = requests.Session()
    cookies = json.loads(user_info["cookies"])
    cookies_jar = requests.utils.cookiejar_from_dict(cookies)
    session.cookies = cookies_jar
    user_info["cookies_update"] = "No"

    # 获取历史数据
    url = "https://wxxy.csu.edu.cn/ncov/wap/default/index"
    try:
        http_result = session.get(url, allow_redirects=False, timeout=(3, 10))
        if http_result.status_code == 302:
            Kit.print_red("[SIGN] Step 1 error: User {} lost session".format(user_info["username"]))
            return "lost_status", "User session loss", "绑定登录失效"
    except requests.exceptions.ReadTimeout:
        Kit.print_red("[SIGN] Step 1 error: ：requests.exceptions.ReadTimeout")
        return "connect_error", "ReadTimeout at step 1", "自动登录超时"
    except requests.exceptions.ConnectionError:
        Kit.print_red("[SIGN] Step 1 error: ：requests.exceptions.ConnectionError")
        return "connect_error", "ConnectionError at step 1", "自动登录超时"

    # 解析模板数据
    regex = r'var def = (.*);'
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return "content_error", "Missing template data", "缺少模版数据"
    def_data = json.loads(re_result.group(1))

    # 解析历史数据
    regex = r'oldInfo: (.*),'
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return "content_error", "Missing history data", "缺少历史数据"
    sign_data = json.loads(re_result.group(1))

    # 合并两份数据
    for def_key in def_data.keys():
        if def_key in ["id", "date", "created"]:
            continue
        if def_key in sign_data.keys():
            def_data[def_key] = sign_data[def_key]

    # 提取打卡位置
    if "geo_api_info" not in def_data.keys() or \
            len(def_data["geo_api_info"].strip()) == 0:
        return "content_error", "Missing location data", "缺少定位数据"
    api_data = json.loads(def_data["geo_api_info"].replace(r'\"', '"'))
    user_location = {
        "country": api_data["addressComponent"]["country"],
        "province": api_data["addressComponent"]["province"],
        "city": api_data["addressComponent"]["city"],
        "district": api_data["addressComponent"]["district"],
        "township": api_data["addressComponent"]["township"]
    }
    if user_location["province"] in ('北京市', '上海市', '重庆市', '天津市'):
        user_location["city"] = user_location["district"]
        user_location["district"] = user_location["township"]

    # 检查打卡位置
    risk_data = risk_area.get(user_location["province"], {})
    risk_data = risk_data.get(user_location["city"], {})
    risk_data = risk_data.get(user_location["district"], None)
    if risk_data is not None and user_info["me"] != "Yes":
        return "risk_area", json.dumps(user_location, ensure_ascii=False), "风险地区暂停"

    # 解析打卡状态
    regex = r"hasFlag: '(.*)',"
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return "content_error", "Missing sign flag data", "缺少打卡标记"
    flag_data = re_result.group(1)
    if flag_data == "1":
        return "stop_sign", json.dumps(user_location, ensure_ascii=False), "今日已提交"

    # 进行用户签到
    url = "https://wxxy.csu.edu.cn/ncov/wap/default/save"
    try:
        http_result = session.post(url, data=sign_data, timeout=(3, 10))
    except requests.exceptions.ReadTimeout:
        Kit.print_red("[SIGN] Step 2 error: ：requests.exceptions.ReadTimeout")
        return "connect_error", "ReadTimeout at step 2", "自动打卡超时"
    except requests.exceptions.ConnectionError:
        Kit.print_red("[SIGN] Step 2 error: ：requests.exceptions.ConnectionError")
        return "connect_error", "ConnectionError at step 2", "自动打卡失败"

    # 修改用户Cookie
    session_cookies = session.cookies.get_dict()
    if session_cookies != cookies and len(session_cookies.keys()) != 0:
        Kit.print_purple("[SIGN] User {} cookies update".format(user_info["username"]))
        new_cookies = json.dumps(session_cookies)
        user_info["cookies_update"] = "Yes"
        user_info["cookies_data"] = new_cookies

    # 解析响应数据
    sign_res = json.loads(http_result.text)
    if sign_res["e"] == 0:
        return "success", json.dumps(user_location, ensure_ascii=False), "提交信息成功"
    elif sign_res["e"] == 1 and sign_res["m"] == "今天已经填报了":
        return "success", json.dumps(user_location, ensure_ascii=False), sign_res["m"]
    return "response_error", "Unknown situation", sign_res["m"]
