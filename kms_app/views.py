from django.shortcuts import render,HttpResponse,redirect,render_to_response,reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import json
import hashlib
from django.db.models import Q,F
from kms_app import models
from utils import data_processing
from utils import MD5_encryption
from kms_app import form
from django.db import connection
from KMS import settings
import time
import os
import uuid
import re
import shutil

# Create your views here.

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
RETURN = '退回'


def login(request):
    """登陆页"""
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        md5_obj = MD5_encryption.Md5(password)
        md5_pwd = md5_obj.md5_password()
        try:
            # 查询用户名和密码是否匹配。 django orm 的 get 方法如果获取不到数据会报错
            login_user = models.KmsUser.objects.get(username=username,password=md5_pwd)
        except Exception:
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
    homepage_nav = models.KmsHomePageSettings.objects.all().values('id','nav_name').order_by('id')
    # print(list(homepage_nav),type(list(homepage_nav)))
    # for i in homepage_nav:
    #     print(i)
    return render(request, 'index.html', {'show_name': show_name, 'permission': permission,'homepage_nav':homepage_nav})

def query_index_data(request):
    nav_id = request.POST.get('navId', None)
    nav_name = request.POST.get('navName', None)
    # if nav_id and nav_name:
    filter_conditions = models.KmsHomePageSettings.objects.filter(id=nav_id,nav_name=nav_name).values('filter_conditions')
    sql = "SELECT `id`, `uuid`, `title`, `issuer`, `issuer_dept`, `classify_name`, `release_date`, `auditor`, `remarks`, " \
          "`issue_type`, `del_status`, `doc_status`, `details`, `describe`, `solution`, `return_reason` " \
          "FROM `kms_app_kmsdocinfo` WHERE " + filter_conditions[0]['filter_conditions']
    # cursor = connection.cursor()
    # cursor.execute(sql)
    raw_query_set = models.KmsDocInfo.objects.raw(sql)  # 原生sql查询
    doc_info_list = list()
    for obj in raw_query_set:
        # 循环查询的RawQuerySet对象，将结果添加到doc_info_list列表中，用于分页使用
        doc_info_list.append(obj)

    pag = Paginator(doc_info_list,16)    # 定义分页器，每页显示10条
    page = request.POST.get('page', None)     # 从前端获取当前的页码数

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

    has_per_page = page_obj.has_previous() # 当前页是否有上一页
    if has_per_page:
        per_page_number = page_obj.previous_page_number() # 上一页页码
    else:
        per_page_number = None

    total_page = list() # 总页数列表
    for page in pag.page_range: # 总页数
        total_page.append(page)

    has_next_page = page_obj.has_next() # 当前页是否有下一页
    if has_next_page:
        next_page_number = page_obj.next_page_number()  # 下一页页码
    else:
        next_page_number = None

    page_dict = {'has_per_page':has_per_page,'per_page_number':per_page_number,'total_page':total_page,
                 'has_next_page':has_next_page,'next_page_number':next_page_number,'current_page':current_page}
    result_list = list()    # json返回的数据列表
    for i in page_obj:
        temp_dict = dict()
        temp_dict['uuid'] = i.uuid
        temp_dict['title'] = i.title
        temp_dict['issuer'] = i.issuer
        temp_dict['classify_name'] = i.classify_name
        temp_dict['issuer_dept'] = i.issuer_dept
        temp_dict['auditor'] = i.auditor
        temp_dict['release_date'] = str(i.release_date)
        result_list.append(temp_dict)

    return HttpResponse(json.dumps({'status':True,'result_list':result_list,'page_dict':page_dict}))

def classify(request):
    """分类页"""
    show_name = request.session['show_name']
    permission = request.session['permission']
    return render(request, 'classify.html', {'show_name': show_name, 'permission': permission})

