# Create your views here.
from django.shortcuts import render, HttpResponse, redirect, render_to_response, reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.db.models import Q, F
from kms_app import models
from kms_app import form
from KMS import settings
from utils import data_processing
from utils import MD5_encryption
from utils import view_attachment
from utils import custom_paginator
import json
import hashlib
import time
import os
import uuid
import re
import shutil

PANEL_USER = 'panel-user'
PANEL_DEPARTMENT = 'panel-department'
PANEL_DEPT_LEVEL = 'panel-dept-level'
PANEL_PERMISSION = 'panel-permission'
PANEL_KNOWLEDGE = 'panel-knowledge'
PANEL_HOMEPAGE = 'panel-homepage'

""" 文档状态 """
SAVE = '保存'
EXAMINE = '审核'
RELEASE = '发布'
SEND_BACK = '退回'

FILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files')


def login(request):
    """登陆页"""
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        md5_obj = MD5_encryption.Md5(password)
        md5_pwd = md5_obj.md5_password()
        try:
            # 查询用户名和密码是否匹配。 django orm 的 get 方法如果获取不到数据会报错
            login_user = models.KmsUser.objects.get(username=username, password=md5_pwd)
        except Exception as e:
            login_user = None

        if login_user:
            # 多对多查询当前用户的权限
            permission = login_user.kmsuserpermissions_set.all().values()

            permission_list = list()
            for i in permission:
                permission_list.append(i['name'])
            request.session['is_login'] = True
            request.session['username'] = username
            request.session['show_name'] = login_user.show_name
            request.session['permission'] = permission_list
            return redirect('/index/')
        else:
            # return HttpResponse(json.dumps({'status': False, 'message': '用户名或密码错误请重新输入'}))
            return render(request, 'login.html', {'message': '用户名或密码错误请重新输入'})
    else:
        return render(request, 'login.html', {'message': ''})


def index(request):
    """主页"""
    show_name = request.session['show_name']
    permission = request.session['permission']
    if permission:
        homepage_nav = list()
        # 根据当前用户权限遍历所有能查看的内容
        for i in permission:
            per_id = models.KmsUserPermissions.objects.filter(name=i).values('id')
            homepage = models.KmsHomePageSettings.objects.filter(Q(view_permissions_id=per_id[0]['id'])).values('id',
                                                                                                                'nav_name').order_by(
                'id')
            for j in homepage:
                homepage_nav.append(j)
        # 对查看内容列表冒泡排序
        count = len(homepage_nav)
        for first in range(count):
            for second in range(first + 1, count):
                if homepage_nav[first]['id'] > homepage_nav[second]['id']:
                    homepage_nav[first], homepage_nav[second] = homepage_nav[second], homepage_nav[first]
    else:
        homepage_nav = models.KmsHomePageSettings.objects.filter(view_permissions_id=None).values('id',
                                                                                                  'nav_name').order_by(
            'id')

    return render(request, 'index.html',
                  {'show_name': show_name, 'permission': permission, 'homepage_nav': homepage_nav})


