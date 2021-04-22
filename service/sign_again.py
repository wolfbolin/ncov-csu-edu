# coding=utf-8
import time
import requests


def main():
    for m in range(10):  # 0 - 9
        for n in range(60):  # 0 - 59
            sign_time = "{:02d}:{:02d}".format(m, n)
            print("Sign time {}".format(sign_time))
            res = requests.get("https://covid19.csu-edu.cn/api/task/sign/{}?sms=No".format(sign_time))
            print(res.status_code)
            print(res.text.strip())
            time.sleep(1)


if __name__ == '__main__':
    main()
