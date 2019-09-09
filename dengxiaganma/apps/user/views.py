# coding:utf-8
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from ..utils.common import Common
from django_redis import get_redis_connection
import json, random
from ..utils import signtools
from ..utils import redistools
from ..utils.verifyphone import VerifyPhone
from ..utils.redistools import RedisTools
from ..utils.publishtools import postActivity
from ..utils.pictools import PictureParsing, ImageParsing, LicenceParsing, LicenseParsing, Parsing
from ..user.models import *
from django.contrib.auth.hashers import make_password, check_password
import datetime, time
import time
from rest_framework.pagination import PageNumberPagination
from dengxiaganma.settings import WEB_HOST_NAME, WEB_IMAGE_SERVER_PATH, WEB_PICTURE_SERVER_PATH, WEB_LICENCE_SERVER_PATH, WEB_LICENSE_SERVER_PATH, WEB_ACTIVITY_SERVER_PATH
from ..user.serializer import ActivitySerializer
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

# TODO: 分页功能自定义类
class MyPageNumberPagination(PageNumberPagination):
    # 默认每页显示的数据条数
    page_size = 10
    # 获取 url 参数中设置的每页显示数据条数
    page_size_query_param = 'size'
    # 最大支持的每页显示的数据条数
    max_page_size = 10
    # 获取 url 参数中传入的页码 key
    page_query_param = 'page'


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
                    User.objects.create(phone=phone, password=password, add_time=add_time, state_info='0')
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
                    # 初始密码手机后6位加密（django哈希加密）
                    password = make_password(str(phone)[5:])
                    User.objects.create(phone=phone, password=password, add_time=add_time, state_info='0')
                    user_obj = User.objects.filter(phone=phone).first()
                    data = {
                        "pid": user_obj.id,
                        "details": '首次登陆成功'
                    }
                    return Response(Common.tureReturn(Common, data=data))
                # 用户存在
                else:
                    # 修改最后一次登陆时间
                    user_obj.use_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    user_obj.save()
                    if user_obj.state_info == '0':
                        data = {
                            "pid": user_obj.id,
                            "details": '登陆成功,信息未完善'
                        }
                        return Response(Common.tureReturn(Common, data=data))
                    else:
                        data = {
                            "pid": user_obj.id,
                            "details": '登陆成功,信息已完善'
                        }
                        return Response(Common.tureReturn(Common, data=data))

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
                if user_obj.state_info == '0':
                    data = {
                        "pid": user_obj.id,
                        "details": '登陆成功,信息未完善'
                    }
                    return Response(Common.tureReturn(Common, data=data))
                else:
                    data = {
                        "pid": user_obj.id,
                        "details": '登陆成功,信息已完善'
                    }
                    return Response(Common.tureReturn(Common, data=data))
            # 用户存在密码不正确
            else:
                return Response(Common.falseReturn(Common, data='密码有误，登陆失败'))
        # 不存在则提示用户注册
        else:
            return Response(Common.falseReturn(Common, data='用户不存在，登陆失败'))


# TODO: 忘了密码-用户密码修改
class UpdatePwdView(APIView):
    def post(self, request):
        pid = request.data.get("pid")
        sms_code = request.data.get("sms_code")
        new_pwd = request.data.get("new_pwd")
        # 验证码校验,连接redi
        link_redis = RedisTools()
        # 获取redis中sms_phone的值
        redis_sms_phone = link_redis.redis_conn.get("sms_%s" % phone)
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
                user_obj = User.objects.filter(id=pid).first()
                # 用户不存在
                if not user_obj:
                    return Response(Common.falseReturn(Common, data='该用户未注册'))
                # 用户存在
                else:
                    # 密码加密
                    password = make_password(new_pwd)
                    # 更改密码
                    user_obj.password = password
                    # 修改最后一次登陆时间
                    user_obj.use_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    user_obj.save()
                    if user_obj.state_info == '0':
                        return Response(Common.tureReturn(Common, data='该用户信息未完善'))
                    else:
                        return Response(Common.tureReturn(Common, data='该用户信息已完善'))


