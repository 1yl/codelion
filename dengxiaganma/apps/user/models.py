# coding:utf-8
from django.db import models
import datetime
import django.utils.timezone as timezone
# Create your models here.
class Image(models.Model):
    """图片"""
    # image = models.ImageField(upload_to=str('image/{time}'.format(time=str(datetime.date.today().strftime("%Y%m/%d")))), verbose_name='用户图片')
    image = models.CharField(max_length=256, verbose_name='图片', default='')
    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='图片上传时间')
    # update_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='图片更改时间')
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='用户ID')


    class Meta:
        db_table = 'Image'
        verbose_name = '图片'
        verbose_name_plural = verbose_name


class Like(models.Model):
    """喜好"""
    # 1.互动聊天  2.美食咖啡  3.唱歌泡吧  4.运动户外  5.电影展览
    likename = models.CharField(max_length=50, verbose_name='喜好')


    class Meta:
        db_table = 'Like'
        verbose_name = '喜好'
        verbose_name_plural = verbose_name

class UserRelation(models.Model):
    """用户关注表"""
    user_id = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='用户ID', default='', related_name='sample1')
    follower_id = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='被关注者用户ID', default='',  related_name='sample2')


class User(models.Model):
    """用户"""
    username = models.CharField(max_length=50, verbose_name='用户昵称')
    phone = models.CharField(max_length=50, verbose_name='手机号')
    password = models.CharField(max_length=128, verbose_name='密码')
    add_time = models.DateTimeField(default=timezone.now, verbose_name='注册时间')
    use_time = models.DateTimeField(auto_now_add=True, verbose_name='最近登录时间')
    born_time = models.DateTimeField(auto_now_add=True, verbose_name='出生日期')
    # 1:man  0:woman
    sex = models.BooleanField(blank=True, verbose_name='性别')
    job = models.CharField(max_length=50, verbose_name='职业')
    # 1: 已完善  0： 未完善
    state_info = models.BooleanField(blank=True, verbose_name='信息是否完善')
    # 喜好
    fan = models.ManyToManyField(Like, verbose_name='喜好')
    # 头像
    img_head = models.CharField(max_length=256, verbose_name='头像', default='')
    # 地区
    area = models.CharField(max_length=50, verbose_name='地区', default='')


    class Meta:
        db_table = 'User'
        verbose_name = '用户'
        verbose_name_plural = verbose_name



