# coding:utf-8
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from ..utils.common import Common
from django_redis import get_redis_connection
import json, random
from ..utils import redistools
from ..utils.verifyphone import VerifyPhone
from ..utils.redistools import RedisTools
from ..utils.pictools import PictureParsing, ImageParsing
from ..user.models import *
from django.contrib.auth.hashers import make_password, check_password
import time, datetime
# Create your views here.
# TODO：初始化
class InitView(APIView):
    def get(self, request):
        return Response("111")

# TODO: 日期
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)


# TODO: 发送验证码
class SendSMSView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        # 发送验证码
        """
        sms_code = "%06d" % random.randint(0, 999999)
        # 创建redis连接对象（'verify_codes'表示settings文件中redis配置的选择）
        redis_conn = get_redis_connection("verify_codes")
        # 使用管道
        # print(redis_conn)
        pl = redis_conn.pipeline()
        # 存储短信验证码至redis数据库
        pl.setex("sms_%s" % phone, redistools.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 记录用户发送短信的频次
        pl.setex('send_flag_%s' % phone, redistools.SEND_SMS_CODE_INTERVAL, 1)
        # 指令传递，将数据写入redis
        pl.execute()
        """
        sms_code = RedisTools().linkredis(phone=phone)
        print(sms_code)
        # 获取该号码在redis中的频次
        send_flag = RedisTools().redis_conn.get('send_flag_%s' % phone)
        if int(send_flag) > 1:
            return Response({"msg": "操作太过频繁！", "status": '0'})
        else:
            # 发送短信验证码
            try:
                vp = VerifyPhone(phone=phone, sms_code=sms_code)
                res = vp.send_sms()
                return Response(Common.tureReturn(Common, data=res))
            except Exception as e:
                print(e)
                return Response(Common.falseReturn(Common, data='发送失败'))

# TODO: 用户手机注册
class RegistView(APIView):
    def post(self, request):
        """
        获取json数据
        phone = request.data
        return Response(phone)
        return Response(Common.tureReturn(Common, data=phone))
        """
        phone = request.data.get("phone")
        print(type(phone))
        sms_code = request.data.get("sms_code")
        # 判断用户是否已经注册
        user_obj = User.objects.filter(phone=phone).first()
        if not user_obj:
            # 连接redi
            link_redis = RedisTools()
            # 获取redis中sms_phone的值
            redis_sms_phone = link_redis.redis_conn.get("sms_%s" % phone)
            print(type(redis_sms_phone))
            print(redis_sms_phone)
            # 如果sms_phone不存在
            if not redis_sms_phone:
                return Response(Common.falseReturn(Common, data='验证码已过期'))
            else:
                redis_sms_phone = str(redis_sms_phone, encoding='utf-8')
                # sms_phone存在，判断验证码是否匹配
                if redis_sms_phone != sms_code:
                    # 不匹配
                    return Response(Common.falseReturn(Common, data='验证失败'))
                else:
                    # 匹配
                    add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(str(phone)[5:])
                    # 初始密码手机后6位加密（django哈希加密）
                    password = make_password(str(phone)[5:])
                    print(password)
                    print(len(password))
                    User.objects.create(phone=phone, password=password, add_time=add_time, state_info=0)
                    return Response(Common.tureReturn(Common, data='注册成功'))
        else:
            return Response(Common.falseReturn(Common, data='用户已注册'))


# TODO: 用户手机验证登录
class LoginPhoneView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        sms_code = request.data.get("sms_code")
        # 验证码校验,连接redi
        link_redis = RedisTools()
        # 获取redis中sms_phone的值
        redis_sms_phone = link_redis.redis_conn.get("sms_%s" % phone)
        print(type(redis_sms_phone))
        print(redis_sms_phone)
        # 如果sms_phone不存在
        if not redis_sms_phone:
            return Response(Common.falseReturn(Common, data='验证码已过期'))
        else:
            redis_sms_phone = str(redis_sms_phone, encoding='utf-8')
            # sms_phone存在，判断验证码是否匹配
            if redis_sms_phone != sms_code:
                # 不匹配
                return Response(Common.falseReturn(Common, data='验证失败'))
            else:
                # 匹配,判断用户是否已经存在
                user_obj = User.objects.filter(phone=phone).first()
                # 用户不存在
                if not user_obj:
                    add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(str(phone)[5:])
                    # 初始密码手机后6位加密（django哈希加密）
                    password = make_password(str(phone)[5:])
                    print(password)
                    print(len(password))
                    User.objects.create(phone=phone, password=password, add_time=add_time, state_info=0)
                    return Response(Common.tureReturn(Common, data='登陆成功'))
                # 用户存在
                else:
                    # 修改最后一次登陆时间
                    user_obj.use_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    user_obj.save()
                    if user_obj.state_info == 1:
                        return Response(Common.tureReturn(Common, data='登陆成功,信息已完善'))
                    else:
                        return Response(Common.tureReturn(Common, data='登陆成功,信息未完善'))



# TODO： 用户密码登录
class LoginPwdView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        # 查找是否存在该用户
        user_obj = User.objects.filter(phone=phone).first()
        # 存在即验证密码
        if user_obj:
            # 用户存在且密码正确
            if check_password(password, user_obj.password):
                # 修改最后一次登陆时间
                user_obj.use_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                user_obj.save()
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                if user_obj.state_info == 1:
                    return Response(Common.tureReturn(Common, data='登陆成功,信息已完善'))
                else:
                    return Response(Common.tureReturn(Common, data='登陆成功,信息未完善'))
            # 用户存在密码不正确
            else:
                return Response(Common.falseReturn(Common, data='密码有误，登陆失败'))
        # 不存在则提示用户注册
        else:
            return Response(Common.falseReturn(Common, data='用户不存在，登陆失败'))


