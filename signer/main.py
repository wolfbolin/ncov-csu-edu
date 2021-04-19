# coding=utf-8
import Kit
from Config import get_config
from turbo import multiprocess_master


def main():
    # 读取配置文件
    config = get_config()
    for key in config["POOL"].keys():
        config["POOL"][key] = int(config["POOL"][key])
    config["MYSQL"]["port"] = int(config["MYSQL"]["port"])
    Kit.print_azure("Read config success.")

    # 运行启动
    multiprocess_master(config)


if __name__ == '__main__':
    main()