def release(request):
    """发布页"""
    if request.method == "GET":
        username = request.session['username']      # 当前登陆用户
        show_name = request.session['show_name']
        current_time = time.strftime('%Y-%m-%d')    # 当前时间
        doc_uuid = request.GET.get('doc_uuid', None)      # 获取当前文件的uuid
        # 获取当前用户所在部门的id
        group = models.KmsUser.objects.filter(username=username).values('groups__id','groups__dept_name')
        # 获取部门内的所有人
        all_people = models.KmsUser.objects.filter(groups_id=group[0]['groups__id']).values('uid','username','show_name')
        permission_name = models.KmsUserPermissions.objects.get(name='审核员')
        auditor_list = list()
        # 查询当前部门下具有 审核员 权限的人
        for i in all_people:
            auditor = permission_name.kms_user.filter(uid=i['uid']).values()
            if auditor:
                auditor_list.append(auditor[0]['show_name'])
        # 分类数据处理
        query_result = models.KmsKnowledgeClassify.objects.all().values('id', 'category', 'classify_name').order_by('id')
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

        if doc_uuid is None:    # 生成文档uuid
            doc_uuid = uuid.uuid1()     # 文档uuid
            os.mkdir(os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), str(doc_uuid)))
        else:
            file_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), str(doc_uuid))
            # 每次刷新后 shutil.rmtree() 先强制删除所有文件，然后在重新创建 doc_uuid 文件夹
            # shutil.rmtree(os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), str(doc_uuid)))
            if not os.path.exists(file_path):
                os.mkdir(os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), str(doc_uuid)))

        return render(request, 'release.html', {'show_name': show_name, 'current_time': current_time, 'auditor_list': auditor_list,
                                                'dept_name': group[0]['groups__dept_name'], 'category_list': result_list,'doc_uuid': doc_uuid})

def media_upload(request):
    file = request.FILES.get('file')
    doc_uuid = request.POST.get('doc_uuid')
    # 拼接文件路径
    file_dir = os.path.join(
        os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), str(doc_uuid)),file.name)

    # 写入文件
    f = open(file_dir, 'wb')
    for i in file.chunks():
        f.write(i)
    f.close()
    ret_url = list()    # 前端显示地址列表
    url ='{0}{1}{2}'.format(settings.MEDIA_URL, str(doc_uuid) + '/', file.name)     # 富文本框图片显示地址
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
        file_dir = os.path.join(
            os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), doc_uuid),att_file.name)
        f = open(file_dir, 'wb')
        for i in att_file.chunks():
            f.write(i)
        f.close()
        # 下载和预览的url
        url = settings.MEDIA_URL + str(doc_uuid) + '/' + att_file.name
        file_type = re.search(r'[^.]+\w$', att_file.name).group()
        img_list = ['jpg', 'jpeg', 'jpe', 'gif', 'png', 'pns', 'bmp', 'png', 'tif']
        pdf_list = ['pdf']
        text_list = ['txt', 'md', 'csv', 'nfo', 'ini', 'json', 'php', 'js', 'css']

        # bootstrap fileinput 上传文件的回显参数，initialPreview，initialPreviewConfig
        initialPreview = []
        if file_type in img_list:
            initialPreview.append("<img src='" + url + "' class='file-preview-image' style='max-width:100%;max-height:100%;'>")
        elif file_type in pdf_list:
            initialPreview.append("<div class='file-preview-frame'><div class='kv-file-content'><embed class='kv-preview-data file-preview-pdf' src='" + url +
                                  "' type='application/pdf' style='width:100%;height:160px;'></div></div>")
        elif file_type in text_list:
            f = open(file_dir)
            initialPreview.append("<div class='file-preview-frame'><div class='kv-file-content'><textarea class='kv-preview-data file-preview-text' title='" + att_file.name +
                                  "' readonly style='width:213px;height:160px;'>"+f.read()+"</textarea></div></div>")
        else:
            initialPreview.append("<div class='file-preview-other'><span class='file-other-icon'><i class='glyphicon glyphicon-file'></i></span></div>")

        initialPreviewConfig = [{
            'caption': att_file.name,
            'type': file_type,
            'downloadUrl': url,
            'url': '/del_doc_file/',
            'size': os.path.getsize(file_dir),
            'extra': {'doc_uuid': doc_uuid},    # 删除文件携带的参数
            'key': att_file.name,
        }]
        return HttpResponse(json.dumps({'initialPreview':initialPreview, 'initialPreviewConfig':initialPreviewConfig,'append': True}))
    else:
        return HttpResponse(json.dumps({'status': False}))

