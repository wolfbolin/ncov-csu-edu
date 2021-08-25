# coding=utf-8
import re
import Kit
import json
import uuid
import base64
import logging
import requests
from requests import utils
from bs4 import BeautifulSoup
from Cryptodome.Cipher import AES
from urllib.parse import urlencode
from flask import current_app as app


def user_sso_login(username, password):
    # 新版信息门户登录
    session = requests.session()
    session.headers.update({"Accept-Language": "zh-CN,zh;q=0.9"})
    auth_url = "https://wxxy.csu.edu.cn/ncov/wap/default/index"
    auth_url = "https://wxxy.csu.edu.cn/a_csu/api/cas/index?" + urlencode({"from": "wap", "redirect": auth_url})
    auth_url = "https://ca.csu.edu.cn/authserver/login?" + urlencode({"service": auth_url})
    http_result = session.get(auth_url)

    try:
        soup = BeautifulSoup(http_result.text, 'lxml')
        salt = soup.find(id="pwdLoginDiv").find(id="pwdEncryptSalt")["value"]
        exec_ = soup.find(id="pwdLoginDiv").find(id="execution")["value"]
    except TypeError:
        run_err = "BeautifulSoup TypeError"
        return "Failed", run_err, "连接SSO失败(信网中心连接异常)"

    # 检查是否需要验证码
    check_url = "https://ca.csu.edu.cn/authserver/checkNeedCaptcha.htl"
    params = {"username": username, "_": Kit.unix_time(1000)}
    http_result = session.get(check_url, params=params)
    check_result = json.loads(http_result.text)

    if check_result["isNeed"] is True:
        image_url = "https://ca.csu.edu.cn/authserver/getCaptcha.htl?" + str(Kit.unix_time(1000))
        image_result = session.get(image_url)
        image_data = image_result.content
        image_name = str(uuid.uuid1())
        image_path = "{}/captcha/{}.jpg".format(app.config["BASE"]["abspath"], image_name)
        open(image_path, "wb").write(image_data)
        return "Captcha", (auth_url, session, salt, exec_, image_name, image_data), "需要用户输入验证码"

    # 若无需验证码则直接进行登录
    params = {"salt": salt, "exec_": exec_, "captcha": None}
    return user_sso_login_step2(auth_url, session, username, password, params)


def user_sso_login_step2(auth_url, session, username, password, params):
    # 正式发起登录请求
    form_data = {
        "username": username,
        "password": get_aes_password(password, params["salt"]),
        "captcha": params["captcha"],
        "_eventId": "submit",
        "execution": params["exec_"],
        "cllt": "userNameLogin",
        "dllt": "generalLogin",
        "lt": "",
    }
    try:
        http_result = session.post(auth_url, data=form_data)
        re_result = re.search("<title>(.*)</title>", http_result.text)
        html_title = re_result.group(1)
    except requests.exceptions.ReadTimeout:
        run_err = "requests.exceptions.ReadTimeout:[%s]" % auth_url
        app.logger.error(run_err)
        return "Failed", run_err, "连接SSO失败(信网中心无响应)"
    except requests.exceptions.ConnectionError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % auth_url
        app.logger.error(run_err)
        return "Failed", run_err, "连接SSO失败(信网中心无响应)"
    except AttributeError:
        run_err = "requests.exceptions.ConnectionError:[%s]" % auth_url
        app.logger.error(run_err)
        return "Failed", run_err, "连接SSO异常(无法正确解析页面)"

    if html_title == "健康打卡":
        return "Success", session, "信息门户SSO登录成功"
    elif html_title == "完善资料":
        return "Failed", "Incomplete user data", "连接SSO失败(个人信息未完善)"
    elif html_title == "统一身份认证平台":
        try:
            soup = BeautifulSoup(http_result.text, 'lxml')
            tip = soup.find(id="formErrorTip").find(id="showErrorTip")
            tip_text = tip.contents[0].string
        except (TypeError, AttributeError):
            return "Failed", http_result.text, "连接SSO失败(未知的错误原因)"

        return "Failed", "User login failed. Platform did not jump", "连接SSO失败({})".format(tip_text)
    else:
        run_err = "Unknown html title: " + html_title
        return "Failed", run_err, "连接SSO失败(未知的错误原因)"


def get_aes_password(password, salt):
    encrypt_iv = Kit.random_string(16)
    encrypt_mode = AES.MODE_CBC
    encrypt_text = Kit.random_string(64) + str(password)
    fill_block_size = AES.block_size - len(encrypt_text) % AES.block_size
    encrypt_text = encrypt_text + fill_block_size * chr(fill_block_size)
    encrypt_lock = AES.new(salt.encode("utf-8"), encrypt_mode, encrypt_iv.encode('utf-8'))
    ciphered_text = encrypt_lock.encrypt(encrypt_text.encode("utf-8"))
    return base64.standard_b64encode(ciphered_text).decode("utf-8")


def user_sso_login_old(username, password):
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
    Kit.write_log(logging.WARNING, 'force_logout', username, "success", "Force user logout", message)
