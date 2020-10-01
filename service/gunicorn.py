# coding=utf-8
import os
import multiprocessing

if not os.path.exists('./log/'):
    os.makedirs('./log/')

bind = '0.0.0.0:80'
loglevel = "info"
workers = multiprocessing.cpu_count()