def del_doc_file(request):
    """
    wangEditor控件 bootstarp fileinput控件 删除媒体内容或附件时同步删除服务器中的数据
    :param request:
    :return:
    """
    # print(request.META.get('HTTP_SENDING_METHOD'))
    # print(type(request.META),request.META)
    # print('HTTP_SENDING_METHOD' in request.META.keys())
    if request.method == 'POST':
        doc_uuid = request.POST.get('doc_uuid', None)
        file_name = request.POST.get('fileName',None)
        key = request.POST.get('key',None)
        temp_file_name = ''
        if file_name:
            temp_file_name = file_name
        elif key:
            temp_file_name = key

        file_dir = os.path.join(
            os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), doc_uuid), temp_file_name)
        # 检查前端删除的文件是否存在，存在则删除
        if os.path.exists(file_dir):
            os.remove(file_dir)

    return HttpResponse(json.dumps({'status': True}))

def del_all_att(request):
    """ 批量删除附件 """
    doc_uuid = request.POST.get('doc_uuid', None)
    file_list = request.POST.getlist('aryFiles', None)

    for file_name in json.loads(file_list[0]):
        file_dir = os.path.join(
            os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), doc_uuid), file_name)

        if os.path.exists(file_dir):
            os.remove(file_dir)
    return HttpResponse(json.dumps({"status": True}))

def del_doc(request):
    """ 删除文档 """
    if request.method == 'POST':
        uuid_list = request.POST.getlist('uuidSet',None)
        for i in json.loads(uuid_list[0]):
            ret = models.KmsDocInfo.objects.filter(uuid=i).delete()
            shutil.rmtree(os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), str(i)))
    return HttpResponse(json.dumps({'status': True}))

def save_doc(request):
    operation = request.POST.get('operation',None)
    doc_uuid = request.POST.get('uuid', None)
    title = request.POST.get('title', None)
    classify_name = request.POST.get('classify', None)
    issuer = request.POST.get('issuer', None)
    release_date = request.POST.get('releaseDate', None)
    auditor = request.POST.get('auditor', None)
    issue_type = request.POST.get('issueType', None)
    issuer_dept = request.POST.get('issuerDept', None)
    remarks = request.POST.get('remarks', None)
    details = request.POST.get('details1', None)
    describe = request.POST.get('describe1', None)
    solution = request.POST.get('solution1', None)
    list_url = request.POST.getlist('aryUrl', None)
    if operation == 'save':
        obj = models.KmsDocInfo.objects.create(uuid=doc_uuid,title=title,classify_name=classify_name,issuer=issuer,release_date=release_date,
                                         auditor=auditor,issue_type=issue_type,remarks=remarks,issuer_dept=issuer_dept,details=details,
                                         describe=describe,solution=solution,del_status=0,doc_status=SAVE)
    elif operation == 'submit':
        obj = models.KmsDocInfo.objects.create(uuid=doc_uuid,title=title,classify_name=classify_name,issuer=issuer,release_date=release_date,
                                         auditor=auditor,issue_type=issue_type,remarks=remarks,issuer_dept=issuer_dept,details=details,
                                         describe=describe,solution=solution,del_status=0,doc_status=EXAMINE)

    for dict_url in json.loads(list_url[0]):
        models.KmsFilePath.objects.create(doc_info_id=obj.id,uuid=doc_uuid,path=dict_url['url'],name=dict_url['name'])
    return HttpResponse(json.dumps({'status': True}))

