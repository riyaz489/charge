# Generated by Django 3.0.8 on 2020-07-14 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20200714_1038'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='blog_data',
            new_name='BlogData',
        ),
    ]
