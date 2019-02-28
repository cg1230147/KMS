#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render,HttpResponse,redirect

class LoginMD(MiddlewareMixin):

    def process_request(self, request):
        # 中间件验证登陆，请求登陆之外的页面且没有session或过期的跳转到登陆页面
        if request.path != '/login/' and request.path != '/':
            username = request.session.get('username')
            if not username:
                return render(request, 'login.html', {'message': ''})
            elif request.path == '/manage/':
                permission = request.session.get('permission')
                if '管理员' not in permission:
                    return HttpResponse('<script>alert("您无权访问此模块！")</script>')

    def process_response(self, request, response):
        return response