def query_index_data(request):
    nav_id = request.POST.get('navId', None)
    nav_name = request.POST.get('navName', None)
    condition = models.KmsHomePageSettings.objects.filter(id=nav_id, nav_name=nav_name).values('nav_name','view_permissions__name',
                                                                                               'filter_conditions')
    condition_dict = json.loads(condition[0]['filter_conditions'])
    if nav_name == '全部文档':
        query_set = models.KmsDocInfo.objects.filter(Q(del_status=condition_dict['del_status']) &
                                                     Q(doc_status=condition_dict['doc_status'])).values().order_by('-release_date')
    elif condition[0]['view_permissions__name'] == '审核员':
        query_set = models.KmsDocInfo.objects.filter(Q(del_status=condition_dict['del_status']) &
                                                     Q(doc_status=condition_dict['doc_status']) &
                                                     Q(auditor_account=request.session['username'])).values().order_by('-release_date')
    else:
        query_set = models.KmsDocInfo.objects.filter(Q(del_status=condition_dict['del_status']) &
                                                     Q(doc_status=condition_dict['doc_status']) &
                                                     Q(issuer_account=request.session['username'])).values().order_by('-release_date')

    for i in query_set:
        i['release_date'] = str(i['release_date'])
    # print(query_set.query)
    # print(query_set)
    """
    sql = "SELECT `id`, `uuid`, `title`, `issuer`, `issuer_dept`, `classify_name`, `release_date`, `auditor`, `remarks`, " \
          "`issue_type`, `del_status`, `doc_status`, `details`, `describe`, `solution`, `return_reason` " \
          "FROM `kms_app_kmsdocinfo`"
    """
    # 首页左侧菜单查询对应条件
    # models.KmsDocInfo.objects.filter(del_status=0,doc_status='发布',issuer_account=request.session['username']).values()
    """
    query_conditions = {
        '全部文档': sql + 'WHERE del_status = 0 AND doc_status = "发布"',
        '待提交文档': sql + 'WHERE del_status = 0 AND doc_status = "保存" AND issuer_account = "' + request.session[
            'username'] + '"',
        '已提交文档': sql + 'WHERE del_status = 0 AND doc_status = "审核" AND issuer_account = "' + request.session[
            'username'] + '"',
        '已发布文档': sql + 'WHERE del_status = 0 AND doc_status = "发布" AND issuer_account = "' + request.session[
            'username'] + '"',
        '审核失败': sql + 'WHERE del_status = 0 AND doc_status = "退回" AND issuer_account = "' + request.session[
            'username'] + '"',
        '待审核文档': sql + 'WHERE del_status = 0 AND doc_status = "审核" AND auditor_account = "' + request.session[
            'username'] + '"',
        '已审核文档': sql + 'WHERE del_status = 0 AND doc_status = "发布" AND auditor_account = "' + request.session[
            'username'] + '"',
        '已退回': sql + 'WHERE del_status = 0 AND doc_status = "退回" AND auditor_account = "' + request.session[
            'username'] + '"',
    }
    """
    # cursor = connection.cursor()
    # cursor.execute(sql)
    # raw_query_set = models.KmsDocInfo.objects.raw(query_conditions[nav_name])  # 原生sql查询

    # doc_info_list = list()
    # for obj in raw_query_set:
        # 循环查询的RawQuerySet对象，将结果添加到doc_info_list列表中，用于分页使用
        # doc_info_list.append(obj)

    # number = 16
    # pag = Paginator(query_set, number)  # 定义分页器，每页显示16条
    page = request.POST.get('page', None)  # 从前端获取当前的页码数
    """
    try:
        # 当前页。转换为int类型,出现异常赋值为1
        current_page = int(page)
        # print(current_page)
    except:
        current_page = 1

    try:
        # 获取分页对象
        page_obj = pag.page(current_page)
    except PageNotAnInteger:
        page_obj = pag.page(1)
    except EmptyPage:
        page_obj = pag.page(pag.num_pages)

    has_per_page = page_obj.has_previous()  # 当前页是否有上一页
    if has_per_page:
        per_page_number = page_obj.previous_page_number()  # 上一页页码
    else:
        per_page_number = None

    # total_page = [page for page in pag.page_range] # 总页数列表
    # print(pag.page_range.start,pag.page_range.stop,len(pag.page_range))
    # 控制页面上面只展示5页
    if len(pag.page_range) < 5:
        s, e = 1, len(pag.page_range)
    elif current_page - 5 < 1:
        s, e = 1, 5
    elif current_page + 5 > len(pag.page_range):
        s, e = len(pag.page_range) - 4, len(pag.page_range)
    else:
        s, e = current_page - 2, current_page + 2

    # 当前显示的页码
    curr_show_pages = [i for i in range(s, e + 1)]

    has_next_page = page_obj.has_next()  # 当前页是否有下一页
    if has_next_page:
        next_page_number = page_obj.next_page_number()  # 下一页页码
    else:
        next_page_number = None

    paging_param = {'has_per_page': has_per_page, 'per_page_number': per_page_number, 'total_page': len(pag.page_range),
                    'has_next_page': has_next_page, 'next_page_number': next_page_number, 'current_page': current_page,
                    'curr_show_pages': curr_show_pages}
 
    result_list = list()  # json返回的数据列表
    for i in page_obj:
        temp_dict = dict()
        temp_dict['uuid'] = i.uuid
        temp_dict['title'] = i.title
        temp_dict['issuer'] = i.issuer
        temp_dict['classify_name'] = i.classify_name
        temp_dict['issuer_dept'] = i.issuer_dept
        temp_dict['auditor'] = i.auditor
        temp_dict['release_date'] = str(i.release_date)
        temp_dict['doc_status'] = i.doc_status
        result_list.append(temp_dict)
    """
    pag_obj = custom_paginator.CustomPaginator(query_set, page)
    paging_param, data_set = pag_obj.paginator()
    return HttpResponse(json.dumps({'status': True, 'result_list': data_set, 'paging_param': paging_param}))


def classify(request):
    """分类页"""
    if request.method == 'GET':
        show_name = request.session['show_name']
        permission = request.session['permission']

        query_result = models.KmsKnowledgeClassify.objects.all().values('id', 'category', 'classify_name').order_by(
            'id')

        category_list = list()  # 类别列表
        classify_list = list()  # 处理结果列表
        for i in query_result:  # 获取所有类别
            category_list.append(i['category'])

        for j in list(set(category_list)):  # 通过set去除重复
            pro_data = {'category': None, 'nodes': []}
            for k in query_result:
                if j == k['category']:
                    pro_data['category'] = j
                    pro_data['nodes'].append(k)
            classify_list.append(pro_data)
        # lam = lambda category: category.get('category')
        # for i in classify_list:
        #     print(lam(i))
        # 对分类用名称排序，lambda中 category 为classify_list中的每个元素
        classify_list.sort(key=lambda category: category.get('category'))
        return render(request, 'classify.html',
                      {'show_name': show_name, 'permission': permission, 'classify_list': classify_list})
    elif request.method == 'POST':
        # 获取分类数据
        classify_name = request.POST.get('classifyName', None)
        query_set = models.KmsDocInfo.objects.filter(classify_name=classify_name, doc_status='发布').values().order_by('-release_date')
        for i in query_set:
            i['release_date'] = str(i['release_date'])
        # print(query_set)
        page = request.POST.get('page', None)  # 从前端获取当前的页码数
        pag_obj = custom_paginator.CustomPaginator(query_set, page)
        paging_param, data_set = pag_obj.paginator()
        """
        number = 16
        pag = Paginator(list(query_set), number)  # 定义分页器，每页显示16条
        page = request.POST.get('page', None)  # 从前端获取当前的页码数

        try:
            # 当前页。转换为int类型,出现异常赋值为1
            current_page = int(page)
        except:
            current_page = 1

        try:
            # 获取分页对象
            page_obj = pag.page(current_page)
        except PageNotAnInteger:
            page_obj = pag.page(1)
        except EmptyPage:
            page_obj = pag.page(pag.num_pages)

        has_per_page = page_obj.has_previous()  # 当前页是否有上一页
        if has_per_page:
            per_page_number = page_obj.previous_page_number()  # 上一页页码
        else:
            per_page_number = None

        # total_page = [page for page in pag.page_range] # 总页数列表
        # print(pag.page_range.start,pag.page_range.stop,len(pag.page_range))
        # 控制页面上面只展示5页
        if len(pag.page_range) < 5:
            s, e = 1, len(pag.page_range)
        elif current_page - 5 < 1:
            s, e = 1, 5
        elif current_page + 5 > len(pag.page_range):
            s, e = len(pag.page_range) - 4, len(pag.page_range)
        else:
            s, e = current_page - 2, current_page + 2

        # 当前显示的页码
        curr_show_pages = [i for i in range(s, e + 1)]

        has_next_page = page_obj.has_next()  # 当前页是否有下一页
        if has_next_page:
            next_page_number = page_obj.next_page_number()  # 下一页页码
        else:
            next_page_number = None

        paging_param = {'has_per_page': has_per_page, 'per_page_number': per_page_number,'total_page': len(pag.page_range),
                        'has_next_page': has_next_page, 'next_page_number': next_page_number,'current_page': current_page,
                        'curr_show_pages': curr_show_pages }
        """
        return HttpResponse(json.dumps({'status': True, 'query_data': data_set, 'paging_param': paging_param}))


