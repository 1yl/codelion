# Generated by Django 2.2.3 on 2019-08-06 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20190806_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='update_time',
        ),
    ]