def view_form(request):
    """ 文件查看 """
    doc_uuid = request.GET.get('doc_uuid', None)

    if doc_uuid:
        doc_obj = models.KmsDocInfo.objects.filter(uuid=doc_uuid).values('uuid','title','classify_name','issuer',
                                                                         'release_date','issuer_dept','auditor',
                                                                         'issue_type','remarks','details','describe',
                                                                         'solution',)
        doc_result = doc_obj[0]
        doc_result['release_date'] = str(doc_result['release_date'])
        path_obj = models.KmsFilePath.objects.filter(uuid=doc_uuid).values('path','name')
        doc_result.update({'initialPreview': [], 'initialPreviewConfig': []})
        for dict_path in path_obj:
            # print(dict_path)
            file_type = re.search(r'[^.]+\w$', dict_path['path']).group()
            img_list = ['jpg', 'jpeg', 'jpe', 'gif', 'png', 'pns', 'bmp', 'png', 'tif']
            pdf_list = ['pdf']
            text_list = ['txt', 'md', 'csv', 'nfo', 'ini', 'json', 'php', 'js', 'css']

            # bootstrap fileinput 预览参数，initialPreview，initialPreviewConfig
            file_dir = os.path.join(
                os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), doc_uuid),dict_path['name'])
            if file_type in img_list:
                doc_result['initialPreview'].append(
                    "<img src='" + dict_path['path'] + "' class='file-preview-image' style='max-width:100%;max-height:100%;'>")
            elif file_type in pdf_list:
                doc_result['initialPreview'].append(
                    "<div class='file-preview-frame'><div class='kv-file-content'><embed class='kv-preview-data file-preview-pdf' src='" + dict_path['path'] +
                    "' type='application/pdf' style='width:100%;height:160px;'></div></div>")
            elif file_type in text_list:
                f = open(file_dir)
                doc_result['initialPreview'].append(
                    "<div class='file-preview-frame'><div class='kv-file-content'><textarea class='kv-preview-data file-preview-text' title='" + dict_path['name'] +
                    "' readonly style='width:213px;height:160px;'>"+f.read()+"</textarea></div></div>"
                )
            else:
                doc_result['initialPreview'].append(
                    "<div class='file-preview-other'><span class='file-other-icon'><i class='glyphicon glyphicon-file'></i></span></div>")


            initialPreviewDict = {
                'caption': dict_path['name'],
                'type': file_type,
                'downloadUrl': dict_path['path'],
                # 'url': '/del_doc_file/',
                'size': os.path.getsize(file_dir),
                'extra': {'doc_uuid': doc_uuid},  # 删除文件携带的参数
                'key': dict_path['name'],
            }
            doc_result['initialPreviewConfig'].append(initialPreviewDict)

        return render(request, 'view_form.html', {'data': doc_result})

"""
def del_doc_att(request):
    key = request.POST.get('key', None)
    doc_uuid = request.POST.get('doc_uuid', None)
    print(key,doc_uuid)
    file_dir = os.path.join(
        os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'upload_files'), doc_uuid), key)
    if os.path.exists(file_dir):
        os.remove(file_dir)
    return HttpResponse(json.dumps({'status': True}))
"""

