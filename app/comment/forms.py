# -*- coding:utf8 -*-
'''
User Form.
'''
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User, Role
from flask.ext.pagedown.fields import PageDownField

class CommentForm(Form):
    comment = PageDownField('记录你的声音', validators=[Required()])
    submit = SubmitField('提交')
