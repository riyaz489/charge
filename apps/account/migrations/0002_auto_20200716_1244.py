# Generated by Django 3.0.8 on 2020-07-16 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='image',
            field=models.CharField(default='https://3.bp.blogspot.com/-qDc5kIFIhb8/UoJEpGN9DmI/AAAAAAABl1s/BfP6FcBY1R8/s1600/BlueHead.jpg', max_length=1000),
        ),
        migrations.CreateModel(
            name='AccountSubscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_account', to=settings.AUTH_USER_MODEL)),
                ('following_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='subscribers',
            field=models.ManyToManyField(related_name='related_to', through='account.AccountSubscriber', to=settings.AUTH_USER_MODEL),
        ),
    ]
