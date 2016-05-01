# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, redirect, url_for, abort, flash
from . import user
from ..models import User, Role, Post
from flask.ext.login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from .. import messages
from ..decorators import admin_required

# 定义路由函数
@user.route('/<username>', methods=['GET', 'POST'])
def user_profile(username):
    tmp_user = User.query.filter_by(username=username).first()
    if tmp_user is None:
        abort(404)
    posts = tmp_user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user/user.html', user=tmp_user, posts=posts)

# 用户编辑资料页
@user.route('/edit', methods=['GET', 'POST'])
@login_required
def user_edit():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(messages.update_profile_ok)
        return redirect(url_for('user.user_profile', username=current_user.username))
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    form.name.data = current_user.name
    return render_template('user/edit.html', form=form)

# 直接索引用户资料页，同时需要管理员权限
@user.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        # 不能修改邮件
        # user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(messages.update_profile_ok)
        return redirect(url_for('user.user_profile', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('user/edit.html', form=form, user=user)