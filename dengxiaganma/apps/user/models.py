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

class BlackList(models.Model):
    """黑名单"""
    first_person = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='第一人称ID', default='', related_name='sample3')
    third_person = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='第三人称ID', default='', related_name='sample4')

class CarBrand(models.Model):
    """车品牌"""
    name = models.CharField(max_length=50, verbose_name='品牌名', default='')
    initial = models.CharField(max_length=50, verbose_name='品牌名的拼音/英文名首字母', default='')
    image_filename = models.CharField(max_length=50, verbose_name='品牌图片名', default='')


class CarSeries(models.Model):
    """车系"""
    name = models.CharField(max_length=50, verbose_name='车系名', default='')
    brand = models.ForeignKey('CarBrand', on_delete=models.CASCADE, verbose_name='所属品牌id', default='')

class CarModel(models.Model):
    """车型"""
    name = models.CharField(max_length=50, verbose_name='车型名称', default='')
    price = models.CharField(verbose_name='车型上市时指导价格（w）', default='', max_length=50)
    series = models.ForeignKey('CarSeries', on_delete=models.CASCADE, verbose_name='所属车系id', default='')
    brand = models.ForeignKey('CarBrand', on_delete=models.CASCADE, verbose_name='所属品牌id', default='')

class CarBarn(models.Model):
    """车库"""
    # car_brand = models.CharField(max_length=50, verbose_name='车标', default='')
    # car_brand = models.ForeignKey('CarBrand', on_delete=models.CASCADE, verbose_name='所属品牌id', default='')
    # car_series = models.ForeignKey('CarSeries', on_delete=models.CASCADE, verbose_name='所属车系id', default='')
    # car_type = models.CharField(max_length=50, verbose_name='车型', default='')
    car_model = models.ForeignKey('CarModel', on_delete=models.CASCADE, verbose_name='所属车型id', default='')
    # car_color = models.CharField(max_length=50, verbose_name='颜色', default='')
    # car_value = models.CharField(max_length=50, verbose_name='估值', default='')
    car_person = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='用户ID', default='')

class Activity(models.Model):
    """活动"""
    activity_name = models.ForeignKey('Like', on_delete=models.CASCADE, verbose_name='活动名称', default='')
    activity_type = models.CharField(max_length=50, verbose_name='活动类型', default='')
    activity_issue = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='活动发布人', default='', related_name='sample5')
    activity_join = models.ManyToManyField('User', verbose_name='活动参与者', default='', related_name='sample6')
    activity_time = models.DateTimeField(auto_now_add=True, verbose_name='活动时间')
    activity_area_start = models.CharField(max_length=50, verbose_name='活动出发地', default='')
    activity_area_end = models.CharField(max_length=50, verbose_name='活动目的地', default='')
    activity_person_sex = models.CharField(max_length=50, verbose_name='活动参与人群性别', default='')
    activity_person_num = models.CharField(max_length=50, verbose_name='活动参与人群人数', default='')
    activity_car = models.ForeignKey('CarBarn', on_delete=models.CASCADE, verbose_name='我的出行车辆', default='')
    activity_img = models.CharField(max_length=256, verbose_name='活动添加图片', default='')
    # 活动想法
    activity_content = models.TextField(verbose_name='说说你的想法', default='')

class Topic(models.Model):
    """话题"""
    topic_name = models.CharField(max_length=50, verbose_name='话题名称', default='')
    topic_user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='话题发布人', default='')
    topic_time = models.DateTimeField(auto_now_add=True, verbose_name='话题发布时间')

class User(models.Model):
    """用户"""
    # SIGN_CHOICES = (
    #     ('1', '白羊座'),
    #     ('2', '金牛座'),
    #     ('3', '双子座'),
    #     ('4', '巨蟹座'),
    #     ('5', '狮子座'),
    #     ('6', '处女座'),
    #     ('7', '天秤座'),
    #     ('8', '天蝎座'),
    #     ('9', '射手座'),
    #     ('10', '摩羯座'),
    #     ('11', '水瓶座'),
    #     ('12', '双鱼座'),
    # )
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
    # 行驶证
    driver_licence = models.CharField(max_length=256, verbose_name='行驶证', default='')
    # 驾驶证
    driver_license = models.CharField(max_length=256, verbose_name='驾驶证', default='')
    # 星座
    sign = models.CharField(max_length=50, verbose_name='星座', default='')


    class Meta:
        db_table = 'User'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

