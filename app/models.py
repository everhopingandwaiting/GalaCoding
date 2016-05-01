# -*- coding:utf8 -*-
'''
Add database models.
'''
from . import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from datetime import datetime
import hashlib
from markdown import markdown
import bleach

# 使用flask-login模块自动加载用户信息
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 模型字典，用于向外展示数据库模型
tables = {}

# 动态更新模型字典的修饰器
# 不需要改变类或者函数的行为，在一些处理以后，直接返回好了，不要包装函数了
def addModel(model):
    tables[model.__name__] = model
    return model

# USer model
@addModel
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 每个用户的email是唯一的，只能通过数据库删，否则终身不变
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # 文章的反向引用
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 用户图像，存储用户头像的url，而非二进制格式
    avatar_url = db.Column(db.String(100), unique=True, index=True)
    # 更新用户登录时间
    def ping(self):
        self.last_seen = self.member_since
        self.member_since = datetime.utcnow()
        db.session.add(self)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 存储密码的散列值，不存储用户密码，为了保护用户密码的隐私性
    password_hash = db.Column(db.String(64))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 邮箱验证是否有效
    confirmed = db.Column(db.Boolean, default=False)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    @staticmethod
    def parse_confirm_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return data.get('confirm')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 添加权限验证
    def can(self, permissions):
        return self.role is not None and (self.role.permission & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # 生成avatar的hashurl，使用http://www.gravatar.com/avatar的生成头像的服务
    # 计算md5是计算密集型，会占用大量cpu，一般初始化新用户时，会执行一次
    def generate_avatar_url(self):
        # self.avatar_url = 'https://www.gravatar.com/avatar/'+hashlib.md5(self.email.encode('utf-8')).hexdigest()
        total = 0
        for i in range(1, len(self.email)):
            total = total + ord(self.email[i])
        self.avatar_url = '/static/avatar/avatar{0}.png'.format(total%200)

    # 生成不同尺寸的url，这时经常被调用
    def avatar_url_auto(self, size=100, default='idention', rating='g'):
        # return '{0}?s={1}&d={2}&r={3}'.format(self.avatar_url, size, default, rating)
        return self.avatar_url

    def __repr__(self):
        return '<User %r>' % self.username

# 为了保证一致性，添加一个匿名用户
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

# 向flask-login管理添加默认的匿名类
login_manager.anonymous_user = AnonymousUser

# 使用权限来管理角色，同时通过一对多的关系，来对应相应用户
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

# 角色数据库，用于分配权限
@addModel
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)
    users = db.RelationshipProperty('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name = role_name)
            role.permission = roles[role_name][0]
            role.default = roles[role_name][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

@addModel
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 富文本
    body_html = db.Column(db.Text)

    # 富文本转化
    @staticmethod
    def on_chaged_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
                        markdown(value, output_format='html'),
                        tags=allowed_tags, strip=True))

# 绑定SQLAlchemy的事件监听
db.event.listen(Post.body, 'set', Post.on_chaged_body)