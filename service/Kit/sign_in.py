# coding=utf-8
import re
import Kit
import json
import requests
from flask import current_app as app


def user_login(username, password):
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


def user_clock(session):
    # 获取历史数据
    url = "https://wxxy.csu.edu.cn/ncov/wap/default/index"
    try:
        http_result = session.get(url)
    except requests.exceptions.ReadTimeout:
        run_err = "requests.exceptions.ReadTimeout:[%s]" % url
        Kit.print_red(run_err)
        return False, "自动登录失败", run_err
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        Kit.print_red(run_err)
        return False, "自动登录失败", run_err
    regex = r'oldInfo: (.*),'
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return False, "缺少历史数据", "Missing history data"
    sign_data = json.loads(re_result.group(1))
    regex = r'var def = (.*);'
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return False, "缺少模版数据", "Missing template data"
    def_string = re_result.group(1)
    def_data = json.loads(def_string)
    api_string = def_data["geo_api_info"].replace(r'\"', '"')
    if len(api_string.strip()) == 0:
        return False, "缺少定位数据", "Missing location data"
    api_data = json.loads(api_string)
    sign_data["geo_api_info"] = str(api_string)
    sign_data["address"] = api_data["formattedAddress"]
    sign_data["area"] = api_data["addressComponent"]["province"] \
                        + api_data["addressComponent"]["city"] \
                        + api_data["addressComponent"]["district"]
    sign_data["province"] = api_data["addressComponent"]["province"]
    sign_data["city"] = api_data["addressComponent"]["city"]
    if sign_data["province"] in ('长沙市', '上海市', '重庆市', '天津市'):
        sign_data["city"] = sign_data["province"]

    # 重发数据完成签到
    url = "https://wxxy.csu.edu.cn/ncov/wap/default/save"
    try:
        http_result = session.post(url, data=sign_data)
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
        return True, sign_res["m"], "success"
    elif sign_res["e"] == 1 and sign_res["m"] == "今天已经填报了":
        return True, sign_res["m"], "success"
    return False, sign_res["m"], "Unknown situation"