def search(request):
    search_condition = request.POST.get('searchCondition', None)
    search_category = request.POST.get('searchCategory', None)
    # c = {search_category: search_condition}
    # qs = models.KmsDocInfo.objects.filter(**{search_category: search_condition}).values().order_by('-release_date')

    if search_category == 'fuzzy_search':
        query_set = models.KmsDocInfo.objects.filter(Q(title__contains=search_condition) |
                                                     Q(issuer__contains=search_condition) |
                                                     Q(auditor__contains=search_condition) |
                                                     Q(issuer_dept__contains=search_condition) |
                                                     Q(classify_name__contains=search_condition) |
                                                     Q(release_date__contains=search_condition) |
                                                     Q(issue_type__contains=search_condition) |
                                                     Q(subject__contains=search_condition) |
                                                     Q(remarks__contains=search_condition) |
                                                     Q(details__contains=search_condition) |
                                                     Q(describe__contains=search_condition) |
                                                     Q(solution__contains=search_condition)).values().order_by('-release_date')
    else:
        query_set = models.KmsDocInfo.objects.filter(**{search_category: search_condition}).values().order_by('-release_date')

    for i in query_set:
        i['release_date'] = str(i['release_date'])
    page = request.POST.get('page', None)  # 从前端获取当前的页码数
    pag_obj = custom_paginator.CustomPaginator(query_set, page)
    paging_param, data_set = pag_obj.paginator()

    return HttpResponse(json.dumps({'status': True, 'query_data': data_set, 'paging_param': paging_param}))


def release(request):
    """发布页"""
    if request.method == "GET":
        username = request.session['username']  # 当前登陆用户
        show_name = request.session['show_name']
        current_time = time.strftime('%Y-%m-%d')  # 当前时间
        doc_uuid = request.GET.get('doc_uuid', None)  # 获取当前文件的uuid

        # 获取当前用户所在部门的id
        group = models.KmsUser.objects.filter(username=username).values('groups__id', 'groups__dept_name')
        # 获取部门内的所有人
        all_people = models.KmsUser.objects.filter(groups_id=group[0]['groups__id']).values('uid', 'username',
                                                                                            'show_name')
        permission_name = models.KmsUserPermissions.objects.get(name='审核员')
        auditor_list = list()
        # 查询当前部门下具有 审核员 权限的人
        for i in all_people:
            auditor_dict = dict()
            auditor = permission_name.kms_user.filter(uid=i['uid']).values()
            if auditor:
                auditor_dict['show_name'] = auditor[0]['show_name']
                auditor_dict['username'] = auditor[0]['username']
                auditor_list.append(auditor_dict)

        # 分类数据处理
        query_result = models.KmsKnowledgeClassify.objects.all().values('id', 'category', 'classify_name').order_by(
            'id')
        category_list = list()  # 类别列表
        result_list = list()  # 处理结果列表
        for i in query_result:  # 获取所有类别
            category_list.append(i['category'])
        for j in list(set(category_list)):  # 通过set去除重复
            pro_data = {'category': None, 'nodes': []}
            for k in query_result:
                if j == k['category']:
                    pro_data['category'] = j
                    pro_data['nodes'].append(k)
            result_list.append(pro_data)
        # 用uuid查询当前文档是否存在数据库中
        current_doc = models.KmsDocInfo.objects.filter(uuid=doc_uuid).values()
        # 新增文件 doc_status 为空
        try:
            if current_doc[0]:
                current_doc = current_doc[0]
                current_doc['release_date'] = str(current_doc['release_date'])
                doc_status = current_doc['doc_status']
        except Exception as e:
            final_doc = None
            doc_status = ''

        if not current_doc:
            # 不存在数据库中为新启文件
            if doc_uuid is None:
                doc_uuid = uuid.uuid1()  # 生成文档uuid，并以uuid创建文件存放目录
                os.makedirs(os.path.join(os.path.join(FILE_DIR, str(doc_uuid)), 'attachment'))
            else:
                if not os.path.exists(os.path.join(FILE_DIR, str(doc_uuid))):
                    os.makedirs(os.path.join(os.path.join(FILE_DIR, str(doc_uuid)), 'attachment'))
        else:
            va_obj = view_attachment.ViewAtt(doc_uuid, current_doc)
            final_doc = va_obj.view_att()

        return render(request, 'release.html',
                      {'show_name': show_name, 'current_time': current_time, 'auditor_list': auditor_list,
                       'dept_name': group[0]['groups__dept_name'], 'category_list': result_list,
                       'doc_uuid': doc_uuid, 'doc_status': doc_status, 'data': final_doc})


def media_upload(request):
    file = request.FILES.get('file')
    doc_uuid = request.POST.get('doc_uuid')
    # 拼接文件路径
    file_dir = os.path.join(os.path.join(FILE_DIR, str(doc_uuid)), file.name)

    # 写入文件
    f = open(file_dir, 'wb')
    for i in file.chunks():
        f.write(i)
    f.close()
    ret_url = list()  # 前端显示地址列表
    url = '{0}{1}{2}'.format(settings.MEDIA_URL, str(doc_uuid) + '/', file.name)  # 富文本框图片显示地址
    ret_url.append(url)

    return HttpResponse(json.dumps({'error': 0, 'url': ret_url, 'file_name': file.name}))


