# coding=utf-8
from flask import Blueprint

task_blue = Blueprint('task', __name__)
from .task import *
from .count import *
