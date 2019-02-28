#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib

class Md5(object):
    def __init__(self,password):
        self.password = password

    def md5_password(self):
        salt = 'knowledge_base_management_system_app'   # 加盐
        md5pwd = hashlib.md5(salt.encode('utf-8'))
        md5pwd.update(self.password.encode('utf-8'))
        return md5pwd.hexdigest()