def attachment_upload(request):
    """
    上传附件
    :param request:
    :return:
    """
    att_file = request.FILES.get('attachment', None)
    doc_uuid = request.POST.get('doc_uuid', None)

    if att_file:
        # 保存文件
        file_dir = os.path.join(os.path.join(os.path.join(FILE_DIR, doc_uuid), 'attachment'), att_file.name)
        f = open(file_dir, 'wb')
        for i in att_file.chunks():
            f.write(i)
        f.close()
        # 下载和预览的url
        url = settings.MEDIA_URL + str(doc_uuid) + '/attachment/' + att_file.name

        # url = '{0}{1}{2}{3}{4}{5}'.format(FILE_DIR, str(doc_uuid), '/', 'attachment', att_file.name)
        file_type = re.search(r'[^.]+\w$', att_file.name).group()
        img_list = ['jpg', 'jpeg', 'jpe', 'gif', 'png', 'pns', 'bmp', 'png', 'tif']
        pdf_list = ['pdf']
        text_list = ['txt', 'md', 'csv', 'info', 'ini', 'json', 'php', 'js', 'css']
        # bootstrap fileinput 上传文件的回显参数，initialPreview，initialPreviewConfig
        initialPreview = []
        if file_type in img_list:
            initialPreview.append(
                "<img src='" + url + "' class='file-preview-image' style='max-width:100%;max-height:100%;'>")
        elif file_type in pdf_list:
            initialPreview.append(
                "<div class='file-preview-frame'><div class='kv-file-content'><embed class='kv-preview-data file-preview-pdf' src='" + url +
                "' type='application/pdf' style='width:100%;height:160px;'></div></div>")
        elif file_type in text_list:
            f = open(file_dir)
            initialPreview.append(
                "<div class='kv-file-content'><textarea class='kv-preview-data file-preview-text' title='" + att_file.name +
                "' readonly style='width:213px;height:160px;'>" + f.read() + "</textarea></div>")
            f.close()
        else:
            initialPreview.append(
                "<div class='file-preview-other'><span class='file-other-icon'><i class='glyphicon glyphicon-file'></i></span></div>")

        initialPreviewConfig = [{
            'caption': att_file.name,
            'type': file_type,
            'downloadUrl': url,
            'url': '/del_doc_file/',
            'size': os.path.getsize(file_dir),
            'extra': {'doc_uuid': doc_uuid},  # 删除文件携带的参数
            'key': att_file.name,
        }]
        return HttpResponse(json.dumps(
            {'initialPreview': initialPreview, 'initialPreviewConfig': initialPreviewConfig, 'append': True}))
    else:
        return HttpResponse(json.dumps({'status': False}))


def del_doc_file(request):
    """
    wangEditor控件 bootstarp fileinput控件 删除媒体内容或附件时同步删除服务器中的数据
    :param request:
    :return:
    """
    if request.method == 'POST':
        doc_uuid = request.POST.get('doc_uuid', None)
        file_name = request.POST.get('fileName', None)
        key = request.POST.get('key', None)
        models.KmsFilePath.objects.filter(uuid=doc_uuid, name=key).delete()
        temp_file_name = ''
        if file_name:
            temp_file_name = file_name
        elif key:
            temp_file_name = key

        file_dir = os.path.join(os.path.join(FILE_DIR, doc_uuid), temp_file_name)
        # 检查前端删除的文件是否存在，存在则删除
        if os.path.exists(file_dir):
            os.remove(file_dir)
        else:
            file_dir = os.path.join(os.path.join(os.path.join(FILE_DIR, doc_uuid), 'attachment'), temp_file_name)
            os.remove(file_dir)

    return HttpResponse(json.dumps({'status': True}))


def del_all_att(request):
    """ 批量删除附件 """
    doc_uuid = request.POST.get('doc_uuid', None)
    file_list = request.POST.getlist('aryFiles', None)

    for file_name in json.loads(file_list[0]):
        file_dir = os.path.join(os.path.join(os.path.join(FILE_DIR, doc_uuid), 'attachment'), file_name)
        models.KmsFilePath.objects.filter(uuid=doc_uuid, name=file_name).delete()
        if os.path.exists(file_dir):
            os.remove(file_dir)
    return HttpResponse(json.dumps({"status": True}))


def del_doc(request):
    """ 删除文档 """
    if request.method == 'POST':
        uuid_list = request.POST.getlist('uuidSet', None)
        for i in json.loads(uuid_list[0]):
            models.KmsDocInfo.objects.filter(uuid=i).delete()
            models.KmsFilePath.objects.filter(uuid=i).delete()
            try:
                shutil.rmtree(os.path.join(FILE_DIR, i))
            except FileNotFoundError as e:
                print(e)
    return HttpResponse(json.dumps({'status': True}))


