# coding=utf-8
import logging
import re
import Kit
import json
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
        return False, run_err, "连接CAS失败(信网中心无响应)"
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        app.logger.error(run_err)
        return False, run_err, "连接CAS失败(信网中心无响应)"
    regex = r'tokenId.*value="(?P<tokenId>\w+)".*account.*value="(?P<account>\w+)".*Thirdsys.*value="(?P<Thirdsys>\w+)"'
    re_result = re.search(regex, http_result.text)
    if re_result is None:
        return False, "Missing tokenid or other information", "连接CAS失败(疑似账号密码错误)"

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
        return False, run_err, "连接SSO失败(信网中心无响应)"
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        app.logger.error(run_err)
        return False, run_err, "连接SSO失败(信网中心无响应)"

    return True, session, "信息门户SSO登录成功"


def base_info_update(conn, username, cookies):
    if cookies == "":
        user_force_logout(conn, username, "登录态丢失，自动退出登录状态")
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
        user_force_logout(conn, username, "登录态丢失，自动退出登录状态")
        Kit.print_red(run_err)
        return
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % url
        user_force_logout(conn, username, "登录态丢失，自动退出登录状态")
        Kit.print_red(run_err)
        return

    if http_result.status_code == 302:
        user_force_logout(conn, username, "登录态丢失，自动退出登录状态")
        return

    # 解析用户姓名
    regex = r'realname: "(.*)",'
    re_result = re.search(regex, http_result.text)
    realname = re_result.group(1)

    # 解析学院名称
    regex = r'xymc: "(.*)",'
    re_result = re.search(regex, http_result.text)
    college = re_result.group(1)

    app.logger.info("登录用户身份：{}={}@{}".format(username, realname, college))

    # 更新用户数据
    cursor = conn.cursor()
    sql = "UPDATE `user` SET `realname`=%s, `college`=%s WHERE `username`=%s"
    cursor.execute(sql, args=[realname, college, username])
    conn.commit()


def user_force_logout(conn, username, message=Kit.str_time()):
    cursor = conn.cursor()
    sql = "UPDATE `user` SET `online`='No' WHERE `username`=%s"
    cursor.execute(sql, args=[username])
    Kit.write_log(logging.WARNING, 'force_logout', username, "success", message)
