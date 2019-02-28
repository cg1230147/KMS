# Generated by Django 2.1.3 on 2019-02-26 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KmsDepartmentLevel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('department_level', models.CharField(max_length=16)),
                ('superior_correlate_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='KmsDocInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('uuid', models.CharField(default=None, max_length=64, unique=True)),
                ('title', models.CharField(db_index=True, default=None, max_length=128, verbose_name='标题')),
                ('issuer', models.CharField(db_index=True, default=None, max_length=8, verbose_name='发布人')),
                ('issuer_dept', models.CharField(default=None, max_length=16, verbose_name='发布部门')),
                ('classify_name', models.CharField(default=None, max_length=16, verbose_name='知识分类')),
                ('release_date', models.DateField(auto_now_add=True, verbose_name='发布时间')),
                ('auditor', models.CharField(default=None, max_length=16, verbose_name='审核人')),
                ('remarks', models.TextField(blank=True, verbose_name='备注')),
                ('issue_type', models.CharField(default=None, max_length=16, verbose_name='发布类型')),
                ('del_status', models.IntegerField(default=0, verbose_name='文档状态')),
                ('release_status', models.IntegerField(default=0, verbose_name='发布状态')),
                ('examine_status', models.IntegerField(default=0, verbose_name='审核状态')),
                ('details', models.TextField(verbose_name='详细内容')),
                ('describe', models.TextField(verbose_name='问题描述')),
                ('solution', models.TextField(verbose_name='解决方案')),
            ],
        ),
        migrations.CreateModel(
            name='KmsGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('superior_dept', models.IntegerField()),
                ('dept_name', models.CharField(max_length=16)),
                ('dept_level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kms_app.KmsDepartmentLevel')),
            ],
        ),
        migrations.CreateModel(
            name='KmsKnowledgeClassify',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(max_length=16)),
                ('classify_name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='KmsUser',
            fields=[
                ('uid', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=32, verbose_name='用户名')),
                ('show_name', models.CharField(max_length=16, verbose_name='显示名称')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
                ('email', models.EmailField(default=None, max_length=32, null=True, verbose_name='邮箱')),
                ('phone_number', models.CharField(default=None, max_length=11, null=True, verbose_name='手机号')),
                ('groups', models.ForeignKey(on_delete='id', to='kms_app.KmsGroup')),
            ],
        ),
        migrations.CreateModel(
            name='KmsUserPermissions',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=16)),
                ('kms_user', models.ManyToManyField(to='kms_app.KmsUser')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='kmsdocinfo',
            index_together={('title', 'issuer', 'classify_name')},
        ),
        migrations.AlterUniqueTogether(
            name='kmsuser',
            unique_together={('username', 'password')},
        ),
    ]