def save_doc(request):
    operation = request.POST.get('operation', None)
    doc_uuid = request.POST.get('uuid', None)
    title = request.POST.get('title', None)
    classify_name = request.POST.get('classify', None)
    issuer = request.POST.get('issuer', None)
    release_date = request.POST.get('releaseDate', None)
    auditor = request.POST.get('auditor', None)
    auditor_account = request.POST.get('auditorAccount', None)
    issue_type = request.POST.get('issueType', None)
    issuer_dept = request.POST.get('issuerDept', None)
    subject = request.POST.get('subject', None)
    remarks = request.POST.get('remarks', None)
    details = request.POST.get('details1', None)
    describe = request.POST.get('describe1', None)
    solution = request.POST.get('solution1', None)
    list_url = request.POST.getlist('aryUrl', None)
    return_reason = request.POST.get('returnReason', None)
    username = request.session['username']
    # print(operation,doc_uuid,title,classify_name,issuer,release_date,auditor,auditor_account,issue_type,issuer_dept,
    #       remarks,details,describe,solution,list_url,return_reason)
    # print(username)
    # 如果数据库中不存在则创建，存在则更新
    if not models.KmsDocInfo.objects.filter(uuid=doc_uuid):
        if operation == 'save':
            obj = models.KmsDocInfo.objects.create(uuid=doc_uuid, title=title, classify_name=classify_name,
                                                   issuer=issuer, issuer_account=username, release_date=release_date,
                                                   auditor=auditor, auditor_account=auditor_account,
                                                   issue_type=issue_type, subject=subject, remarks=remarks,
                                                   issuer_dept=issuer_dept, details=details,
                                                   describe=describe, solution=solution, del_status=0, doc_status=SAVE)
        elif operation == 'submit':
            obj = models.KmsDocInfo.objects.create(uuid=doc_uuid, title=title, classify_name=classify_name,
                                                   issuer=issuer, issuer_account=username, release_date=release_date,
                                                   auditor=auditor, auditor_account=auditor_account,
                                                   issue_type=issue_type, subject=subject, remarks=remarks,
                                                   issuer_dept=issuer_dept, details=details,
                                                   describe=describe, solution=solution, del_status=0,
                                                   doc_status=EXAMINE)
    else:
        if operation == 'save':
            obj = models.KmsDocInfo.objects.filter(uuid=doc_uuid)
            obj.update(uuid=doc_uuid, title=title, classify_name=classify_name, issuer=issuer, issuer_account=username,
                       release_date=release_date, auditor=auditor, auditor_account=auditor_account,
                       issue_type=issue_type,
                       remarks=remarks, issuer_dept=issuer_dept, details=details, describe=describe, solution=solution,
                       del_status=0, doc_status=SAVE, return_reason=return_reason, subject=subject)
            obj = obj[0]  # 获取KmsDocInfo对象
        elif operation == 'submit':
            obj = models.KmsDocInfo.objects.filter(uuid=doc_uuid)
            obj.update(uuid=doc_uuid, title=title, classify_name=classify_name, issuer=issuer, issuer_account=username,
                       release_date=release_date, auditor=auditor, auditor_account=auditor_account,
                       issue_type=issue_type,
                       remarks=remarks, issuer_dept=issuer_dept, details=details, describe=describe, solution=solution,
                       del_status=0, return_reason=return_reason, subject=subject, doc_status=EXAMINE)
            obj = obj[0]
        elif operation == 'release':
            obj = models.KmsDocInfo.objects.filter(uuid=doc_uuid)
            obj.update(uuid=doc_uuid, title=title, classify_name=classify_name, issuer=issuer, issuer_account=username,
                       release_date=release_date, auditor=auditor, auditor_account=auditor_account,
                       issue_type=issue_type,
                       remarks=remarks, issuer_dept=issuer_dept, details=details, describe=describe, solution=solution,
                       del_status=0, return_reason=return_reason, subject=subject, doc_status=RELEASE)
            obj = obj[0]
        elif operation == 'send_back':
            obj = models.KmsDocInfo.objects.filter(uuid=doc_uuid)
            obj.update(return_reason=return_reason, doc_status=SEND_BACK)
            print(obj)
            obj = obj[0]
            # obj = obj[0]
    # 更新附件信息
    for dict_url in json.loads(list_url[0]):
        if not models.KmsFilePath.objects.filter(uuid=doc_uuid, name=dict_url['name']):
            models.KmsFilePath.objects.create(doc_info_id=obj.id, uuid=doc_uuid, path=dict_url['url'],
                                              name=dict_url['name'])

    return HttpResponse(json.dumps({'status': True}))


def view_form(request):
    """ 文件查看 """
    doc_uuid = request.GET.get('doc_uuid', None)

    if doc_uuid:
        doc_obj = models.KmsDocInfo.objects.filter(uuid=doc_uuid).values()
        current_doc = doc_obj[0]
        current_doc['release_date'] = str(current_doc['release_date'])
        va_obj = view_attachment.ViewAtt(doc_uuid, current_doc)
        final_doc = va_obj.view_att()
        return render(request, 'view_form.html', {'data': final_doc})


def center(request):
    """个人中心"""
    show_name = request.session['show_name']
    permission = request.session['permission']
    return render(request, 'center.html', {'show_name': show_name, 'permission': permission})


def user_info(request):
    username = request.session['username']
    if request.method == 'GET':
        handle = request.GET.get('handle')
        query_data = list()
        if handle == 'personal-info':
            query_set = models.KmsUser.objects.filter(username=username).values('email', 'phone_number')
            query_data.append(query_set[0])

        return HttpResponse(json.dumps({'status': True, 'query_data': query_data}))
    if request.method == 'POST':
        handle = request.POST.get('handle')
        if handle == 'personal-info':
            # 修改个人信息
            email = request.POST.get('email', None)
            phone_number = request.POST.get('phoneNumber', None)
            models.KmsUser.objects.filter(username=username).update(email=email, phone_number=phone_number)
        elif handle == 'change-pwd':
            # 修改密码
            old_password = request.POST.get('oldPassword', None)
            new_password = request.POST.get('newPassword', None)
            md5_obj_old = MD5_encryption.Md5(old_password)  # 加密旧密码
            old_md5_pwd = md5_obj_old.md5_password()
            valid_pwd = models.KmsUser.objects.filter(username=username, password=old_md5_pwd)  # 验证旧密码
            if valid_pwd:
                md5_obj_new = MD5_encryption.Md5(new_password)  # 加密新密码
                new_md5_pwd = md5_obj_new.md5_password()
                models.KmsUser.objects.filter(username=username, password=old_md5_pwd).update(password=new_md5_pwd)
            else:
                return HttpResponse(json.dumps({'status': False}))

        return HttpResponse(json.dumps({'status': True}))


def logout(request):
    # 删除当前用户所有session数据
    request.session.delete(request.session.session_key)
    return redirect('/login/')


# manage
def manage(request):
    """后台管理"""
    show_name = request.session['show_name']
    permission = request.session['permission']
    return render(request, 'manage.html', {'show_name': show_name, 'permission': permission})


