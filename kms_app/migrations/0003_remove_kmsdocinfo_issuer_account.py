# Generated by Django 2.1.3 on 2019-03-08 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kms_app', '0002_auto_20190308_1616'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kmsdocinfo',
            name='issuer_account',
        ),
    ]
