# -*- coding:utf8 -*-
'''
index route.
'''
from flask import render_template, redirect, url_for, request, current_app, abort, flash
from . import main
from forms import PostForm
from ..comment.forms import CommentForm
from ..models import Permission, Post, Concern_posts, Comment
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
    shows = request.args.get('shows')
    if shows is not None and shows == 'recommend':
        pagination = current_user.recommend_posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False)
    elif shows is not None and shows == 'concern':
        pagination = current_user.concern_posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False)
    else:
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination, shows=shows)

# 索引文章的链接
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if current_user.can(Permission.COMMENT) and form.validate_on_submit():
        comment = Comment(author=current_user._get_current_object(), body=form.comment.data, post=post)
        db.session.add(comment)
        db.session.commit()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', form=form, posts=[post], comments=comments, pagination=pagination)

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
        return redirect(url_for('main.post', id=post.id))
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

# 关注谋篇文章
@main.route('/concern/<int:id>')
@login_required
def concern(id):
    post = Post.query.get_or_404(id)
    is_concern = request.args.get('action')
    if is_concern == 'concern':
        if current_user.concern(post):
            flash(messages.concern_ok)
        else:
            flash(messages.concern_again_err)
    elif is_concern == 'unconcern':
        if current_user.unconcern(post):
            flash(messages.unconcern_ok)
        else:
            flash(messages.unconcern_again_err)
    else:
        pass
    return redirect(url_for('main.post', id=id))