def query(request):
    if request.method == 'POST':
        handle = request.POST.get('handle', None)
        if handle == PANEL_USER:
            """ 查询所有用户 """
            query_result = models.KmsUser.objects.all().values('uid', 'username', 'password', 'show_name', 'email',
                                                               'phone_number', 'groups__dept_name', 'groups__id').order_by('username')

            result_list = list()
            for user_item in query_result:
                user_item.update({'permissionsID': [], 'permissions': []})
                user_obj = models.KmsUser.objects.get(uid=user_item['uid'])
                for i in user_obj.kmsuserpermissions_set.all().values():  # 查询多对多用户权限
                    user_item['permissionsID'].append(i['id'])
                    user_item['permissions'].append(i['name'])
                result_list.append(user_item)
            # 将所有结果为null的字段转换为空字符串
            for i in result_list:
                for j in i:
                    i[j] = "" if i[j] is None else i[j]

            page = request.POST.get('page', None)  # 从前端获取当前的页码数
            pag_obj = custom_paginator.CustomPaginator(result_list, page, 5, 16)
            paging_param, data_set = pag_obj.paginator()

            return_data = {'status': True, 'query_data': data_set, 'paging_param': paging_param}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_DEPARTMENT:
            """ 查询所有群组 """
            result_list = list()
            query_group = models.KmsGroup.objects.all().annotate(name=F('dept_name')).values('id', 'name',
                                                                                             'dept_level__department_level',
                                                                                             'superior_dept')
            for dept_item in query_group:
                dept_item.update({'nodes': []})
                result_list.append(dept_item)
            obj = data_processing.Processing()
            gds = obj.group_data_structure(result_list)
            return_data = {'status': True, 'query_data': gds}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_DEPT_LEVEL:
            """ 查询所有部门级别 """
            query_result = models.KmsDepartmentLevel.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {
                    'level_id': i.id,
                    'department_level': i.department_level,
                    'superior_correlate_id': i.superior_correlate_id}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_PERMISSION:
            """ 查询所有权限 """
            query_result = models.KmsUserPermissions.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {
                    'permitId': i.id,
                    'permitName': i.name}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_KNOWLEDGE:
            query_result = models.KmsKnowledgeClassify.objects.all().values('id', 'category', 'classify_name').order_by(
                'id')
            category_list = list()  # 类别列表
            result_list = list()  # 处理结果列表
            for i in query_result:  # 获取所有类别
                category_list.append(i['category'])
            for j in list(set(category_list)):  # 通过set去除重复
                pro_data = {'category': None, 'nodes': []}
                for k in query_result:
                    if j == k['category']:
                        pro_data['category'] = j
                        pro_data['nodes'].append(k)
                result_list.append(pro_data)
            result_list.sort(key=lambda category: category.get('category'))
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_HOMEPAGE:
            query_result = models.KmsHomePageSettings.objects.all().values('id', 'nav_name', 'view_permissions__id',
                                                                           'view_permissions__name',
                                                                           'filter_conditions').order_by('id')
            result_list = list()
            for i in query_result:
                result_dict = {
                    'id': i['id'],
                    'navName': i['nav_name'],
                    'viewPermissions': i['view_permissions__name'] if i['view_permissions__name'] else '',
                    'viewPermissionsId': i['view_permissions__id'],
                    'filterConditions': i['filter_conditions']}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))


def add(request):
    if request.method == "POST":
        handle = request.POST.get('handle')
        if handle == PANEL_USER:
            """ 添加注册人员 """
            username = request.POST.get('username', None)
            show_username = request.POST.get('showUsername', None)
            password = request.POST.get('password', None)
            email = request.POST.get('email', None) if request.POST.get('email', None) else None
            phone_number = request.POST.get('phoneNumber', None) if request.POST.get('phoneNumber', None) else None
            reg_department = request.POST.get('regDepartment', None)
            reg_permission = request.POST.get('regPermission', None)
            # 列表为空时赋值为None，不为空时将列表内所有元素转换为int类型
            reg_permission = list(map(int, json.loads(reg_permission))) if json.loads(reg_permission) else None

            form_verifying = form.RegisterForm(request.POST)  # 验证提交的数据
            if form_verifying.is_valid():
                # print(formVerifying.cleaned_data)
                md5_obj = MD5_encryption.Md5(password)
                md5_pwd = md5_obj.md5_password()
                models.KmsUser.objects.create(username=username, show_name=show_username, password=md5_pwd,
                                              email=email, phone_number=phone_number, groups_id=reg_department)
                user_obj = models.KmsUser.objects.filter(username=username)
                if reg_permission is not None:
                    for i in reg_permission:
                        permit_obj = models.KmsUserPermissions.objects.get(id=i)
                        permit_obj.kms_user.add(*user_obj)
                return HttpResponse(json.dumps({'status': True, 'message': '注册成功！'}))
            else:
                # print(formVerifying.errors.get_json_data())
                return HttpResponse(json.dumps({'status': False, 'message': form_verifying.errors.get_json_data()}))
        elif handle == PANEL_DEPARTMENT:
            # 添加部门
            dept_level = request.POST.get('deptLevel', None)
            superior_dept_id = request.POST.get('superiorDeptId', None)
            superior_dept_id = superior_dept_id if superior_dept_id else None
            dept_name = request.POST.get('deptName', None)
            dept_level_id = models.KmsDepartmentLevel.objects.filter(department_level=dept_level).values('id').first()
            models.KmsGroup.objects.create(dept_level_id=dept_level_id['id'],
                                           superior_dept=superior_dept_id,
                                           dept_name=dept_name)
            return HttpResponse(json.dumps({'status': True}))
        elif handle == PANEL_DEPT_LEVEL:
            # 添加部门级别
            dept_level = request.POST.get('deptLevel', None)
            sup_correlate = request.POST.get('supCorrelate', None)
            sup_correlate = sup_correlate if sup_correlate else None
            models.KmsDepartmentLevel.objects.create(department_level=dept_level, superior_correlate_id=sup_correlate)
            query_result = models.KmsDepartmentLevel.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {
                    'levelId': i.id,
                    'department_level': i.department_level,
                    'superior_correlate_id': i.superior_correlate_id}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_PERMISSION:
            # 添加权限
            permit_name = request.POST.get('permitName', None)
            models.KmsUserPermissions.objects.create(name=permit_name)
            query_result = models.KmsUserPermissions.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {
                    'permitId': i.id,
                    'permitName': i.name}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_KNOWLEDGE:
            knowledge_category = request.POST.get('knowledgeCategory', None)
            classify_name = request.POST.get('classifyName', None)
            # 查询是否重复，重复时不做任何操作
            is_exist = models.KmsKnowledgeClassify.objects.filter(category=knowledge_category,
                                                                  classify_name=classify_name)
            if not is_exist:
                models.KmsKnowledgeClassify.objects.create(category=knowledge_category, classify_name=classify_name)
            return HttpResponse(json.dumps({'status': True}))
        elif handle == PANEL_HOMEPAGE:
            # 添加首页导航
            nav_name = request.POST.get('navName', None)
            view_permissions = request.POST.get('viewPermissions', None)
            view_permissions = view_permissions if view_permissions else None
            filter_conditions = request.POST.get('filterConditions', None)

            models.KmsHomePageSettings.objects.create(nav_name=nav_name, view_permissions_id=view_permissions,
                                                      filter_conditions=filter_conditions)
            query_result = models.KmsHomePageSettings.objects.all().values('id', 'nav_name', 'view_permissions__id',
                                                                           'view_permissions__name',
                                                                           'filter_conditions').order_by('id')
            result_list = list()
            for i in query_result:
                result_dict = {
                    'id': i['id'],
                    'navName': i['nav_name'],
                    'viewPermissions': i['view_permissions__name'] if i['view_permissions__name'] else '',
                    'viewPermissionsId': i['view_permissions__id'],
                    'filterConditions': i['filter_conditions']}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))


