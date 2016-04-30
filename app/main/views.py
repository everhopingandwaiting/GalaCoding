# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, redirect, url_for
from . import main
from forms import PostForm
from ..models import Permission, Post
from flask.ext.login import current_user
from .. import db

# 定义路由函数
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    # 加载数据库所有文章
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)