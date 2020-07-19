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