def edit(request):
    """ 编辑后台数据 """
    if request.method == "POST":
        handle = request.POST.get('handle')
        if handle == PANEL_USER:
            uid = request.POST.get('uid', None)
            raw_username = request.POST.get('rawUsername', None)
            raw_password = request.POST.get('rawPassword', None)
            username = request.POST.get('username', None)
            show_username = request.POST.get('showUsername', None)
            password = request.POST.get('password', None)
            email = request.POST.get('email', None) if request.POST.get('email', None) else None
            phone_number = request.POST.get('phoneNumber', None) if request.POST.get('phoneNumber', None) else None
            reg_department = request.POST.get('regDepartment', None)
            reg_permission = request.POST.get('regPermission', None)
            reg_permission = list(map(int, json.loads(reg_permission))) if json.loads(reg_permission) else None

            formVerifying = form.RegisterForm(request.POST, request.get_full_path())  # 验证提交的数据
            if formVerifying.is_valid():
                if raw_password == password:
                    models.KmsUser.objects.filter(uid=uid, username=raw_username).update(username=username,
                                                                                         show_name=show_username,
                                                                                         email=email,
                                                                                         phone_number=phone_number,
                                                                                         groups_id=reg_department)
                else:
                    md5Obj = MD5_encryption.Md5(password)
                    md5pwd = md5Obj.md5_password()
                    models.KmsUser.objects.filter(uid=uid, username=raw_username).update(username=username,
                                                                                         show_name=show_username,
                                                                                         password=md5pwd,
                                                                                         email=email,
                                                                                         phone_number=phone_number,
                                                                                         groups_id=reg_department)
                user_obj = models.KmsUser.objects.filter(uid=uid, username=username).first()
                if reg_permission is not None:
                    # 添加权限
                    user_obj.kmsuserpermissions_set.add(*reg_permission)
                    all_permission = user_obj.kmsuserpermissions_set.all().values()
                    # 批量删除权限
                    for j in all_permission:
                        if j['id'] not in reg_permission:
                            user_obj.kmsuserpermissions_set.remove(j['id'])
                else:
                    # 删除所有权限
                    all_permission = user_obj.kmsuserpermissions_set.all().values()
                    for i in all_permission:
                        user_obj.kmsuserpermissions_set.remove(i['id'])
                return HttpResponse(json.dumps({'status': True, 'message': '修改成功！'}))
            else:
                # print(formVerifying.errors.get_json_data())
                return HttpResponse(json.dumps({'status': False, 'message': formVerifying.errors.get_json_data()}))
        elif handle == PANEL_DEPARTMENT:
            # 修改部门信息
            raw_dept_name = request.POST.get('rawDeptName', None)  # 原部门名称
            dept_level = request.POST.get('deptLevel', None)  # 部门级别
            curr_dept_name = request.POST.get('deptName', None)  # 修改后的名称
            superior_dept_id = request.POST.get('superiorDeptId', None)  # 上级部门名称
            dept_id = request.POST.get('deptId', None)
            # 将所上级部门为当前修改的部门的 superior_dept 字段更新为修改后的内容
            # models.KmsGroup.objects.filter(superior_dept=rawDeptName).update(superior_dept=deptId)
            # 获取部门id
            dept_level_id = models.KmsDepartmentLevel.objects.filter(department_level=dept_level).values('id').first()
            models.KmsGroup.objects.filter(Q(id=dept_id) & Q(dept_name=raw_dept_name)).update(
                dept_level=dept_level_id['id'], superior_dept=superior_dept_id, dept_name=curr_dept_name)
            return HttpResponse(json.dumps({'status': True}))
        elif handle == PANEL_DEPT_LEVEL:
            # 修改部门级别
            level_id = request.POST.get('levelId', None)
            dept_level = request.POST.get('deptLevel', None)
            raw_content = request.POST.get('rawContent', None)
            sup_correlate = request.POST.get('supCorrelate', None)
            models.KmsDepartmentLevel.objects.filter(id=level_id,
                                                     department_level=raw_content).update(department_level=dept_level,
                                                                                          superior_correlate_id=sup_correlate)
            query_result = models.KmsDepartmentLevel.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {
                    'levelId': i.id,
                    'department_level': i.department_level,
                    'superior_correlate_id': i.superior_correlate_id}
                result_list.append(result_dict)
            returnData = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(returnData))
        elif handle == PANEL_PERMISSION:
            # 修改权限
            permit_id = request.POST.get('permitId', None)
            permit_name = request.POST.get('permitName', None)
            raw_content = request.POST.get('rawContent', None)
            models.KmsUserPermissions.objects.filter(id=permit_id, name=raw_content).update(name=permit_name)
            query_result = models.KmsUserPermissions.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {'permitId': i.id, 'permitName': i.name}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_KNOWLEDGE:
            knowledge_category = request.POST.get('knowledgeCategory', None)
            classify_name = request.POST.get('classifyName', None)
            raw_knowledge_category = request.POST.get('rawCategory', None)
            raw_classify_name = request.POST.get('rawClassifyName', None)
            models.KmsKnowledgeClassify.objects.filter(category=raw_knowledge_category,
                                                       classify_name=raw_classify_name).update(
                category=knowledge_category,
                classify_name=classify_name)
            return HttpResponse(json.dumps({'status': True}))
        elif handle == PANEL_HOMEPAGE:
            hps_id = request.POST.get('hpsId', None)
            nav_name = request.POST.get('navName', None)
            raw_nav_name = request.POST.get('rawNavName', None)
            view_permissions = request.POST.get('viewPermissions', None)
            view_permissions = view_permissions if view_permissions else None
            filter_conditions = request.POST.get('filterConditions', None)

            models.KmsHomePageSettings.objects.filter(id=hps_id, nav_name=raw_nav_name).update(nav_name=nav_name,
                                                                                               view_permissions_id=view_permissions,
                                                                                               filter_conditions=filter_conditions)

            query_result = models.KmsHomePageSettings.objects.all().values('id', 'nav_name', 'view_permissions__id',
                                                                           'view_permissions__name',
                                                                           'filter_conditions').order_by('id')
            result_list = list()
            for i in query_result:
                result_dict = {
                    'id': i['id'],
                    'navName': i['nav_name'],
                    'viewPermissions': i['view_permissions__name'] if i['view_permissions__name'] else '',
                    'viewPermissionsId': i['view_permissions__id'],
                    'filterConditions': i['filter_conditions']}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))


