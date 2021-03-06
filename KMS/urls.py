"""KMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from kms_app import views
from django.conf.urls.static import static
from django.conf.urls import url
from django.views import static as vs
from KMS import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$', views.login, name=''),
    re_path(r'login/$', views.login, name='login',),
    # index
    re_path(r'index/$', views.index, name='index'),
    re_path(r'query_index_data/$', views.query_index_data, name='query_index_data'),
    re_path(r'logout/$', views.logout, name='logout'),
    re_path(r'classify/', views.classify, name='classify'),
    re_path(r'search/', views.search, name='search'),
    # release
    re_path(r'release/$', views.release, name='release'),
    re_path(r'media_upload/', views.media_upload, name='media_upload'),
    re_path(r'att_upload/', views.attachment_upload, name='att_upload'),
    re_path(r'del_doc_file/', views.del_doc_file, name='del_doc_file'),
    re_path(r'del_all_att/', views.del_all_att, name='del_all_att'),
    re_path(r'del_doc', views.del_doc, name='del_doc'),
    re_path(r'save_doc/', views.save_doc, name='save_doc'),
    # viewForm
    re_path(r'view_form', views.view_form, name='view_form'),
    # center
    re_path(r'center/$', views.center, name='center'),
    re_path(r'user_info/', views.user_info, name='user_info'),
    # manage
    re_path(r'manage/$', views.manage, name='manage'),
    re_path(r'add/', views.add, name='add'),
    re_path(r'query/', views.query, name='query'),
    re_path(r'edit/', views.edit, name='edit'),
    re_path(r'del/', views.delete, name='del'),
    re_path(r'query_dept_level/', views.query_dept_level, name='query_dept_level'),
    re_path(r'query_dept_list', views.query_dept_list, name='query_dept_list'),

    # 关闭debug模式后设置静态文件和media访问方式
    url(r'^static/(?P<path>.*)$', vs.serve,{'document_root': settings.STATIC_ROOT}, name='static'),
    url(r'^upload_files/(?P<path>.*)$', vs.serve,{'document_root': settings.MEDIA_ROOT}, name='upload_files'),

]
# 上传文件url路径
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


