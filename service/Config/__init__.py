# coding=utf-8
import os
import logging
import configparser


class UserConfigParser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, option_str):
        return option_str


def get_config(run_env=None):
    # 读取配置文件
    if run_env is None:
        if 'SERVICE_ENV' in os.environ:
            run_env = os.environ['SERVICE_ENV']
        else:
            run_env = 'production'
    print("Load config [%s]" % run_env)
    config_path = '{}/{}.ini'.format(os.path.split(os.path.abspath(__file__))[0], run_env)
    if os.path.isfile(config_path):
        config = UserConfigParser()
        config.read(config_path, encoding='utf-8')

        app_config = dict()
        for section in config.sections():
            app_config[section] = dict(config.items(section))

        app_config["RUN_ENV"] = run_env
        return app_config
    else:
        logging.error("Config not exist")
        exit()