def center(request):
    """个人中心"""
    show_name = request.session['show_name']
    permission = request.session['permission']
    return render(request, 'center.html', {'show_name': show_name, 'permission': permission})

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
        handle = request.POST.get('handle',None)
        if handle == PANEL_USER:
            """ 查询所有用户 """
            query_result = models.KmsUser.objects.all().values('uid','username','password','show_name','email',
                                                              'phone_number','groups__dept_name','groups__id')
            result_list = list()
            for user_item in query_result:
                user_item.update({'permissionsID': [], 'permissions': []})
                user_obj = models.KmsUser.objects.get(uid=user_item['uid'])
                for i in user_obj.kmsuserpermissions_set.all().values():    # 查询多对多用户权限
                    user_item['permissionsID'].append(i['id'])
                    user_item['permissions'].append(i['name'])
                result_list.append(user_item)
            # 将所有结果为null的字段转换为空字符串
            for i in result_list:
                for j in i:
                    i[j] = "" if i[j] is None else i[j]
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_DEPARTMENT:
            """ 查询所有群组 """
            result_list = list()
            query_group = models.KmsGroup.objects.all().annotate(name=F('dept_name')).values('id', 'name', 'dept_level__department_level', 'superior_dept')
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
                    'level_id':i.id,
                    'department_level':i.department_level,
                    'superior_correlate_id':i.superior_correlate_id}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_PERMISSION:
            """ 查询所有权限 """
            query_result = models.KmsUserPermissions.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {
                    'permitId':i.id,
                    'permitName':i.name}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_KNOWLEDGE:
            query_result = models.KmsKnowledgeClassify.objects.all().values('id', 'category', 'classify_name').order_by('id')
            category_list = list()      # 类别列表
            result_list = list()        # 处理结果列表
            for i in query_result:      # 获取所有类别
                category_list.append(i['category'])
            for j in list(set(category_list)):  # 通过set去除重复
                pro_data = {'category': None, 'nodes': []}
                for k in query_result:
                    if j == k['category']:
                        pro_data['category'] = j
                        pro_data['nodes'].append(k)
                result_list.append(pro_data)
            # print(result_list)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_HOMEPAGE:
            query_result = models.KmsHomePageSettings.objects.all().values('id','nav_name','view_permissions__id',
                                                                           'view_permissions__name','filter_conditions').order_by('id')
            result_list = list()
            for i in query_result:
                result_dict = {
                    'id':i['id'],
                    'navName':i['nav_name'],
                    'viewPermissions':i['view_permissions__name'] if i['view_permissions__name'] else '',
                    'viewPermissionsId':i['view_permissions__id'],
                    'filterConditions':i['filter_conditions']}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))

