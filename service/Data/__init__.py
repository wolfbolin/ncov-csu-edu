# coding=utf-8
from flask import Blueprint

data_blue = Blueprint('data', __name__)
from .risk import *
from .task import *
from .count import *
