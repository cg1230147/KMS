#!/usr/bin/env python
# -*- coding:utf-8 -*-
li = [
    {'id': 18, 'deptLevel__department_level': '顶级部门', 'superiorDept': None, 'name': '美络科技', 'nodes': []},
    {'id': 19, 'deptLevel__department_level': '一级部门', 'superiorDept': 18, 'name': '北京美络', 'nodes': []},
    {'id': 20, 'deptLevel__department_level': '一级部门', 'superiorDept': 18, 'name': '广州美络', 'nodes': []},
    {'id': 21, 'deptLevel__department_level': '二级部门', 'superiorDept': 19, 'name': '行政中心', 'nodes': []},
    {'id': 24, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '系统开发部', 'nodes': []},
    {'id': 25, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '移动开发中心', 'nodes': []},
    {'id': 28, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '行政中心', 'nodes': []},
    {'id': 22, 'deptLevel__department_level': '三级部门', 'superiorDept': 21, 'name': '人资部', 'nodes': []},
    {'id': 23, 'deptLevel__department_level': '三级部门', 'superiorDept': 21, 'name': '行政部', 'nodes': []},
    {'id': 26, 'deptLevel__department_level': '三级部门', 'superiorDept': 24, 'name': 'OA项目部', 'nodes': []},
    {'id': 27, 'deptLevel__department_level': '三级部门', 'superiorDept': 25, 'name': 'Android组', 'nodes': []},
    {'id': 29, 'deptLevel__department_level': '三级部门', 'superiorDept': 28, 'name': '人资部', 'nodes': []}]

class DataProcessing(object):
    def __init__(self,data, tempList=list()):
        self.data = data
        self.tempList = tempList
        self.result = []
    def dataProcessing(self):
        for item in self.data:
            if item['superiorDept'] is None:
                temp = item
                self.tempList.append(temp)
                self.result.append(temp)
                self.data.remove(item)
                return self.dataProcessing()
            else:
                if self.tempList:
                    for i in self.tempList:
                        if item['superiorDept'] == i['id']:
                            temp = item
                            self.tempList.append(temp)
                            i['nodes'].append(temp)
                            self.data.remove(item)
                            return self.dataProcessing()
        return self.result

obj = DataProcessing(li)
ret = obj.dataProcessing()
# print('result=', result)
print(ret)
# for k in result:
#     print(k)

json = {'id': 18, 'deptLevel__department_level': '顶级部门', 'superiorDept': None, 'name': '美络科技', 'nodes': [
    {'id': 19, 'deptLevel__department_level': '一级部门', 'superiorDept': 18, 'name': '北京美络', 'nodes': [
        {'id': 21, 'deptLevel__department_level': '二级部门', 'superiorDept': 19, 'name': '行政中心', 'nodes': [
            {'id': 22, 'deptLevel__department_level': '三级部门', 'superiorDept': 21, 'name': '人资部', 'nodes': []},
            {'id': 23, 'deptLevel__department_level': '三级部门', 'superiorDept': 21, 'name': '行政部', 'nodes': []}
        ]}
    ]},
    {'id': 20, 'deptLevel__department_level': '一级部门', 'superiorDept': 18, 'name': '广州美络', 'nodes': [
        {'id': 24, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '系统开发部', 'nodes': [
            {'id': 26, 'deptLevel__department_level': '三级部门', 'superiorDept': 24, 'name': 'OA项目部', 'nodes': []}
        ]},
        {'id': 25, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '移动开发中心', 'nodes': [
            {'id': 27, 'deptLevel__department_level': '三级部门', 'superiorDept': 25, 'name': 'Android组', 'nodes': []}
        ]},
        {'id': 28, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '行政中心', 'nodes': [
            {'id': 29, 'deptLevel__department_level': '三级部门', 'superiorDept': 28, 'name': '人资部', 'nodes': []}
        ]}
    ]}
]}

d = [{'id': 18, 'deptLevel__department_level': '顶级部门', 'superiorDept': None, 'name': '美络科技', 'nodes': [
    {'id': 19, 'deptLevel__department_level': '一级部门', 'superiorDept': 18, 'name': '北京美络', 'nodes': [
        {'id': 21, 'deptLevel__department_level': '二级部门', 'superiorDept': 19, 'name': '行政中心', 'nodes': [
            {'id': 22, 'deptLevel__department_level': '三级部门', 'superiorDept': 21, 'name': '人资部', 'nodes': []},
            {'id': 23, 'deptLevel__department_level': '三级部门', 'superiorDept': 21, 'name': '行政部', 'nodes': []}]}]},
    {'id': 20, 'deptLevel__department_level': '一级部门', 'superiorDept': 18, 'name': '广州美络', 'nodes': [
        {'id': 24, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '系统开发部', 'nodes': [
            {'id': 26, 'deptLevel__department_level': '三级部门', 'superiorDept': 24, 'name': 'OA项目部', 'nodes': []}]},
        {'id': 25, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '移动开发中心', 'nodes': [
            {'id': 27, 'deptLevel__department_level': '三级部门', 'superiorDept': 25, 'name': 'Android组', 'nodes': []}]},
        {'id': 28, 'deptLevel__department_level': '二级部门', 'superiorDept': 20, 'name': '行政中心', 'nodes': [
            {'id': 29, 'deptLevel__department_level': '三级部门', 'superiorDept': 28, 'name': '人资部', 'nodes': []}]}]}]}]


