# Generated by Django 3.0.8 on 2020-07-24 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20200724_2102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='otp',
        ),
        migrations.RemoveField(
            model_name='account',
            name='otp_timestamp',
        ),
    ]
