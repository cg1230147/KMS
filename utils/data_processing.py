#!/usr/bin/env python
# -*- coding:utf-8
from kms_app import models

class Processing(object):
    def __init__(self):
        self.result = []
        self.deptName = str()

    def group_data_structure(self, data, temp_list=list()):
        for item in data:
            if item['superior_dept'] is None:
                temp = item
                temp_list.append(temp)
                self.result.append(temp)
                data.remove(item)
                return self.group_data_structure(data,temp_list)
            else:
                if temp_list:
                    for i in temp_list:
                        if item['superior_dept'] == i['id']:
                            temp = item
                            temp_list.append(temp)
                            i['nodes'].append(temp)
                            data.remove(item)
                            return self.group_data_structure(data,temp_list)
        del temp_list[:]     # 每次清空，否则下一次执行时，还会存在数据
        return self.result

    def group_data_join(self,data_id):
        queryResult = models.KmsGroup.objects.filter(id=data_id).values('dept_name', 'superior_dept')
        for i in queryResult:
            self.deptName = self.deptName + '/' + i['dept_name']
            return self.group_data_join(i['superior_dept'])
        return self.deptName

'''
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
'''