def delete(request):
    """ 删除数据 """
    if request.method == 'POST':
        handle = request.POST.get('handle', None)
        data_set = request.POST.getlist('dataSet', None)  # 获取需要删除文件的列表
        return_data = {'status': True}
        if handle == PANEL_USER:
            for i in json.loads(data_set[0]):
                models.KmsUser.objects.filter(Q(uid=i['id']) & Q(username=i['name'])).delete()
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_DEPARTMENT:
            for i in json.loads(data_set[0]):
                models.KmsGroup.objects.filter(Q(id=i['id']) & Q(dept_name=i['name'])).delete()
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_DEPT_LEVEL:
            for i in json.loads(data_set[0]):
                models.KmsDepartmentLevel.objects.filter(Q(id=i['id']) & Q(department_level=i['name'])).delete()
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_PERMISSION:
            for i in json.loads(data_set[0]):
                models.KmsUserPermissions.objects.filter(Q(id=i['id']) & Q(name=i['name'])).delete()
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_KNOWLEDGE:
            for i in json.loads(data_set[0]):
                models.KmsKnowledgeClassify.objects.filter(
                    Q(category=i['knowledgeCategory']) & Q(classify_name=i['classifyName'])).delete()
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_HOMEPAGE:
            for i in json.loads(data_set[0]):
                models.KmsHomePageSettings.objects.filter(Q(id=i['id']) & Q(nav_name=i['navName'])).delete()
            return HttpResponse(json.dumps(return_data))


def query_dept_level(request):
    """
    新增修改部门时，选择部门级别查询对应上级部门
    :param request:
    :return:
    """
    if request.method == 'POST':
        superior_dept_id = request.POST.get('superiorDeptId', None)
        dept_level = request.POST.get('deptLevel', None)
        if superior_dept_id is not None:
            query_result = models.KmsGroup.objects.filter(id=superior_dept_id).values('dept_level__department_level',
                                                                                      'dept_name', 'superior_dept',
                                                                                      'id')
        else:
            query_result = models.KmsGroup.objects.filter(dept_level=dept_level).values('dept_level__department_level',
                                                                                        'dept_name', 'superior_dept',
                                                                                        'id')
        result_list = list()
        for dept_item in query_result:
            result_list.append(dept_item)
            obj = data_processing.Processing()
            sup_dept_name = obj.group_data_join(dept_item['superior_dept'])
            dept_item['dept_name'] = dept_item['dept_name'] + sup_dept_name

        return HttpResponse(json.dumps({'status': True, 'query_data': result_list}))


def query_dept_list(request):
    """
    注册人员时获取所有的部门列表
    :param request:
    :return:
    """
    result_list = list()
    query_result = models.KmsGroup.objects.all().values('dept_level__department_level', 'dept_name', 'superior_dept',
                                                        'id')
    for dept_item in query_result:
        result_list.append(dept_item)
        obj = data_processing.Processing()
        sup_dept_name = obj.group_data_join(dept_item['superior_dept'])
        # print(deptItem['dept_name'], supDeptName)
        dept_item['dept_name'] = dept_item['dept_name'] + sup_dept_name
    return HttpResponse(json.dumps({'status': True, 'query_data': result_list}))


# 定时清理过期session
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
try:
    def clear_session():
        os.chdir(os.path.dirname(os.path.dirname(__file__)))
        ret = os.system('python manage.py clearsessions')
        if ret == 0:
            print('清理过期session完成！')


    # scheduler.add_job(clear_session, 'interval', seconds=3)
    scheduler.add_job(clear_session, 'cron', hour=23, minute=30)
    scheduler.start()
except Exception as e:
    print(e)
    scheduler.shutdown()
