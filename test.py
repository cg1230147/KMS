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
pp = '/upload_files/001fa4d8-39a8-11e9-ae43-3c970e58089b/2._华能集团新建二级单位邮件地址簿系统部署步骤（v1.0）.docx'
path = os.path.dirname(__file__)
# print(path,pp)
# print(os.path.join(path,pp))
# os.mkdir(os.path.join(os.path.join(os.path.dirname(__file__),'upload_files'), 'dirname'))

import uuid
# print(uuid.NAMESPACE_DNS)
import re
# res = re.search(r'[^.\\/\w]+$', '1_完整版_软件项目开发计划书.doc')
# res = re.search(r'[^.\\/:*?"<>|\r\n]+$', '1_完整版_软件项目开发计划书.pdf')
res = re.sub(r'^/','', pp,1)

print(res)

import shutil

# shutil.rmtree('F:\新建文件夹')

# os.makedirs('f:/111/222')
# dir = os.path.join(
#         os.path.join(
#             os.path.join(
#                 os.path.dirname(os.path.dirname(__file__)), 'upload_files'), str('asdaskjhuh12hhud')),'attachment')
# print(dir)
"""
class T(object):
    __instance = None
    def __new__(cls, *args, **kwargs):
        print(cls.__instance,cls,object)
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            return cls.__instance

s = T()
print(id(s))
a = T()
print(id(a))
"""

li = [{'id': 16, 'nav_name': '待审核文档'}, {'id': 17, 'nav_name': '已审核文档'}, {'id': 18, 'nav_name': '已退回'}, {'id': 7, 'nav_name': '全部文档'}, {'id': 12, 'nav_name': '待提交文档'}, {'id': 13, 'nav_name': '已提交文档'}, {'id': 14, 'nav_name': '已发布文档'}, {'id': 15, 'nav_name': '审核失败'}]

"""
for i in range(len(li)):
    # print(i)
    for j in range(i+1,len(li)):
        if li[i]['id'] > li[j]['id']:
            li[i],li[j] = li[j],li[i]

print(li)
"""

import os

os.chdir(os.path.dirname(__file__))
os.system('python manage.py clearsessions')