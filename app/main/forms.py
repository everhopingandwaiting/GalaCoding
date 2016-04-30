# -*- coding:utf8 -*-
'''
Main Form.
'''
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError
from ..models import Post

class PostForm(Form):
    body = TextAreaField('有什么好的想法？', validators=[Required()])
    submit = SubmitField('提交')