def add(request):
    if request.method == "POST":
        handle = request.POST.get('handle')
        if handle == PANEL_USER:
            """ 添加注册人员 """
            username = request.POST.get('username',None)
            show_username = request.POST.get('showUsername',None)
            password = request.POST.get('password',None)
            email = request.POST.get('email',None) if request.POST.get('email',None) else None
            phone_number = request.POST.get('phoneNumber',None) if request.POST.get('phoneNumber',None) else None
            reg_department = request.POST.get('regDepartment',None)
            reg_permission = request.POST.get('regPermission',None)
            # 列表为空时赋值为None，不为空时将列表内所有元素转换为int类型
            reg_permission = list(map(int, json.loads(reg_permission))) if json.loads(reg_permission) else None

            form_verifying = form.RegisterForm(request.POST)     # 验证提交的数据
            if form_verifying.is_valid():
                # print(formVerifying.cleaned_data)
                md5_obj = MD5_encryption.Md5(password)
                md5_pwd = md5_obj.md5_password()
                models.KmsUser.objects.create(username=username,show_name=show_username, password=md5_pwd,
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
            sup_correlate = request.POST.get('supCorrelate',None)
            sup_correlate = sup_correlate if sup_correlate else None
            models.KmsDepartmentLevel.objects.create(department_level=dept_level,superior_correlate_id=sup_correlate)
            query_result = models.KmsDepartmentLevel.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {
                    'levelId':i.id,
                    'department_level':i.department_level,
                    'superior_correlate_id':i.superior_correlate_id}
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
                    'permitId':i.id,
                    'permitName':i.name}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_KNOWLEDGE:
            knowledge_category = request.POST.get('knowledgeCategory', None)
            classify_name = request.POST.get('classifyName',None)
            # 查询是否重复，重复时不做任何操作
            is_exist = models.KmsKnowledgeClassify.objects.filter(category=knowledge_category, classify_name=classify_name)
            if not is_exist:
                models.KmsKnowledgeClassify.objects.create(category=knowledge_category, classify_name=classify_name)
            return HttpResponse(json.dumps({'status':True}))
        elif handle == PANEL_HOMEPAGE:
            # 添加首页导航
            nav_name = request.POST.get('navName', None)
            view_permissions = request.POST.get('viewPermissions', None)
            view_permissions = view_permissions if view_permissions else None
            filter_conditions = request.POST.get('filterConditions', None)

            models.KmsHomePageSettings.objects.create(nav_name=nav_name,view_permissions_id=view_permissions,
                                                      filter_conditions=filter_conditions)
            query_result = models.KmsHomePageSettings.objects.all().values('id','nav_name','view_permissions__id',
                                                                           'view_permissions__name','filter_conditions').order_by('id')
            result_list = list()
            for i in query_result:
                result_dict = {
                    'id':i['id'],
                    'navName':i['nav_name'],
                    'viewPermissions':i['view_permissions__name'] if i['view_permissions__name'] else '',
                    'viewPermissionsId':i['view_permissions__id'],
                    'filterConditions':i['filter_conditions']}
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
            username = request.POST.get('username',None)
            show_username = request.POST.get('showUsername',None)
            password = request.POST.get('password',None)
            email = request.POST.get('email',None) if request.POST.get('email',None) else None
            phone_number = request.POST.get('phoneNumber',None) if request.POST.get('phoneNumber',None) else None
            reg_department = request.POST.get('regDepartment',None)
            reg_permission = request.POST.get('regPermission',None)
            reg_permission = list(map(int, json.loads(reg_permission))) if json.loads(reg_permission) else None

            formVerifying = form.RegisterForm(request.POST, request.get_full_path())  # 验证提交的数据
            if formVerifying.is_valid():
                if raw_password == password:
                    models.KmsUser.objects.filter(uid=uid,username=raw_username).update(username=username,
                                                                                       show_name=show_username,
                                                                                       email=email,
                                                                                       phone_number=phone_number,
                                                                                       groups_id=reg_department)
                else:
                    md5Obj = MD5_encryption.Md5(password)
                    md5pwd = md5Obj.md5_password()
                    models.KmsUser.objects.filter(uid=uid,username=raw_username).update(username=username,
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
            raw_dept_name = request.POST.get('rawDeptName', None)     # 原部门名称
            dept_level = request.POST.get('deptLevel', None)   # 部门级别
            curr_dept_name = request.POST.get('deptName', None)       # 修改后的名称
            superior_dept_id = request.POST.get('superiorDeptId', None)   # 上级部门名称
            dept_id = request.POST.get('deptId', None)
            # 将所上级部门为当前修改的部门的 superior_dept 字段更新为修改后的内容
            # models.KmsGroup.objects.filter(superior_dept=rawDeptName).update(superior_dept=deptId)
            # 获取部门id
            dept_level_id = models.KmsDepartmentLevel.objects.filter(department_level=dept_level).values('id').first()
            models.KmsGroup.objects.filter(Q(id=dept_id) & Q(dept_name=raw_dept_name)).update(
                                            dept_level=dept_level_id['id'],superior_dept=superior_dept_id,dept_name=curr_dept_name)
            return HttpResponse(json.dumps({'status': True}))
        elif handle == PANEL_DEPT_LEVEL:
            # 修改部门级别
            level_id = request.POST.get('levelId', None)
            dept_level = request.POST.get('deptLevel', None)
            raw_content = request.POST.get('rawContent', None)
            sup_correlate = request.POST.get('supCorrelate',None)
            models.KmsDepartmentLevel.objects.filter(id=level_id,
                                                     department_level=raw_content).update(department_level=dept_level,
                                                                                         superior_correlate_id=sup_correlate)
            query_result = models.KmsDepartmentLevel.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {
                    'levelId':i.id,
                    'department_level':i.department_level,
                    'superior_correlate_id':i.superior_correlate_id}
                result_list.append(result_dict)
            returnData = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(returnData))
        elif handle == PANEL_PERMISSION:
            # 修改权限
            permit_id = request.POST.get('permitId', None)
            permit_name = request.POST.get('permitName', None)
            raw_content = request.POST.get('rawContent', None)
            models.KmsUserPermissions.objects.filter(id=permit_id,name=raw_content).update(name=permit_name)
            query_result = models.KmsUserPermissions.objects.all()
            result_list = list()
            for i in query_result:
                result_dict = {'permitId': i.id, 'permitName': i.name}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))
        elif handle == PANEL_KNOWLEDGE:
            knowledge_category = request.POST.get('knowledgeCategory', None)
            classify_name = request.POST.get('classifyName',None)
            raw_knowledge_category = request.POST.get('rawCategory', None)
            raw_classify_name = request.POST.get('rawClassifyName', None)
            models.KmsKnowledgeClassify.objects.filter(category=raw_knowledge_category,
                                                       classify_name=raw_classify_name).update(category=knowledge_category,
                                                                                               classify_name=classify_name)
            return HttpResponse(json.dumps({'status': True}))
        elif handle == PANEL_HOMEPAGE:
            hps_id = request.POST.get('hpsId',None)
            nav_name = request.POST.get('navName', None)
            raw_nav_name = request.POST.get('rawNavName',None)
            view_permissions = request.POST.get('viewPermissions', None)
            view_permissions = view_permissions if view_permissions else None
            filter_conditions = request.POST.get('filterConditions', None)

            models.KmsHomePageSettings.objects.filter(id=hps_id,nav_name=raw_nav_name).update(nav_name=nav_name,
                                                                                              view_permissions_id=view_permissions,
                                                                                              filter_conditions=filter_conditions)

            query_result = models.KmsHomePageSettings.objects.all().values('id','nav_name','view_permissions__id',
                                                                           'view_permissions__name','filter_conditions').order_by('id')
            result_list = list()
            for i in query_result:
                result_dict = {
                    'id':i['id'],
                    'navName':i['nav_name'],
                    'viewPermissions':i['view_permissions__name'] if i['view_permissions__name'] else '',
                    'viewPermissionsId':i['view_permissions__id'],
                    'filterConditions':i['filter_conditions']}
                result_list.append(result_dict)
            return_data = {'status': True, 'query_data': result_list}
            return HttpResponse(json.dumps(return_data))

