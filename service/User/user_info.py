# coding=utf-8
import re
import Kit
import json
import pymysql
import requests
from requests import utils
from flask import current_app as app


def user_sso_login(username, password):
    # 信息门户登录
    session = requests.Session()
    url = "http://ca.its.csu.edu.cn/Home/Login/215"
    http_data = {
        "userName": username,
        "passWord": password,
        "enter": "true"
    }
    try:
        http_result = session.post(url, data=http_data)
    except requests.exceptions.ReadTimeout:
        run_err = "requests.exceptions.ReadTimeout:[%s]" % url
        app.logger.error(run_err)
        return False, "连接CAS失败(信网中心无响应)", run_err
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        app.logger.error(run_err)
        return False, "连接CAS失败(连接信网中心失败)", run_err
    regex = r'tokenId.*value="(?P<tokenId>\w+)".*account.*value="(?P<account>\w+)".*Thirdsys.*value="(?P<Thirdsys>\w+)"'
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return False, "连接CAS失败(疑似账号密码错误)", "Missing tokenid or other information"

    # sso认证
    url = "https://wxxy.csu.edu.cn/a_csu/api/sso/validate"
    http_data = {
        "tokenId": re_result["tokenId"],
        "account": re_result["account"],
        "Thirdsys": re_result["Thirdsys"]
    }
    try:
        session.post(url, data=http_data)
    except requests.exceptions.ReadTimeout:
        run_err = "requests.exceptions.ReadTimeout:[%s]" % url
        app.logger.error(run_err)
        return False, "连接SSO失败(信网中心无响应)", run_err
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        app.logger.error(run_err)
        return False, "连接SSO失败(信网中心无响应)", run_err

    return True, session, "success"


def user_sign_task(config, user_info, risk_area):
    # 连接数据库
    try:
        # 连接数据库
        conn = pymysql.connect(**config['MYSQL'])
        cursor = conn.cursor()
        # 初始化连接
        session = requests.Session()
        cookies = json.loads(user_info["cookies"])
        cookies_jar = requests.utils.cookiejar_from_dict(cookies)
        session.cookies = cookies_jar
        # 执行签到
        status, data, run_err = user_sign_in(session, risk_area)
        # 检查更新
        session_cookies = session.cookies.get_dict()
        if session_cookies != cookies and len(session_cookies.keys()) != 0:
            Kit.print_blue("User {} cookies update".format(user_info["username"]))
            new_cookies = json.dumps(session_cookies)
            sql = "UPDATE `user` SET `cookies` = %s WHERE `username` = %s"
            cursor.execute(query=sql, args=[new_cookies, user_info["username"]])
            conn.commit()

        if user_info["sms"] == "Yes":
            Kit.send_sms_message(config["BASE"]["sms_token"], user_info["nickname"],
                                 user_info["phone"], (status, data, run_err))

        # 任务完成
        Kit.write_log(conn, 'user_check', user_info["username"], status, data, run_err)
        sql = "UPDATE `task` SET `status`=%s, `sign_time`=%s, `location`=%s WHERE `username`=%s AND `date` = CURDATE()"
        cursor.execute(sql, args=["success" if status else "error",
                                  Kit.str_time("%H:%M:%S"),
                                  run_err if status else "Unknown",
                                  user_info["username"]])
        conn.commit()
    except BaseException as e:
        # 异常故障强制登出
        conn = pymysql.connect(**config['MYSQL'])
        user_force_logout(conn, user_info["username"], "打卡状态异常", "Runtime error:{}".format(e))
        Kit.print_red(e)


def user_sign_in(session, risk_area):
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
    sign_data["geo_api_info"] = str(api_string)
    sign_data["address"] = api_data["formattedAddress"]
    sign_data["area"] = "{} {} {}".format(api_data["addressComponent"]["province"],
                                          api_data["addressComponent"]["city"],
                                          api_data["addressComponent"]["district"])
    sign_data["province"] = api_data["addressComponent"]["province"]
    sign_data["city"] = api_data["addressComponent"]["city"]
    if sign_data["province"] in ('北京市', '上海市', '重庆市', '天津市'):
        sign_data["city"] = sign_data["province"]

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
        return False, "自动终止({})".format(risk_data), json.dumps(location, ensure_ascii=False)

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


def base_info_update(conn, username, cookies):
    if cookies == "":
        user_force_logout(conn, username, "登录态丢失", "自动退出登录状态")
        return

    # 初始化连接
    session = requests.Session()
    cookies = json.loads(cookies)
    cookies_jar = requests.utils.cookiejar_from_dict(cookies)
    session.cookies = cookies_jar

    # 获取页面数据
    url = "https://wxxy.csu.edu.cn/ncov/wap/default/index"
    try:
        http_result = session.get(url, proxies={"https": None}, allow_redirects=False)
    except requests.exceptions.ReadTimeout:
        run_err = "requests.exceptions.ReadTimeout:[%s]" % url
        user_force_logout(conn, username, "登录态丢失", "自动退出登录状态")
        Kit.print_red(run_err)
        return
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        user_force_logout(conn, username, "登录态丢失", "自动退出登录状态")
        Kit.print_red(run_err)
        return

    if http_result.status_code == 302:
        user_force_logout(conn, username, "登录态丢失", "自动退出登录状态")
        return

    # 解析用户姓名
    regex = r'realname: "(.*)",'
    re_result = re.search(regex, http_result.text)
    realname = re_result.group(1)

    # 解析学院名称
    regex = r'xymc: "(.*)",'
    re_result = re.search(regex, http_result.text)
    college = re_result.group(1)

    print("用户身份：{}={}.{}".format(username, realname, college))

    # 更新用户数据
    cursor = conn.cursor()
    sql = "UPDATE `user` SET `realname`=%s, `college`=%s WHERE `username`=%s"
    cursor.execute(sql, args=[realname, college, username])
    conn.commit()


def user_force_logout(conn, username, status, message=Kit.str_time()):
    cursor = conn.cursor()
    sql = "UPDATE `user` SET `online`='No' WHERE `username`=%s"
    cursor.execute(sql, args=[username])
    Kit.write_log(conn, 'info_update', username, 0, status, message)
