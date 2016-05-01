# -*- coding:utf8 -*-
'''
Main Form.
'''
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError
from ..models import Post
from flask.ext.pagedown.fields import PageDownField

class PostForm(Form):
    body = PageDownField('有什么好的想法？', validators=[Required()])
    submit = SubmitField('提交')