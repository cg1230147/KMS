#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
from django import forms
from kms_app import models
from django.core.exceptions import ValidationError

class CustomValidators(object):
    @staticmethod
    def phone_validate(value):
        phone_re = re.compile(r'^[1][345678][\d]{9}$')
        if not phone_re.match(value):
            raise ValidationError('手机号格式错误')
    @staticmethod
    def username_validate(value):
        whetherExists = models.KmsUser.objects.filter(username=value)
        if whetherExists:
            raise forms.ValidationError('用户名已存在,请修改用户名')

class RegisterForm(forms.Form):
    def __init__(self,data, url=None):
        super(RegisterForm, self).__init__(data)
        self.url = url

    # username = forms.CharField(validators=[CustomValidators.username_validate],
    #                            error_messages={'required': '用户名不能为空',
    #                                            'max_length': '用户名长度应为4-16个字符',
    #                                            'min_length': '用户名长度应为4-16个字符'}, max_length=16, min_length=4)
    username = forms.CharField()
    showUsername = forms.CharField(error_messages={'required': '显示名称不能为空'})
    password = forms.CharField(error_messages={'required': '密码不能为空'})
    email = forms.EmailField(error_messages={'invalid': '邮箱格式错误'},required=False)
    phone = forms.CharField(validators=[CustomValidators.phone_validate],required=False)
    regDepartment = forms.CharField(error_messages={'required': '部门不能为空'})

    def clean_username(self):
        value = self.cleaned_data['username']
        max_length = 16
        min_length = 4
        if self.url == '/edit/':
            if len(value) > max_length or len(value) < min_length:
                raise forms.ValidationError('用户名长度应为4-16个字符')
            elif len(value) == 0:
                raise forms.ValidationError('用户名不能为空')
        else:
            whetherExists = models.KmsUser.objects.filter(username=value)
            if whetherExists:
                raise forms.ValidationError('用户名已存在,请修改用户名')
            elif len(value) > max_length or len(value) < min_length:
                raise forms.ValidationError('用户名长度应为4-16个字符')
            elif len(value) == 0:
                raise forms.ValidationError('用户名不能为空')
        return value




