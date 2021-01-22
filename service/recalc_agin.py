import csv
import requests


def main():
    data_file = open("Config/recalc_list.csv", "r")
    csv_data = csv.DictReader(data_file)
    for item in csv_data:
        print(item)
        res = requests.get("https://covid19.csu-edu.cn/api/deal/order/check", params=item)
        print(res.text.strip())


if __name__ == '__main__':
    main()
