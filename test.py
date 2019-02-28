#!/usr/bin/env python
# -*- coding:utf-8 -*-

class A:
    def __init__(self, name):
        self.name = name

class B(A):
    def __init__(self):
        super(B, self).__init__('name')
    def inner(self):
        print(self.name)

# obj = B()
# obj.inner()

n = [{'category': '华能移动办公', 'nodes': [
        {'id': 6, 'category': '华能移动办公', 'classify_name': '服务器问题'},
        {'id': 7, 'category': '华能移动办公', 'classify_name': '后台设置'}]},
     {'category': 'domino 8.0', 'nodes': [
         {'id': 5, 'category': 'domino 8.0', 'classify_name': '后台设置'},
         {'id': 11, 'category': 'domino 8.0', 'classify_name': '服务器问题'}]},
     {'category': 'domino 9.0', 'nodes': [
         {'id': 2, 'category': 'domino 9.0', 'classify_name': '服务器问题'},
         {'id': 3, 'category': 'domino 9.0', 'classify_name': '后台设置'}]},
     {'category': 'java 1.0', 'nodes': [
         {'id': 8, 'category': 'java 1.0', 'classify_name': '客户端问题'},
         {'id': 9, 'category': 'java 1.0', 'classify_name': '系统bug'}]}]

# for i in n:
#     print(i['category'])
#     for j in i['nodes']:
#         print(j['classify_name'])

import os
# print(os.path.dirname(__file__))
# print(os.path.abspath(__file__))
# print(os.path.join(os.path.dirname(__file__),'upload_files'))
# os.mkdir(os.path.join(os.path.join(os.path.dirname(__file__),'upload_files'), 'dirname'))

import uuid
print(uuid.NAMESPACE_DNS)
import re
# res = re.search(r'[^.\\/\w]+$', '1_完整版_软件项目开发计划书.doc')
# res = re.search(r'[^.\\/:*?"<>|\r\n]+$', '1_完整版_软件项目开发计划书.pdf')
res = re.search(r'[^\\.]+$', '.txt1_完整版_软件.doc项目开发计划书.xslx')

print(res)