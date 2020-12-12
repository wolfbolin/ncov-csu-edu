# coding=utf-8
import os
import re
import Kit
import zipfile
import requests
import subprocess

# 引入Windows特定库
if Kit.run_platform() == "windows":
    import winreg

# 全局变量
version_re = re.compile(r'^[1-9]\d*\.\d*.\d*')


def env_check(cache_path):
    print("[INFO]", "Check chrome driver env...")
    cache_path = os.path.abspath(cache_path)

    chrome_version = get_chrome_version()
    driver_version = get_driver_version(cache_path)

    if chrome_version == "0":
        print("[INFO]", "Please install chrome browser")
        return False

    if not chrome_version.startswith(driver_version):
        print("[INFO]", "Downloading driver")
        if not download_driver(chrome_version, cache_path):
            return False

    print("[INFO]", "Chrome driver check pass")
    return True


def get_chrome_version():
    print("[INFO]", "Check chrome version...")
    if Kit.run_platform() == "windows":
        try:
            # 从注册表中获得版本号
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
            version, _ = winreg.QueryValueEx(key, 'version')

            print('[INFO]", "Current Chrome Version: {}'.format(version))  # 这步打印会在命令行窗口显示
            return version_re.findall(version)[0]  # 返回前3位版本号
        except WindowsError as e:
            print('[INFO]", "Check Chrome failed:{}'.format(e))
            return "0"
    else:
        try:
            cmd = r'google-chrome-stable --version'
            out, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            out = out.decode('utf-8')
            version = out.split(' ')[2]  # 拆分回显字符串，获取版本号
            print('[INFO]", "Current Chrome Version:{}'.format(version))
            return version_re.findall(version)[0]  # 返回前3位版本号
        except WindowsError as e:
            print('[INFO]", "Check Chrome failed:{}'.format(e))
            return "0"


def get_driver_version(driver_path):
    print("[INFO]", "Check driver version...")
    if Kit.run_platform() == "windows":
        try:
            # 执行cmd命令并接收命令回显
            cmd = r'"{}/chromedriver" --version'.format(driver_path)
            out, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            out = out.decode('utf-8')
            _v = out.split(' ')[1]  # 拆分回显字符串，获取版本号
            print('[INFO]", "Current chrome driver Version:{}'.format(_v))
            return version_re.findall(_v)[0]
        except IndexError as e:
            print('[INFO]", "Check chrome driver failed:{}'.format(e))
            return "0"
    else:
        try:
            # 执行cmd命令并接收命令回显
            cmd = r'chromedriver --version'.format(driver_path)
            out, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            out = out.decode('utf-8')
            _v = out.split(' ')[1]  # 拆分回显字符串，获取版本号
            print('[INFO]", "Current chrome driver Version:{}'.format(_v))
            return version_re.findall(_v)[0]
        except IndexError as e:
            print('[INFO]", "Check chrome driver failed:{}'.format(e))
            return "0"


def download_driver(version, driver_path):
    # 获取淘宝镜像列表
    proxies = {"http": None, "https": None}
    session = requests.session()
    session.trust_env = False
    driver_path = os.path.abspath(driver_path)
    http_res = session.get("http://npm.taobao.org/mirrors/chromedriver", proxies=proxies)
    mirror_list = re.findall(r'<a href="(.*)">(.*)</a>', http_res.text)
    for mirrors in mirror_list:
        if mirrors[1].startswith(version):
            print("[INFO]", "Download version:", mirrors[1][:-1])
            # 下载压缩文件
            file_url = "http://npm.taobao.org" + mirrors[0] + "/chromedriver_win32.zip"
            print("[INFO]", "Driver url:", file_url)
            driver_res = session.get(file_url, proxies=proxies)
            # 写入压缩文件
            zip_path = driver_path + "/chromedriver_win32.zip"
            zip_file = open(zip_path, "wb")
            zip_file.write(driver_res.content)
            zip_file.close()
            # 下载完成后解压
            zip_file = zipfile.ZipFile(zip_path, 'r')
            for fileM in zip_file.namelist():
                zip_file.extract(fileM, os.path.dirname(zip_path))
            zip_file.close()
            # 删除残留文件
            os.remove(zip_path)

            print("[INFO]", "Download complete")
            return True
    print("[INFO]", "Not found suitable driver")
    return False
