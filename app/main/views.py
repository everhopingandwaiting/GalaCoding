# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, redirect, url_for
from . import main

# 定义路由函数
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')