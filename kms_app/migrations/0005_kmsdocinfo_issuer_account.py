# Generated by Django 2.1.3 on 2019-03-08 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kms_app', '0004_auto_20190308_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='kmsdocinfo',
            name='issuer_account',
            field=models.CharField(db_index=True, default=None, max_length=8, verbose_name='用户名'),
        ),
    ]