# TODO: 忘了密码-用户密码修改
class UpdatePwdView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        # 发送验证码
        RedisTools().linkredis(phone=phone)
        # 获取该号码在redis中的频次
        send_flag = redis_conn.get('send_flag_%s' % phone)
        if int(send_flag) > 1:
            return Response({"msg": "操作太过频繁！", "status": '0'})
        else:
            # 发送短信验证码
            try:
                vp = VerifyPhone(phone=phone, sms_code=sms_code)
                res = vp.send_sms()
            except Exception as e:
                print(e)
                return Response(Common.falseReturn(Common, data='发送失败'))


# TODO: 首次登陆完善信息
class EditInfoFirst(APIView):
    def post(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 用户头像
        img_head = request.data.get("img_head")
        # 用户头像后缀
        suffix = request.data.get("suffix")
        # 用户昵称
        nike = request.data.get("nike")
        # 用户性别
        sex = request.data.get("sex")
        # 获取该用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 头像处理
        img = ImageParsing(img_head, suffix)
        user_obj.img_head = img
        user_obj.sex = sex
        user_obj.username = nike
        user_obj.save()
        return Response(Common.tureReturn(Common, data='保存成功'))


# TODO: 发布照片至照片墙
class PublishPic(APIView):
    def post(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 照片 [{"base64": "xxx", "type": "jpg"}, ...]
        picture = request.data.get("picture")
        # 获取该用户对象
        user_obj = User.objects.filter(phone=phone).first()
        for i in picture:
            img = PictureParsing(i["base64"], i["type"])
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            Image.objects.create(user_id=user_obj.id, image=img, create_time=create_time)
        return Response("ok")


# TODO: 编辑个人信息
class EditInfo(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        nike = request.data.get("nike")
        sex = request.data.get("sex")
        birthday = request.data.get("birthday")
        job = request.data.get("job")
        area = request.data.get("area")
        like = request.data.get("like")
        headimg = request.data.get('headimg')
        # 日期str 转 datetime
        birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d %H:%M:%S')
        # 获取用户对象
        obj = User.objects.get(phone=phone)
        # 头像处理
        img = ImageParsing(headimg["base64"], headimg["type"])
        # 先删除所有与phone的关系
        obj.fan.clear()
        # 可能存在多个爱好
        for i in like:
            # 1.互动聊天  2.美食咖啡  3.唱歌泡吧  4.运动户外  5.电影展览
            # 增加
            obj.fan.add(i)
        obj.img_head = img
        obj.username = nike
        obj.sex = sex
        obj.born_time = birthday
        obj.job = job
        obj.area = area
        obj.save()
        return Response(Common.tureReturn(Common, data='保存成功'))


# TODO: 获取编辑信息
class GetEditInfo(APIView):
    def post(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 获取该用户对象
        user_obj = User.objects.filter(phone=phone).first()
        img_head = user_obj.img_head
        # http:188.131.183.84/dxgm/picture/
        img_head_url = "http:188.131.183.84/dxgm/picture/{0}".format(img_head)
        # 用户昵称
        user_nike = user_obj.username
        # 用户性别
        user_sex = user_obj.sex
        # 用户生日
        user_born = user_obj.born_time
        # datetime 转 str
        user_born = user_born.strftime('%Y-%m-%d %H:%M:%S')
        # 用户职业
        user_job = user_obj.job
        # 用户地区
        user_area = user_obj.area
        # 喜好
        user_fan = user_obj.fan.filter(id=user_obj.id)
        print(user_fan)

        data = {
            "img_head_url": img_head_url,
            "user_nike": user_nike,
            "user_sex": user_sex,
            "user_born": user_born,
            "user_job": user_job,
            "user_area": user_area,
            "user_fan": user_fan,
        }
        # data = json.dumps(data, cls=DateEncoder)
        return Response(Common.tureReturn(Common, data=data))

# TODO: 个人页(含关注、粉丝、黑名单)
class PersonalPage(APIView):
    def post(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 获取该用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 关注人数
        focus_num = 1
        # 粉丝人数
        fans_num = 1
        # 黑名单人数
        blacklist_num = 1
        data = {
            "username": user_obj.username,
            "sex": user_obj.sex,
            "job": user_obj.job,
            "area": user_obj.area,
            "focus_num": focus_num,
            "fans_num": fans_num,
            "blacklist_num": blacklist_num
        }
        return Response(Common.tureReturn(Common, data=data))

# TODO: 关注
class AddFocus(APIView):
    # 添加关注
    def post(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 关注表添加记录
        UserRelation.objects.create(user_id_id=user_obj.id, follower_id_id=id)
        return Response(Common.tureReturn(Common, data='添加关注'))

    # 取消关注
    def delete(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 关注表添加记录
        UserRelation.objects.filter(user_id_id=user_obj.id, follower_id_id=id).delete()
        return Response(Common.tureReturn(Common, data='取消关注'))

    def get(self, request):
        phone = request.data.get("phone")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        print(phone)
        return Response('q')