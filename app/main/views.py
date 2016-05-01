# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, redirect, url_for, request, current_app, abort, flash
from . import main
from forms import PostForm
from ..models import Permission, Post
from flask.ext.login import current_user, login_required
from .. import db
from .. import messages

# 定义路由函数
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    # 加载数据库所有文章
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)

# 索引文章的链接
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])

# 编辑文章
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash(messages.post_update_ok)
        return redirect(url_for('post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


# 编辑文章
@main.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMINISTER):
        abort(403)
    u = post.author
    db.session.delete(post)
    return redirect(url_for('user.profile', username=u.username))