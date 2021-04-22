# coding=utf-8
import os
import Kit
import time
import json
import uuid
import random
import pymysql
import logging
import logstash
import threading
import multiprocessing
from singer import user_sign
from singer import read_risk_area
from dbutils.pooled_db import PooledDB
from cmq.account import Account as CMQ_Account
from cmq.cmq_exception import CMQExceptionBase


def multiprocess_master(config):
    # 初始化多进程
    process_bin = []
    process_num = int(config["BASE"]["process"])
    for gid in range(process_num):
        process = multiprocessing.Process(target=multithread_master, args=(config, gid,))
        process_bin.append(process)
    Kit.print_azure("Initialize process pool.")

    # 启动运行多进程
    Kit.print_azure("Start process in pool.")
    for process in process_bin:
        process.start()

    # 启动进程监控保活
    Kit.print_azure("Monitoring process pool...")
    while True:
        for gid, process in enumerate(process_bin):
            if not process.is_alive():
                Kit.print_yellow("Process {} stopped.Restarting...".format(gid))
                process_bin[gid] = multiprocessing.Process(target=multithread_master, args=(config, gid,))
                process_bin[gid].start()
        time.sleep(1)


def multithread_master(config, gid):
    pid = os.getpid()
    Kit.print_green("<P:{0} G:{1}> Start running...".format(pid, gid))

    # 初始化数据库连接池
    pool_config = config["POOL"]
    mysql_config = config["MYSQL"]
    mysql_pool = PooledDB(creator=pymysql, **mysql_config, **pool_config)
    Kit.print_green("<P:{0} G:{1}> Connect mysql done.".format(pid, gid))

    # 初始化线程池
    thread_bin = []
    thread_num = int(config["BASE"]["workers"])
    for tid in range(thread_num):
        thread_arg = (config, (pid, gid, tid), mysql_pool.connection())
        thread = threading.Thread(target=multithread_slave, args=thread_arg)
        thread_bin.append(thread)
    Kit.print_green("<P:{0} G:{1}> Init thread pool done.".format(pid, gid))

    # 启动运行多线程
    for thread in thread_bin:
        thread.start()
    Kit.print_green("<P:{0} G:{1}> Start thread pool.".format(pid, gid))

    # 启动多进程监控保活
    Kit.print_green("<P:{0} G:{1}> Monitoring thread pool.".format(pid, gid))
    while True:
        for tid, thread in enumerate(thread_bin):
            if not thread.is_alive():
                Kit.print_yellow("<P:{0} G:{1}> Thread {2} stopped.Restarting...".format(pid, gid, tid))
                thread_arg = (config, (pid, gid, tid), mysql_pool.connection())
                thread_bin[tid] = threading.Thread(target=multithread_slave, args=thread_arg)
                thread_bin[tid].start()


def multithread_slave(config, ids, conn):
    # 初始化ELK日志组件
    elk_logger = logging.getLogger(str(uuid.uuid1()))
    while elk_logger.hasHandlers():
        elk_logger.removeHandler(elk_logger.handlers[0])
    elk_logger.addHandler(logstash.LogstashHandler(config["ELK"]["host"], int(config["ELK"]["port"]), version=1))
    elk_logger.setLevel(logging.INFO)
    extra = json.loads(config["ELK"]["extra"])

    # 初始化消息队列
    user_config = {
        "host": config["CMQ"]["endpoint"],
        "secretId": config["CMQ"]["secret_id"],
        "secretKey": config["CMQ"]["secret_key"],
        "debug": False
    }
    queue_client = CMQ_Account(**user_config)
    sign_queue = queue_client.get_queue(config["CMQ"]["queue_name"])

    # 初始化风险地区
    risk_area = read_risk_area(conn)
    risk_expire = Kit.unix_time() + 600

    while True:
        # 建立连接并等待消息
        try:
            recv_msg = sign_queue.receive_message(random.randint(10, 30))
        except CMQExceptionBase:
            # Kit.print_white("<P:{0} G:{1} T:{2}> No message received".format(*ids))
            continue

        # 接收到打卡数据
        user_info = json.loads(recv_msg.msgBody)
        log_data = {
            "function": "user_sign_receiver",
            "username": user_info["username"],
            "result": "success",
            "status": "Receive message from CMQ",
            "message": str(recv_msg.msgId)
        }
        elk_logger.info(json.dumps(log_data), extra=extra)
        Kit.print_white("<P:{0} G:{1} T:{2}> {3} Receive message {4}".format(*ids, Kit.str_time(), recv_msg.msgId))

        # 检查风险地区更新
        if Kit.unix_time() > risk_expire:
            risk_area = read_risk_area(conn)
            risk_expire = Kit.unix_time() + 600

        # 完成用户打卡并记录日志
        try:
            user_sign(config, conn, user_info, risk_area, elk_logger)
        except BaseException as e:
            log_data = {
                "function": "user_sign",
                "username": user_info["username"],
                "result": "error",
                "status": "Sign user error",
                "message": str(e)
            }
            elk_logger.info(json.dumps(log_data), extra=extra)

        # 完成后删除消息
        sign_queue.delete_message(recv_msg.receiptHandle)
