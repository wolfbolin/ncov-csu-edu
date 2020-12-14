# coding=utf-8
import os
import re
import Kit
import json
import time
import Config
import pymysql
import selenium
from selenium.webdriver.common.by import By
from selenium.common import exceptions as web_exceptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

update_sql = "REPLACE `region_risk`(`province`,`city`,`block`,`level`,`time`) VALUES (%s,%s,%s,%s,%s)"
risk_rank = {
    "Unknown": 0,
    "低风险地区": 1,
    "中风险地区": 2,
    "高风险地区": 3,
}
risk_name = dict(zip(risk_rank.values(), risk_rank.keys()))
update_rate = 16


def main():
    cache_path = "./cache"
    os.makedirs(cache_path, exist_ok=True)
    if Kit.env_check(cache_path) is False:
        print("[ERR]", "Chrome driver run environment not found")
        return exit(1)

    # MySQL Connect
    config = Config.get_config()
    config['MYSQL']['port'] = int(config['MYSQL']['port'])
    conn = pymysql.connect(**config['MYSQL'])

    # Cache data
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `region_risk`"
    cursor.execute(sql)
    cache_data = {}
    for item in cursor.fetchall():
        cache_data.setdefault(item["province"], {})
        cache_data[item["province"]].setdefault(item["city"], {})
        cache_data[item["province"]][item["city"]].setdefault(item["block"], {})
        cache_data[item["province"]][item["city"]][item["block"]] = {
            "level": item["level"],
            "time": Kit.unix2timestamp(Kit.datetime2unix(item["time"]))
        }

    # Get data
    browser = open_website(cache_path)
    region_data = get_region_info(browser, conn, cache_data)

    # File
    if region_data != "":
        with open("{}/risk_data.json".format(cache_path), "w", encoding="utf-8") as file:
            file.write(json.dumps(region_data, ensure_ascii=False))


def open_website(driver_path):
    print("[INFO]", "Opening website")
    browser = Kit.run_browser(driver_path)
    browser.implicitly_wait(10)
    browser.get("http://bmfw.www.gov.cn/yqfxdjcx/index.html")

    return browser


def get_region_info(browser, conn, cache_data):
    cursor = conn.cursor()
    region_data = dict()

    # 获取更新时间
    global_update_time = browser.find_element_by_class_name("timeDate").text
    global_update_time = Kit.timestamp2unix(global_update_time, "%Y-%m-%d %H时")
    global_update_time = Kit.unix2timestamp(global_update_time)

    # 遍历省份列表
    province_dom = browser.find_element_by_class_name("province")
    province_num = len(province_dom.find_elements_by_tag_name("li"))
    for province_index in range(province_num):
        province = ""
        for k in range(5):
            try:
                province_list = province_dom.find_elements_by_tag_name("li")
                province_item = province_list[province_index]
                province = province_item.text
                province_item.click()
                time.sleep(16 / update_rate)
                break
            except selenium.common.exceptions.WebDriverException:
                province_dom = browser.find_element_by_class_name("province")
                print("[WARN]", "Open province [{}] error, retrying".format(province))
                time.sleep(16 / update_rate)
            if k < 4:
                continue
            raise ConnectionError("Run time error")

        if province in ["香港", "澳门", "台湾"]:
            continue
        print("[INFO]", "Open path:", province)
        region_data[province] = dict()

        # 遍历城市列表
        city_dom = browser.find_element_by_class_name("city")
        city_num = len(city_dom.find_elements_by_tag_name("li"))
        for city_index in range(city_num):
            city = ""
            for k in range(5):
                try:
                    city_list = city_dom.find_elements_by_tag_name("li")
                    city_item = city_list[city_index]
                    city = city_item.text
                    city_item.click()
                    time.sleep(16 / update_rate)
                    break
                except selenium.common.exceptions.WebDriverException:
                    print("[WARN]", "Open city [{}] error, retrying".format(city))
                    city_dom = browser.find_element_by_class_name("city")
                    time.sleep(16 / update_rate)
                if k < 4:
                    continue
                raise ConnectionError("Run time error")

            if city in ["东沙群岛"]:
                continue
            print("[INFO]", "Open path:", province, city)
            region_data[province][city] = dict()

            # 遍历街道列表
            block_dom = browser.find_element_by_class_name("block")
            block_num = len(block_dom.find_elements_by_tag_name("li"))
            for block_index in range(block_num):
                block_list = block_dom.find_elements_by_tag_name("li")
                block_item = block_list[block_index]
                block = re.sub(r"（.*?）", "", block_item.text)

                cache = cache_data.get(province, {}).get(city, {}).get(block, None)
                if cache is not None and cache["time"] == global_update_time:
                    print("[INFO]", "Hit cache", block, cache)
                    region_data[province][city][block] = cache
                    continue

                for k in range(5):
                    try:
                        block_item.click()
                        time.sleep(16 / update_rate)
                        break
                    except selenium.common.exceptions.WebDriverException:
                        block_dom = browser.find_element_by_class_name("block")
                        block_list = block_dom.find_elements_by_tag_name("li")
                        block_item = block_list[block_index]
                        block = re.sub(r"（.*?）", "", block_item.text)
                        print("[WARN]", "Open block [{}] error, retrying".format(block))
                        time.sleep(16 / update_rate)
                    if k < 4:
                        continue
                    raise ConnectionError("Run time error")
                print("[INFO]", "Open path:", province, city, block)

                # 获取风险等级
                try:
                    block_risk = browser.find_element_by_class_name("level-result").text
                except selenium.common.exceptions.WebDriverException:
                    block_risk = "Unknown"
                    level_dom = browser.find_element_by_class_name("risk-table")
                    level_dom = level_dom.find_element_by_tag_name("tbody")
                    risk_list = level_dom.find_elements_by_tag_name("tr")
                    for item in risk_list:
                        level_dom = item.find_elements_by_tag_name("td")[1]
                        block_risk = risk_cmp(block_risk, level_dom.text)

                update_time = browser.find_element_by_class_name("timeDate").text
                update_time = Kit.timestamp2unix(update_time, "%Y-%m-%d %H时")
                update_time = Kit.unix2timestamp(update_time)

                region_data[province][city][block] = {
                    "level": block_risk,
                    "time": update_time
                }

                cursor.execute(update_sql, args=[province, city, block, block_risk, update_time])
                conn.commit()

                print("[INFO]", province, city, block, block_risk, update_time)

    return region_data


def risk_cmp(risk1, risk2):
    risk1 = risk_rank[risk1]
    risk2 = risk_rank[risk2]
    temp = max(risk1, risk2)
    return risk_name[temp]


if __name__ == '__main__':
    main()
