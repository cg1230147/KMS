# Generated by Django 2.1.3 on 2019-02-26 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kms_app', '0002_kmsfilepath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kmsdocinfo',
            name='describe',
            field=models.TextField(blank=True, null=True, verbose_name='问题描述'),
        ),
        migrations.AlterField(
            model_name='kmsdocinfo',
            name='details',
            field=models.TextField(blank=True, null=True, verbose_name='详细内容'),
        ),
        migrations.AlterField(
            model_name='kmsdocinfo',
            name='remarks',
            field=models.TextField(blank=True, null=True, verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='kmsdocinfo',
            name='solution',
            field=models.TextField(blank=True, null=True, verbose_name='解决方案'),
        ),
    ]