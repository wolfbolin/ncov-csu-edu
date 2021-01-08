# coding=utf-8
import os
import re
import Kit
import time
import Config
import pymysql


def main():
    config = Config.get_config()

    # Check environment
    cache_path = config['BASE']['cache_path']
    os.makedirs(cache_path, exist_ok=True)
    if Kit.env_check(cache_path) is False:
        print("[ERR]", "Chrome driver run environment not found")
        return exit(1)

    # MySQL Connect
    config['MYSQL']['port'] = int(config['MYSQL']['port'])
    conn = pymysql.connect(**config['MYSQL'])

    # Get update time
    cursor = conn.cursor()
    sql = "SELECT `val` FROM `kvdb` WHERE `key` = 'risk_update_time'"
    cursor.execute(sql)
    local_data_time = cursor.fetchone()[0]
    print("[INFO]", "Local update time:", local_data_time)

    # Get data
    browser = open_website(cache_path, config['BASE']['headless'])
    risk_data = get_region_info(browser, local_data_time)
    browser.quit()

    if risk_data is None:
        print("[INFO]", "Do nothing, waiting...")
        time.sleep(10 * 60)
    else:
        print("[INFO]", "Update local data")
        sql = "DELETE FROM `region_risk`"
        cursor.execute(sql)
        sql = "REPLACE `region_risk`(`province`,`city`,`block`,`level`) VALUES (%s,%s,%s,%s)"
        for item in risk_data[0]:
            cursor.execute(sql, args=[item[0], item[1], item[2], "高风险"])
        for item in risk_data[1]:
            cursor.execute(sql, args=[item[0], item[1], item[2], "中风险"])
        sql = "UPDATE `kvdb` SET `val`=%s WHERE `key`='risk_update_time'"
        cursor.execute(sql, args=[risk_data[2]])
        conn.commit()
    print("[INFO]", "Update finish")
    return


def open_website(driver_path, headless):
    print("[INFO]", "Opening website")
    browser = Kit.run_browser(driver_path, headless)
    browser.implicitly_wait(10)
    browser.get("http://bmfw.www.gov.cn/yqfxdjcx/risk.html")

    return browser


def get_region_info(browser, local_data_time):
    # Get update time
    remote_data_time = browser.find_element_by_class_name("r-time").text
    remote_data_time = re.search(r'\d{4}-\d{2}-\d{2}', remote_data_time)
    remote_data_time = remote_data_time.group(0)
    print("[INFO]", "Remote update time:", remote_data_time)

    if local_data_time == remote_data_time:
        print("[INFO]", "Remote data not updated")
        return None

    # Get risk data
    area_content = browser.find_elements_by_class_name("m-content")

    # Get high risk area
    high_risk_dom = area_content[0]
    high_risk_list = high_risk_dom.find_elements_by_class_name("m-header")
    high_risk_list = [it.get_attribute('textContent').split(" ") for it in high_risk_list]
    print("[INFO]", "Remote high risk num:", len(high_risk_list))

    # Get medium risk area
    medium_risk_dom = area_content[1]
    medium_risk_list = medium_risk_dom.find_elements_by_class_name("m-header")
    medium_risk_list = [it.get_attribute('textContent').split(" ") for it in medium_risk_list]
    print("[INFO]", "Remote medium risk num:", len(medium_risk_list))
    for item in medium_risk_list:
        item[2] = re.sub(r"（.*?）", "", item[2])

    return high_risk_list, medium_risk_list, remote_data_time


if __name__ == '__main__':
    main()