def delete(request):
    """ 删除数据 """
    if request.method == 'POST':
        handle = request.POST.get('handle', None)
        data_set = request.POST.getlist('dataSet', None)     # 获取需要删除文件的列表
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
                models.KmsKnowledgeClassify.objects.filter(Q(category=i['knowledgeCategory']) & Q(classify_name=i['classifyName'])).delete()
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
        superior_dept_id = request.POST.get('superiorDeptId',None)
        dept_level = request.POST.get('deptLevel',None)
        if superior_dept_id is not None:
            query_result = models.KmsGroup.objects.filter(id=superior_dept_id).values('dept_level__department_level',
                                                                                 'dept_name', 'superior_dept', 'id')
        else:
            query_result = models.KmsGroup.objects.filter(dept_level=dept_level).values('dept_level__department_level',
                                                                                 'dept_name', 'superior_dept', 'id')
        result_list = list()
        for dept_item in query_result:
            result_list.append(dept_item)
            obj = data_processing.Processing()
            sup_dept_name = obj.group_data_join(dept_item['superior_dept'])
            dept_item['dept_name'] = dept_item['dept_name'] + sup_dept_name
        print(result_list)
        return HttpResponse(json.dumps({'status':True, 'query_data': result_list}))

def query_dept_list(request):
    """
    注册人员时获取所有的部门列表
    :param request:
    :return:
    """
    result_list = list()
    query_result = models.KmsGroup.objects.all().values('dept_level__department_level','dept_name', 'superior_dept', 'id')
    for dept_item in query_result:
        result_list.append(dept_item)
        obj = data_processing.Processing()
        sup_dept_name = obj.group_data_join(dept_item['superior_dept'])
        # print(deptItem['dept_name'], supDeptName)
        dept_item['dept_name'] = dept_item['dept_name'] + sup_dept_name
    return HttpResponse(json.dumps({'status': True, 'query_data': result_list}))





