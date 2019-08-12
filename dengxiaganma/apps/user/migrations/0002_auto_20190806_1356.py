# Generated by Django 2.2.3 on 2019-08-06 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to='image/201908/06', verbose_name='用户图片'),
        ),
        migrations.RemoveField(
            model_name='user',
            name='img_head',
        ),
        migrations.AddField(
            model_name='user',
            name='img_head',
            field=models.CharField(default='', max_length=256, verbose_name='头像'),
        ),
        migrations.DeleteModel(
            name='HeadImg',
        ),
    ]