#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import os
from kms_app import models


FILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files')

class ViewAtt(object):
    __instance = None
    def __init__(self,doc_uuid, current_doc):
        self.doc_uuid = doc_uuid
        self.current_doc = current_doc

    def view_att(self):
        path_obj = models.KmsFilePath.objects.filter(uuid=self.doc_uuid ).values('path', 'name')
        self.current_doc.update({'initialPreview': [], 'initialPreviewConfig': []})
        for dict_path in path_obj:
            # print(dict_path)
            file_type = re.search(r'[^.]+\w$', dict_path['path']).group()
            img_list = ['jpg', 'jpeg', 'jpe', 'gif', 'png', 'pns', 'bmp', 'png', 'tif']
            pdf_list = ['pdf']
            text_list = ['txt', 'md', 'csv', 'info', 'ini', 'json', 'php', 'js', 'css']

            # bootstrap fileinput 预览参数，initialPreview，initialPreviewConfig
            file_dir = os.path.join(os.path.join(os.path.join(FILE_DIR, self.doc_uuid ),'attachment'), dict_path['name'])
            if file_type in img_list:
                self.current_doc['initialPreview'].append(
                    "<img src='" + dict_path['path'] + "' class='file-preview-image' style='max-width:100%;max-height:100%;'>")
            elif file_type in pdf_list:
                self.current_doc['initialPreview'].append(
                    "<div class='file-preview-frame'><div class='kv-file-content'><embed class='kv-preview-data file-preview-pdf' src='" +
                    dict_path['path'] +
                    "' type='application/pdf' style='width:100%;height:160px;'></div></div>")
            elif file_type in text_list:
                f = open(file_dir)
                self.current_doc['initialPreview'].append(
                    "<div class='kv-file-content'><textarea class='kv-preview-data file-preview-text' title='" +
                    dict_path['name'] +
                    "' readonly style='width:213px;height:160px;'>" + f.read() + "</textarea></div>"
                )
                f.close()
            else:
                self.current_doc['initialPreview'].append(
                    "<div class='file-preview-other'><span class='file-other-icon'><i class='glyphicon glyphicon-file'></i></span></div>")

            initialPreviewDict = {
                'caption': dict_path['name'],
                'type': file_type,
                'downloadUrl': dict_path['path'],
                'url': '/del_doc_file/',
                'size': os.path.getsize(file_dir),
                'extra': {'doc_uuid': self.doc_uuid },  # 删除文件携带的参数
                'key': dict_path['name'],
            }
            self.current_doc['initialPreviewConfig'].append(initialPreviewDict)
        return self.current_doc
    
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            return cls.__instance
        