# Generated by Django 2.1.3 on 2019-03-08 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kms_app', '0007_auto_20190308_1623'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kmsdocinfo',
            old_name='auditor_issuer_account',
            new_name='auditor_account',
        ),
    ]
