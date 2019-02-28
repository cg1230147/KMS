from django.db import models

# Create your models here.

class KmsUser(models.Model):
    uid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, null=False, verbose_name='用户名')
    show_name = models.CharField(max_length=16, null=False, verbose_name='显示名称')
    password = models.CharField(max_length=64, null=False, verbose_name='密码')
    email = models.EmailField(max_length=32, null=True,default=None, verbose_name='邮箱')
    phone_number = models.CharField(max_length=11, null=True, default=None, verbose_name='手机号')

    groups = models.ForeignKey("KmsGroup", "id",)

    class Meta:
        # 创建用户名、密码联合唯一索引：CREATE UNIQUE INDEX index_name ON KmsUser(username, password);
        unique_together = (('username', 'password'),)

class KmsDocInfo(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=64,default=None,unique=True)
    title = models.CharField(max_length=128, verbose_name='标题', default=None,db_index=True)
    issuer = models.CharField(max_length=8, verbose_name='发布人', default=None, db_index=True)
    issuer_dept = models.CharField(max_length=16, verbose_name='发布部门', default=None)
    classify_name = models.CharField(max_length=16, verbose_name='知识分类', default=None)
    release_date = models.DateField(auto_now_add=True, verbose_name='发布时间')
    auditor = models.CharField(max_length=16, verbose_name='审核人', default=None)
    remarks = models.TextField(null=True,blank=True, verbose_name='备注')
    issue_type = models.CharField(max_length=16, verbose_name='发布类型', default=None)
    del_status = models.IntegerField(verbose_name='文档状态', default=0)        # 0 未删除，1 删除
    release_status = models.IntegerField(verbose_name='发布状态', default=0)    # 0 未发布，1 已发布
    examine_status = models.IntegerField(verbose_name='审核状态', default=0)    # 0 未审核通过，1 审核通过
    details = models.TextField(null=True,blank=True,verbose_name='详细内容')
    describe = models.TextField(null=True,blank=True,verbose_name='问题描述')
    solution = models.TextField(null=True,blank=True,verbose_name='解决方案')

    class Meta:
        # indexes = [
        #     models.Index(fields=['title','issuer','classify_name'])
        # ]
        # 组合索引
        index_together = [
            ('title','issuer','classify_name')
        ]

class KmsFilePath(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=64)
    path = models.CharField(max_length=128)
    doc_info = models.ForeignKey("KmsDocInfo", "id",)

class KmsDepartmentLevel(models.Model):
    id = models.AutoField(primary_key=True)
    department_level = models.CharField(max_length=16)
    superior_correlate_id = models.IntegerField()

class KmsGroup(models.Model):
    id = models.AutoField(primary_key=True)
    # 外键关联到KmsDepartmentLevel表，当KmsDepartmentLevel表删除该条数据后，把外键置空
    dept_level = models.ForeignKey(KmsDepartmentLevel,blank=True,null=True, on_delete=models.SET_NULL,)
    # 上级部门名称ID
    superior_dept = models.IntegerField()
    dept_name = models.CharField(max_length=16)

class KmsUserPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=16)
    # 创建用户表和权限表多对多关系
    kms_user = models.ManyToManyField('KmsUser')

class KmsKnowledgeClassify(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=16)
    classify_name = models.CharField(max_length=16)





