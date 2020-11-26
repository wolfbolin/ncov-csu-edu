# coding=utf-8
from flask import Blueprint

deal_blue = Blueprint('deal', __name__)
from .deal import *