# TODO: 首次登陆完善信息
class EditInfoFirst(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 用户头像
        img_head = request.data.get("img_head")
        # 用户头像后缀
        suffix = request.data.get("suffix")
        # 用户昵称
        nike = request.data.get("nike")
        # 用户性别
        sex = request.data.get("sex")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 头像处理
        print(pid)
        print(img_head)
        print(suffix)
        print(nike)
        print(sex)
        print(user_obj)
        if img_head != '' and suffix != '':
            img = ImageParsing(img_head, suffix)
            user_obj.img_head = img
            user_obj.sex = sex
            user_obj.username = nike
            user_obj.state_info = '1'
            user_obj.save()
            return Response(Common.tureReturn(Common, data='保存成功'))
        else:
            return Response(Common.falseReturn(Common, data='保存失败'))


# TODO: 发布照片至照片墙
class PublishPic(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 照片 [{"base64": "xxx", "type": "jpg"}, ...]
        picture = request.data.get("picture")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        for i in picture:
            if i["base64"] != '' and i["type"]:
                img = PictureParsing(i["base64"], i["type"])
            else:
                img = ''
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            Image.objects.create(user_id=user_obj.id, image=img, create_time=create_time)
        return Response(Common.tureReturn(Common, data='照片上传成功'))


# TODO: 点击更换头像
class ChangeHeadImg(APIView):
    def put(self, request):
        # 获取用户手机号
        pid = request.data.get("pid")
        # 获取用户头像
        headimg = request.data.get("headimg")
        # 用户头像后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 头像处理
        if headimg != '' and suffix != '':
            img = ImageParsing(headimg, suffix)
            user_obj.img_head = img
            user_obj.save()
            return Response(Common.tureReturn(Common, data='头像更换成功'))
        else:
            return Response(Common.falseReturn(Common, data='头像未更换'))


# TODO: 编辑个人信息
class EditInfo(APIView):
    def post(self, request):
        print(request.data.get('headimg'))
        pid = request.data.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        nike = request.data.get("nike")
        sex = request.data.get("sex")
        birthday = request.data.get("birthday")
        job = request.data.get("job")
        area = request.data.get("area")
        like = request.data.get("like")
        headimg = request.data.get('headimg')
        print(headimg)
        if birthday != '':
            # 日期str 转 datetime
            birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d %H:%M:%S')
            # 保存用户信息
            obj.born_time = birthday
            # 星座处理
            # datetime 转 str
            birthday = birthday.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(birthday, '%Y-%m-%d')
            res = signtools.person_sign(birth.month, birth.day)
            obj.sign = res
        # 头像处理
        if headimg["base64"] != '' and headimg["type"] != '':
            img = PictureParsing(headimg["base64"], headimg["type"])
            obj.img_head = img
        # 先删除所有与phone的关系
        obj.fan.clear()
        # 可能存在多个爱好
        for i in like:
            # 1.互动聊天  2.美食咖啡  3.唱歌泡吧  4.运动户外  5.电影展览
            # 增加
            obj.fan.add(i)
        obj.username = nike
        obj.sex = sex
        obj.job = job
        obj.area = area
        obj.coin = "2000"
        obj.state_info = '2'
        obj.save()
        return Response(Common.tureReturn(Common, data='保存成功'))


# TODO: 获取编辑信息
class GetEditInfo(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        img_head = user_obj.img_head
        # http:188.131.183.84/dxgm/picture/
        img_head_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(img_head)
        # 用户昵称
        user_nike = user_obj.username
        # 用户性别
        user_sex = user_obj.sex
        # 用户生日
        user_born = user_obj.born_time
        # datetime 转 str
        user_born = user_born.strftime('%Y-%m-%d')
        # 用户职业
        user_job = user_obj.job
        # 用户地区
        user_area = user_obj.area
        # 喜好
        user_fan = user_obj.fan.all()
        fan_lis = []
        if len(user_fan) > 0:
            for i in user_fan:
                fan_lis.append(i.id)
        data = {
            "img_head_url": img_head_url,
            "user_nike": user_nike,
            "user_sex": user_sex,
            "user_born": user_born,
            "user_job": user_job,
            "user_area": user_area,
            "user_fan": fan_lis,
        }
        return Response(Common.tureReturn(Common, data=data))

# TODO: 个人页(含关注、粉丝、黑名单)
class PersonalPage(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 关注人数
        focus_num = UserRelation.objects.filter(user_id_id=user_obj.id).count()
        # focus_num = 1
        # 粉丝人数
        fans_num = UserRelation.objects.filter(follower_id_id=user_obj.id).count()
        # fans_num = 1
        # 黑名单人数
        blacklist_num = BlackList.objects.filter(third_person_id=user_obj.id).count()
        # blacklist_num = 1
        # datetime 转 str
        user_obj.born_time = user_obj.born_time.strftime('%Y-%m-%d')
        # 用-分割学生的出生日期，获取年月日
        if user_obj.born_time != '':
            birth = datetime.datetime.strptime(user_obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year - birth.year - 1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year - birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year - birth.year - 1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year - birth.year
        else:
            age = ''
        # 头像
        print(user_obj.img_head)
        img_head_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(user_obj.img_head)
        data = {
            "username": user_obj.username,
            "sex": user_obj.sex,
            "job": user_obj.job,
            "area": user_obj.area,
            "focus_num": focus_num,
            "sign": user_obj.sign,
            "head_img": img_head_url,
            "age": age,
            "fans_num": fans_num,
            "blacklist_num": blacklist_num
        }
        print(data)
        return Response(Common.tureReturn(Common, data=data))

# TODO: 关注
class AddFocus(APIView):
    # 添加关注
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 关注表添加记录
        UserRelation.objects.create(user_id_id=user_obj.id, follower_id_id=id)
        return Response(Common.tureReturn(Common, data='添加关注'))

    # 取消关注
    def delete(self, request):
        # 用户手机号
        pid = request.GET.get("pid")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.GET.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 关注表删除记录
        UserRelation.objects.filter(user_id_id=user_obj.id, follower_id_id=id).delete()
        return Response(Common.tureReturn(Common, data='取消关注'))


# TODO: 黑名单
class AddBlackList(APIView):
    # 添加黑名单
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 将第三人称加入黑名单
        BlackList.objects.create(first_person_id=user_obj.id, third_person_id=id)
        # 第一人称关注第三人称
        i_care = UserRelation.objects.filter(user_id_id=user_obj.id, follower_id_id=id).first()
        # 第一人称被第三人称关注
        be_focused = UserRelation.objects.filter(user_id_id=id, follower_id_id=user_obj.id).first()
        # 加入黑名单即解除双方关注关系
        if i_care and be_focused:
            # 双方关注
            i_care.delete()
            be_focused.delete()
        elif be_focused:
            # 被关注
            be_focused.delete()
        elif i_care:
            # 我关注
            i_care.delete()
        return Response(Common.tureReturn(Common, data='加入黑名单'))


    # 移除黑名单
    def delete(self, request):
        # 用户手机号
        pid = request.GET.get("pid")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.GET.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 黑名单表删除记录
        BlackList.objects.filter(first_person_id=user_obj.id, third_person_id=id).delete()
        return Response(Common.tureReturn(Common, data='移除黑名单'))


# TODO: 我的关注
class MyFocus(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取我的关注人员信息
        myfocus_lis = UserRelation.objects.filter(user_id_id=user_obj.id)
        lis = []
        for i in myfocus_lis:
            myfocus_obj = User.objects.filter(id=i.follower_id_id).first()
            # 根据出生年月计算年龄
            # datetime 转 str
            myfocus_obj.born_time = myfocus_obj.born_time.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(myfocus_obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year-birth.year-1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year-birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year-birth.year-1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year-birth.year
            dic = {
                "id": myfocus_obj.id,
                "username": myfocus_obj.username,
                "sex": myfocus_obj.sex,
                "age": age,
                "head_img": myfocus_obj.head_img,
                "job": myfocus_obj.job,
                "focus_state": "已关注"
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 我的粉丝
class MyFans(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取关注我的人员信息
        focusme_lis = UserRelation.objects.filter(follower_id_id=user_obj.id)
        lis = []
        for i in focusme_lis:
            focusme_obj = User.objects.filter(id=i.user_id_id).first()
            # 根据出生年月计算年龄
            # datetime 转 str
            focusme_obj.born_time = focusme_obj.born_time.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(focusme_obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year - birth.year - 1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year - birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year - birth.year - 1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year - birth.year
            # 获取我的粉丝关注状态（关注/互相关注）
            togather = UserRelation.objects.filter(follower_id_id=focusme_obj.id).first()
            if togather:
                focus_state = "互相关注"
            else:
                focus_state = "关注"
            dic = {
                "id": focusme_obj.id,
                "username": focusme_obj.username,
                "sex": focusme_obj.sex,
                "age": age,
                "job": focusme_obj.job,
                "head_img": focusme_obj.head_img,
                "focus_state": focus_state
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 我的黑名单
class MyBlackList(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取我的黑名单人员信息
        black_list = BlackList.objects.filter(first_person_id=user_obj.id)
        lis = []
        for i in black_list:
            black_obj = User.objects.filter(id=i.third_person_id).first()
            # 根据出生年月计算年龄
            # datetime 转 str
            black_obj.born_time = black_obj.born_time.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(black_obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year - birth.year - 1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year - birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year - birth.year - 1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year - birth.year
            dic = {
                "id": black_obj.id,
                "username": black_obj.username,
                "sex": black_obj.sex,
                "age": age,
                "job": black_obj.job,
                "head_img": black_obj.head_img,
                "black_state": "移除"
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# # TODO: 条件筛选
# class ConditionFilter(APIView):
#     def get(self, request):
#         # 用户手机号
#         phone = request.data.get("phone")
#         # 获取用户对象
#         user_obj = User.objects.filter(phone=phone).first()
#         # 获取兴趣(['1','2'])
#         like_list = request.data.get("like")
#         sex = request.data.get("sex")
#         person_num = request.data.get("person_num")
#         person_start = request.data.get("person_start")
#         # (['20', '99'])
#         age_list = request.data.get("age_list")
#         face_score_list = request.data.get("face_score_list")
#         time_list = request.data.get("time_list")
#         distance_list = request.data.get("distance_list")


# TODO: 我的车库
class Mycars(APIView):
    def get(self, request):
        # 用户手机号
        pid = request.GET.get("pid")
        print(pid)
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取用户车库
        carbarn_list = CarBarn.objects.filter(car_person_id=user_obj.id)
        lis = []
        for i in carbarn_list:
            # 获取单车辆车型
            single_model_obj = CarModel.objects.filter(id=i.car_model_id)
            # 根据车型获取车的详细信息
            # 车品牌  车系列
            # brand_id  series_id
            single_brand_obj = CarBrand.objects.filter(id=single_model_obj[0].brand_id)
            single_series_obj = CarSeries.objects.filter(id=single_model_obj[0].series_id)
            if single_model_obj[0].price == '':
                price = ''
            else:
                price = single_model_obj[0].price.split('-')[1]
            dic = {
                "car_id": i.id,
                "car_brand_name": single_brand_obj[0].name,
                "car_series_name": single_series_obj[0].name,
                "car_model_name": single_model_obj[0].name,
                "car_price": price,
                "car_initial": single_brand_obj[0].initial,
                "car_image_filename": single_brand_obj[0].image_filename,
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))

    # 车辆信息
    def post(self, request):
        # 车辆id
        car_id = request.data.get("car_id")
        # 车辆信息
        car_obj = CarBarn.objects.filter(id=car_id).first()
        # 获取单车辆车型
        single_model_obj = CarModel.objects.filter(id=car_obj.car_model_id).first()
        # 根据车型获取车的详细信息
        single_brand_obj = CarBrand.objects.filter(id=single_model_obj.brand_id).first()
        single_series_obj = CarSeries.objects.filter(id=single_model_obj.series_id).first()
        if single_model_obj.price == '':
            price = ''
        else:
            price = single_model_obj.price.split('-')[1]
        dic = {
            "car_id": car_id,
            "car_brand_name": single_brand_obj.name,
            "car_series_name": single_series_obj.name,
            "car_model_name": single_model_obj.name,
            "car_price": price,
            "car_initial": single_brand_obj.initial,
            "car_image_filename": single_brand_obj.image_filename,
        }
        return Response(Common.tureReturn(Common, data=dic))

    # 添加车辆（修改）
    def put(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取车辆型号
        car_model_name = request.data.get("car_model_name")
        # 根据车辆型号获取车辆对象
        single_model_obj = CarModel.objects.filter(name=car_model_name).first()
        # 保存车辆信息至我的车库
        CarBarn.objects.create(car_model_id=single_model_obj.id, car_person_id=user_obj.id)
        # 获取行驶证
        driver_licence = request.data.get("driver_licence")
        # 用户行驶证后缀
        licence_suffix = request.data.get("licence_suffix")
        if driver_licence != '' and licence_suffix != '':
            img = LicenceParsing(driver_licence, licence_suffix)
            user_obj.driver_licence = img
        # 获取驾驶证
        driver_license = request.data.get("driver_license")
        # 用户驾驶证后缀
        license_suffix = request.data.get("license_suffix")
        if driver_licence != '' and licence_suffix != '':
            img = LicenseParsing(driver_license, license_suffix)
            user_obj.driver_license = img
        # 判断该用户是否已存在驾驶证和行驶证
        user_obj.save()
        return Response(Common.tureReturn(Common, data='添加车辆成功'))

    # 删除车库中指定车辆
    def delete(self, request):
        # 车辆id
        # car_id = request.data.get("car_id")
        car_id = request.GET.get("car_id")
        print(car_id)
        # 车辆信息
        car_obj = CarBarn.objects.filter(id=car_id).first()
        print(car_obj)
        car_obj.delete()
        return Response(Common.tureReturn(Common, data='删除车辆成功'))


# TODO: 行驶证上传
class UploadLicence(APIView):
    def put(self, request):
        # 获取用户手机号
        pid = request.data.get("pid")
        # 获取用户行驶证
        licence = request.data.get("licence")
        # 用户行驶证后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 行驶证处理
        if licence != '' and suffix != '':
            img = LicenceParsing(licence, suffix)
            user_obj.driver_licence = img
            user_obj.save()
            return Response(Common.tureReturn(Common, data='行驶证上传成功'))
        else:
            return Response(Common.falseReturn(Common, data='行驶证未上传'))


# TODO: 驾驶证上传
class UploadLicense(APIView):
    def put(self, request):
        # 获取用户手机号
        pid = request.data.get("pid")
        # 获取用户驾驶证
        license = request.data.get("license")
        # 用户驾驶证后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 驾驶证处理
        if license != '' and suffix != '':
            img = LicenseParsing(license, suffix)
            user_obj.driver_license = img
            user_obj.save()
            return Response(Common.tureReturn(Common, data='驾驶证上传成功'))
        else:
            return Response(Common.falseReturn(Common, data='驾驶证未上传'))

# TODO: 发布邀约
class IssueInvitation(APIView):
    def get(self, request):
        like_list = Like.objects.all()
        lis = []
        for i in like_list:
            lis.append(i.likename)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 发布活动点击单人或者多人跳转活动发布页面时话题的读取
class TopicExist(APIView):
    def post(self, request):
        # 获取发布人手机号
        pid = request.data.get("pid")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取发布人所发表的话题（最近4条）
        all_topic_list = Topic.objects.filter(topic_user_id=user_obj.id)
        list1 = []
        if len(all_topic_list) >= 4:
            all_topic_list=all_topic_list[-4:]
            for i in all_topic_list:
                list1.append(i.topic_name)
        elif len(all_topic_list) == 3:
            for i in all_topic_list:
                list1.append(i.topic_name)
                list1.extend(["#中国有14亿护旗手"])
        elif len(all_topic_list) == 2:
            for i in all_topic_list:
                list1.append(i.topic_name)
                list1.extend(["#中国有14亿护旗手","#在田子坊的酒吧偶遇"])
        elif len(all_topic_list) == 1:
            for i in all_topic_list:
                list1.append(i.topic_name)
                list1.extend(["#中国有14亿护旗手","#在田子坊的酒吧偶遇","#清吧约一波"])
        else:
            list1.extend(["#中国有14亿护旗手","#在田子坊的酒吧偶遇","#清吧约一波","#KTV麦霸"])
        return Response(Common.tureReturn(Common, data=list1))


# TODO: 唱歌泡吧
class SingingBar(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        postActivity(request)
        return Response(Common.tureReturn(Common, data='唱歌泡吧活动发布成功'))

    # 活动编辑
    def put(self, request):
        # 调用基类
        pass


# TODO: 互动聊天
class ChatInteraction(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        postActivity(request)
        return Response(Common.tureReturn(Common, data='互动聊天活动发布成功'))

    # 活动编辑
    def put(self, request):
        # 调用基类
        pass

# TODO: 美食咖啡
class GourmetCoffee(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        postActivity(request)
        return Response(Common.tureReturn(Common, data='美食咖啡活动发布成功'))

# TODO: 运动户外
class SportsOutdoors(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        postActivity(request)
        return Response(Common.tureReturn(Common, data='运动户外活动发布成功'))
    
# TODO: 电影展览
class FilmFair(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        postActivity(request)
        return Response(Common.tureReturn(Common, data='电影展览活动发布成功'))


# TODO: 他的主页
class HisHomePage(APIView):
    def post(self, request):
        # 获取他的id
        his_id = request.data.get("id")
        # 获取我的主键id
        pid = request.data.get("pid")
        # 获取他这个人的对象
        his_obj = User.objects.filter(id=his_id).first()
        # 获取他这个人的图片
        Image_list = Image.objects.filter(user_id=his_obj.id)
        # 获取我的关注人员信息
        myfocus_exist = UserRelation.objects.filter(user_id_id=pid, follower_id_id=his_id).first()
        if myfocus_exist:
            focus_status = '0'
        else:
            focus_status = '1'
        # 计算年龄
        # datetime 转 str
        his_obj.born_time = his_obj.born_time.strftime('%Y-%m-%d')
        # 用-分割学生的出生日期，获取年月日
        birth = datetime.datetime.strptime(his_obj.born_time, '%Y-%m-%d')
        # 获取今天的日期
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        # 分割今天的日期获取年月日
        now = datetime.datetime.strptime(now, '%Y-%m-%d')
        # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
        if now.month < birth.month:
            age = now.year - birth.year - 1
        # 如果学生月份比今天小，他过生日了，则年份相减
        if now.month > birth.month:
            age = now.year - birth.year
        # 如果月份相等，学生日比今天大，他没过生日
        if now.month == birth.month and now.day < birth.day:
            age = now.year - birth.year - 1
        # 如果月份相等，学生日比今天小，他过生日了
        if now.month == birth.month and now.day > birth.day:
            age = now.year - birth.year
        # 相册
        list1 = []
        if len(Image_list) > 0:
            for i in Image_list:
                list1.append(i.image)
        # 背景图片
        if len(Image_list) > 0:
            back_img = "http:52.80.194.137:8001/dxgm/picture/{0}".format(Image_list.last().image)
        else:
            back_img = ''
        # 他的邀约 即 他发布的活动
        all_activities = Activity.objects.filter(activity_issue_id=his_id)
        list2 = []
        if len(all_activities) > 0:
            for j in all_activities:
                ac_name = Like.objects.filter(id=j.activity_name_id).first().likename
                dic = {
                    "ac_id": j.id,
                    "ac_name": ac_name
                }
                list2.append(dic)
        # 他参与的话题
        top_list = Topic.objects.filter(topic_user_id=his_id)
        list3 = []
        if len(top_list) > 0:
            for z in top_list:
                result = z.topic_join.all()
                if len(result) > 0:
                    list3.append(z.topic_name)
        # 可能出现信息未完善
        data = {
            # 头像
            "img_head": "http:52.80.194.137:8001/dxgm/picture/{0}".format(his_obj.img_head),
            # 背景图片(默认最后一张)
            "back_img": back_img,
            # 昵称
            "nike_name": his_obj.username,
            # 关注情况（关注/取消关注）(0代表取消关注）
            "focus_status": focus_status,
            "user_sex": his_obj.sex,
            "user_age": age,
            "user_job": his_obj.job,
            "user_area": his_obj.area,
            "pic_list": list1,
            "ac_invite": list2,
            "topic_list": list3,
            # "userAgent": userAgent
        }
        return Response(Common.tureReturn(Common, data=data))


# TODO: 获取所有车型
class GetAllCarBrand(APIView):
    def get(self, request):
        all_carmodels = CarBrand.objects.all()
        lis = []
        for i in all_carmodels:
            data = {
                "id": i.id,
                "model_name": i.name,
                "model_initial": i.initial,
                "model_imagefilename": "http:52.80.194.137:8001/dxgm/car_logo/{0}".format(i.image_filename),
            }
            lis.append(data)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 根据某一车型获取该车型系列
class GetAllCarSeriseByBrand(APIView):
    def post(self, request):
        car_brand_id = request.data.get("car_brand_id")
        car_series_list = CarSeries.objects.filter(brand_id=car_brand_id)
        lis = []
        for i in car_series_list:
            data = {
                "id": i.id,
                "series_name": i.name
            }
            lis.append(data)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 根据某系列车获取该系列所有车型
class GetAllCarModelBySeries(APIView):
    def post(self, request):
        car_series_id = request.data.get("car_series_id")
        car_model_list = CarModel.objects.filter(series_id=car_series_id)
        lis = []
        for i in car_model_list:
            if i.price == '':
                price = ''
            else:
                price = i.price.split('-')[1]
            data = {
                "id": i.id,
                "model_name": i.name,
                "model_price": price,
            }
            lis.append(data)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 邀请他参与我的话题-获取话题列表
class InviteTopic(APIView):
    def post(self, request):
        # 获取我的主键id
        pid = request.data.get("pid")
        # user_obj = User.objects.filter(id=pid).first()
        # 获取我的话题列表
        topic_list = Topic.objects.filter(topic_user_id=pid)
        lis1 = []
        if len(topic_list) > 0:

            for i in topic_list:
                dic = {
                    "id": i.id,
                    "topic_name": i.topic_name
                }
                lis1.append(dic)
        return Response(Common.tureReturn(Common, data=lis1))


# TODO: 邀请他参与我的活动-获取活动列表
class InviteTopic(APIView):
    def post(self, request):
        # 获取我的主键id
        pid = request.data.get("pid")
        # user_obj = User.objects.filter(id=pid).first()
        # 获取我的话题列表
        topic_list = Topic.objects.filter(topic_user_id=pid)
        lis1 = []
        if len(topic_list) > 0:

            for i in topic_list:
                dic = {
                    "id": i.id,
                    "topic_name": i.topic_name
                }
                lis1.append(dic)
        return Response(Common.tureReturn(Common, data=lis1))


# TODO: 邀请他参与我的话题
class InviteTop(APIView):
    def post(self, request):
        # 连接redis
        topic_redis = get_redis_connection("topic")
        # 获取我的主键id
        pid = request.data.get("pid")
        # 获取对方主键id
        hid = request.data.get("hid")
        # 获取话题
        topic_id = request.data.get("topic_id")
        top_obj = Topic.objects.filter(id=topic_id).first()
        p_person = User.objects.filter(id=pid).first()
        h_person = User.objects.filter(id=hid).first()


# TODO: 判断信息是否已全部完善
class JudgeState(APIView):
    def get(self, request):
        # 用户id
        pid = request.GET.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        # 判断状态
        if obj.state_info == "2":
            return Response(Common.tureReturn(Common, data=True))
        else:
            return Response(Common.tureReturn(Common, data=False))


# TODO: 点击发布扣除点数
class ReduceCoin(APIView):
    def get(self, request):
        # 用户id
        pid = request.GET.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        # 判断点数是否充足
        if int(obj.coin) >= 0:
            return Response(Common.tureReturn(Common, data=True))
        else:
            return Response(Common.tureReturn(Common, data=False))


# TODO: 个人活动列表
class ActivityPaging(APIView):
    def post(self, request):
        # 用户id
        pid = request.data.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        # 获取该用户相关活动
        all_activity_objects = Activity.objects.filter(activity_issue_id=obj.id)
        # 图片数量
        pic_num = Image.objects.filter(user_id=obj.id).count()
        # 图片列表
        pic_obj_list = Image.objects.filter(user_id=obj.id)
        pic_list = []
        if len(pic_obj_list) > 0:
            for i in pic_obj_list:
                img_url = "http:52.80.194.137:8001/dxgm/picture/{0}".format(i.image),
                pic_list.append(img_url)
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_activity_objects, request=request, view=self)
        # 实例化对象
        ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            # 活动话题
            topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
            # datetime 转 str
            # 活动时间日期
            i["activity_time"] = i["activity_time"].replace('T', ' ').split('.')[0]
            activity_time = i["activity_time"].split(' ')[0]
            # # 日期str 转 datetime
            birthday = datetime.datetime.strptime(i["activity_time"], '%Y-%m-%d %H:%M:%S')
            # 格式化datetime为%Y-%m-%d %H:%M:%S （datetime==> str）
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # str ==> datetime
            now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
            # 距开始还有多少秒
            # print(birthday-now_time)
            a = time.mktime(birthday.timetuple())
            b = time.mktime(now_time.timetuple())
            seconds = int(a) - int(b)
            # seconds = (birthday-now_time).seconds
            # 如果差距大于一小时
            if seconds > 0:
                # 差值大于一天86400
                if seconds > 86400:
                    day = seconds//86400
                    if day > 30:
                        month = seconds//2592000
                        stime = "{0]个月".format(month)
                    elif day > 15:
                        stime = "半个月"
                    else:
                        stime = "{0]天".format(day)
                else:
                    # 一天之内
                    seconds = seconds%86400
                    if seconds > 3600:
                        hour = seconds//3600
                        stime = "{0}小时".format(hour)
                    else:
                        # 一小时之内
                        minute = seconds%3600
                        if minute > 60:
                            minute = minute//60
                            stime = "{0}分钟".format(minute)
                        else:
                            stime = "即将开始"
            else:
                seconds = int(b) - int(a)
                # 差值大于一天86400
                if seconds > 86400:
                    day = seconds//86400
                    if day > 30:
                        month = seconds//2592000
                        stime = "{0]个月前".format(month)
                    elif day > 15:
                        stime = "半个月前"
                    else:
                        stime = "{0]天前".format(day)
                else:
                    # 一天之内
                    seconds = seconds%86400
                    if seconds > 3600:
                        hour = seconds//3600
                        stime = "{0}小时前".format(hour)
                    else:
                        # 一小时之内
                        minute = seconds%3600
                        if minute > 60:
                            minute = minute//60
                            stime = "{0}分钟前".format(minute)
                        else:
                            stime = "已开始"
            # 获取车库中的车
            carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
            # 获取车对象
            carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()
            # 活动名称
            like_obj = Like.objects.filter(id=i["activity_name"]).first()
            dic = {
                # 人头像
                "head_img": "http:52.80.194.137:8001/dxgm/image/{0}".format(obj.img_head),
                # 姓名
                "nikename": obj.username,
                # 职业
                "job": obj.job,
                # 性别
                "sex": obj.sex,
                # 图片数量
                "pic_num": pic_num,
                # 图片地址
                "pic_list": pic_list,
                # 开始距当前活动还剩多少时间
                "start_time": stime,
                # 车型
                "car_model_name": carmodel_obj.name,
                # 活动名称
                "activity_name": like_obj.likename,
                # 活动主键
                "id": i["id"],
                # 活动类型种类(单人/多人)
                "activity_kind": i["activity_kind"],
                # 活动出发地
                "activity_area_start": i["activity_area_start"],
                # 活动目的地
                "activity_area_end": i["activity_area_end"],
                # 活动时间
                "activity_time": activity_time,
                # 活动话题
                "topic_name": topic_obj.topic_name,
                # 活动参与人群性别
                "activity_person_sex": i["activity_person_sex"],
                # 活动内容-说说你的想法
                "activity_content": i["activity_content"],
            }
            lis.append(dic)
        lis[0]["number"] = all_activity_objects.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 活动首页列表(排除自己和未开始的活动)
class ActivityIndex(APIView):
    def post(self, request):
        pid = request.data.get("pid")
        # 获取现在的时间
        now = datetime.datetime.now()
        # 获取该用户相关活动
        all_activity_objects = Activity.objects.exclude(activity_issue_id=pid)
        lis = []
        if all_activity_objects:
            # all_activity_objects = Activity.objects.all()
            # 实例化分页对象, 获取数据库中的分页数据
            pagination_class = MyPageNumberPagination()
            page_list = pagination_class.paginate_queryset(queryset=all_activity_objects, request=request, view=self)
            # 实例化对象
            ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个

            for i in ser.data:
                # 获取用户对象
                obj = User.objects.filter(id=i["activity_issue"]).first()
                # 图片列表
                pic_obj_list = Image.objects.filter(user_id=obj.id)
                pic_list = []
                if len(pic_obj_list) > 0:
                    for i in pic_obj_list:
                        img_url = "http:52.80.194.137:8001/dxgm/picture/{0}".format(i.image),
                        pic_list.append(img_url)
                # 图片数量
                pic_num = Image.objects.filter(user_id=obj.id).count()
                # 活动话题
                topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
                # datetime 转 str
                # 活动时间日期
                i["activity_time"] = i["activity_time"].replace('T', ' ').split('.')[0]
                activity_time = i["activity_time"].split(' ')[0]
                # # 日期str 转 datetime
                birthday = datetime.datetime.strptime(i["activity_time"], '%Y-%m-%d %H:%M:%S')
                # 格式化datetime为%Y-%m-%d %H:%M:%S （datetime==> str）
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # str ==> datetime
                now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
                # 距开始还有多少秒
                # print(birthday-now_time)
                a = time.mktime(birthday.timetuple())
                b = time.mktime(now_time.timetuple())
                seconds = int(a) - int(b)
                # 如果差距大于一小时
                if seconds > 0:
                    # 差值大于一天86400
                    if seconds > 86400:
                        day = seconds//86400
                        if day > 30:
                            month = seconds//2592000
                            stime = "{0]个月".format(month)
                        elif day > 15:
                            stime = "半个月"
                        else:
                            stime = "{0]天".format(day)
                    else:
                        # 一天之内
                        seconds = seconds%86400
                        if seconds > 3600:
                            hour = seconds//3600
                            stime = "{0}小时".format(hour)
                        else:
                            # 一小时之内
                            minute = seconds%3600
                            if minute > 60:
                                minute = minute//60
                                stime = "{0}分钟".format(minute)
                            else:
                                stime = "即将开始"
                else:
                    seconds = int(b) - int(a)
                    # 差值大于一天86400
                    if seconds > 86400:
                        day = seconds//86400
                        if day > 30:
                            month = seconds//2592000
                            stime = "{0]个月前".format(month)
                        elif day > 15:
                            stime = "半个月前"
                        else:
                            stime = "{0}天前".format(day)
                    else:
                        # 一天之内
                        seconds = seconds%86400
                        if seconds > 3600:
                            hour = seconds//3600
                            stime = "{0}小时前".format(hour)
                        else:
                            # 一小时之内
                            minute = seconds%3600
                            if minute > 60:
                                minute = minute//60
                                stime = "{0}分钟前".format(minute)
                            else:
                                stime = "已开始"
                # 获取车库中的车
                carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
                # 获取车对象
                carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()
                # 活动名称
                like_obj = Like.objects.filter(id=i["activity_name"]).first()
                dic = {
                    # 人头像
                    "head_img": "http:52.80.194.137:8001/dxgm/image/{0}".format(obj.img_head),
                    # 姓名
                    "nikename": obj.username,
                    # 职业
                    "job": obj.job,
                    # 性别
                    "sex": obj.sex,
                    # 图片数量
                    "pic_num": pic_num,
                    # 图片地址
                    "pic_list": pic_list,
                    # 开始距当前活动还剩多少时间
                    "start_time": stime,
                    # 车型
                    "car_model_name": carmodel_obj.name,
                    # 活动名称
                    "activity_name": like_obj.likename,
                    # 活动主键
                    "id": i["id"],
                    # 活动类型种类(单人/多人)
                    "activity_kind": i["activity_kind"],
                    # 活动出发地
                    "activity_area_start": i["activity_area_start"],
                    # 活动目的地
                    "activity_area_end": i["activity_area_end"],
                    # 活动时间
                    "activity_time": activity_time,
                    # 活动话题
                    "topic_name": topic_obj.topic_name,
                    # 活动参与人群性别
                    "activity_person_sex": i["activity_person_sex"],
                    # 活动内容-说说你的想法
                    "activity_content": i["activity_content"],
                }
                lis.append(dic)
            lis[0]["number"] = all_activity_objects.count()
        return Response(Common.tureReturn(Common, data=lis))