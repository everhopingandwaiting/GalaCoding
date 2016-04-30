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
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # 文章的反向引用
    posts = db.relationship('Post', backref='author', lazy='dynamic')

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