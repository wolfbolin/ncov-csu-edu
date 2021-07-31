# coding=utf-8
import os
import re
import Kit
import json
import time
import Config
import requests


def main():
    config = Config.get_config()
    print("[INFO]", "Start at", Kit.str_time())

    # Check environment
    cache_path = config['BASE']['cache_path']
    os.makedirs(cache_path, exist_ok=True)
    if Kit.env_check(cache_path) is False:
        print("[ERR]", "Chrome driver run environment not found")
        return exit(1)

    # Get update time
    res = requests.get("https://covid19.csu-edu.cn/api/data/risk")
    local_data_time = json.loads(res.text)["update_time"]
    print("[INFO]", "Local update time:", local_data_time)

    # Get data
    browser = open_website(cache_path, config['BASE']['headless'])
    risk_data = get_region_info(config, browser, local_data_time)
    browser.quit()

    if risk_data is None:
        print("[INFO]", "Do nothing, waiting...")
        time.sleep(10 * 60)
    else:
        print("[INFO]", "Update local data")
        if config["RUN_ENV"] == "develop":
            url = "http://127.0.0.1:12880/api/data/risk"
        else:
            url = "https://covid19.csu-edu.cn/api/data/risk"

        data = {
            "token": config["BASE"]["risk_token"],
            "high_risk": risk_data[0],
            "medium_risk": risk_data[1],
            "update_time": risk_data[2]
        }
        requests.post(url, json=data)

    print("[INFO]", "Update finish")
    print("[INFO]", "End at", Kit.str_time())
    return


def open_website(driver_path, headless):
    print("[INFO]", "Opening website")
    browser = Kit.run_browser(driver_path, headless)
    browser.implicitly_wait(10)
    browser.get("http://bmfw.www.gov.cn/yqfxdjcx/risk.html")

    return browser


def get_region_info(config, browser, local_data_time):
    # Get update time
    remote_data_time = browser.find_element_by_class_name("r-time").text
    remote_data_time = re.search(r'\d{4}-\d{2}-\d{2} \d{2}', remote_data_time)
    remote_data_time = remote_data_time.group(0) + ":00"
    print("[INFO]", "Remote update time:", remote_data_time)

    if local_data_time == remote_data_time and config["RUN_ENV"] != "develop":
        print("[INFO]", "Remote data not updated")
        return None

    change_tab = browser.find_element_by_class_name("r-high")
    change_tab.click()
    time.sleep(2)

    # Get high risk area
    high_risk_list = []
    for i in range(50):
        high_risk_dom = browser.find_element_by_class_name("h-content")
        element_temp_list = high_risk_dom.find_elements_by_class_name("h-header")
        high_risk_list += [it.get_attribute('textContent').strip().split(" ")[:3] for it in element_temp_list]

        next_button = high_risk_dom.find_element_by_id("nextPage")
        if next_button.is_enabled():
            next_button.click()
            time.sleep(2)
        else:
            break
    print("[INFO]", "Remote high risk num:", len(high_risk_list))

    change_tab = browser.find_element_by_class_name("r-middle")
    change_tab.click()
    time.sleep(2)

    # Get medium risk area
    medium_risk_list = []
    for i in range(50):
        medium_risk_dom = browser.find_element_by_class_name("m-content")
        element_temp_list = medium_risk_dom.find_elements_by_class_name("m-header")
        medium_risk_list += [it.get_attribute('textContent').strip().split(" ")[:3] for it in element_temp_list]

        next_button = medium_risk_dom.find_element_by_id("nextPage")
        if next_button.is_enabled():
            next_button.click()
            time.sleep(2)
        else:
            break
    print("[INFO]", "Remote medium risk num:", len(medium_risk_list))
    for item in medium_risk_list:
        item[2] = re.sub(r"（.*?）", "", item[2])

    return high_risk_list, medium_risk_list, remote_data_time


if __name__ == '__main__':
    main()
