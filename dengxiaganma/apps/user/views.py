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
from ..utils.pictools import PictureParsing, ImageParsing, LicenceParsing, LicenseParsing
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
        if img_head != '' and suffix != '':
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
            if i["base64"] != '' and i["type"]:
                img = PictureParsing(i["base64"], i["type"])
            else:
                img = ''
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            Image.objects.create(user_id=user_obj.id, image=img, create_time=create_time)
        return Response("ok")


# TODO: 点击更换头像
class ChangeHeadImg(APIView):
    def put(self, request):
        # 获取用户手机号
        phone = request.data.get("phone")
        # 获取用户头像
        headimg = request.data.get("headimg")
        # 用户头像后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(phone=phone).first()
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
        phone = request.data.get("phone")
        # 获取用户对象
        obj = User.objects.get(phone=phone)
        nike = request.data.get("nike")
        sex = request.data.get("sex")
        birthday = request.data.get("birthday")
        job = request.data.get("job")
        area = request.data.get("area")
        like = request.data.get("like")
        headimg = request.data.get('headimg')
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
            print(birth.month)
            res = signtools.person_sign(birth.month, birth.day)
            obj.sign = res
        # 头像处理
        if headimg["base64"] != '' and headimg["type"] != '':
            img = PictureParsing(headimg["base64"], headimg["type"])
        else:
            img = ''
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
        focus_num = UserRelation.objects.filter(user_id_id=user_obj.id).count()
        # focus_num = 1
        # 粉丝人数
        fans_num = UserRelation.objects.filter(follower_id_id=user_obj.id).count()
        # fans_num = 1
        # 黑名单人数
        blacklist_num = BlackList.objects.filter(third_person_id=user_obj.id).count()
        # blacklist_num = 1
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
        # 关注表删除记录
        UserRelation.objects.filter(user_id_id=user_obj.id, follower_id_id=id).delete()
        return Response(Common.tureReturn(Common, data='取消关注'))


# TODO: 黑名单
class AddBlackList(APIView):
    # 添加黑名单
    def post(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
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
        phone = request.data.get("phone")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 黑名单表删除记录
        BlackList.objects.filter(first_person_id=user_obj.id, third_person_id=id).delete()
        return Response(Common.tureReturn(Common, data='移除黑名单'))


# TODO: 我的关注
class MyFocus(APIView):
    def get(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
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
                "job": myfocus_obj.job,
                "focus_state": "已关注"
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 我的粉丝
class MyFans(APIView):
    def get(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
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
                "focus_state": focus_state
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 我的黑名单
class MyBlackList(APIView):
    def get(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
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
        phone = request.data.get("phone")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 获取用户车库
        carbarn_list = CarBarn.objects.filter(car_person_id=user_obj.id)
        lis = []
        for i in carbarn_list:
            dic = {
                "car_id": i.id,
                "car_brand": i.car_brand,
                "car_type": i.car_type,
                "car_color": i.car_color
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))

    # 车辆信息
    def post(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 车辆id
        car_id = request.data.get("car_id")
        # 获取用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 车辆信息
        car_obj = CarBarn.objects.filter(id=car_id).first()
        dic = {
            "car_brand": car_obj.car_brand,
            "car_type": car_obj.car_type,
            "car_color": car_obj.car_color,
            "car_value": car_obj.car_value,
            "driver_licence": user_obj.driver_licence,
            "driver_license": user_obj.driver_license
        }
        return Common(Common.tureReturn(Common, data=dic))

    # 添加车辆（修改）
    def put(self, request):
        # 用户手机号
        phone = request.data.get("phone")
        # 获取该用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 获取车辆品牌
        car_brand = request.data.get("car_brand")
        # 获取车辆型号
        car_type = request.data.get("car_type")
        # 获取车辆颜色
        car_color = request.data.get("car_color")
        # 获取车辆价值
        car_value = request.data.get("car_value")
        # 保存车辆信息
        CarBarn.objects.create(car_brand=car_brand,car_type=car_type,car_color=car_color,car_value=car_value,car_person_id=user_obj.id)
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
        car_id = request.data.get("car_id")
        # 车辆信息
        car_obj = CarBarn.objects.filter(id=car_id).first()
        car_obj.delete()
        return Response(Common.tureReturn(Common, data='删除车辆成功'))


# TODO: 行驶证上传
class UploadLicence(APIView):
    def put(self, request):
        # 获取用户手机号
        phone = request.data.get("phone")
        # 获取用户行驶证
        licence = request.data.get("licence")
        # 用户行驶证后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(phone=phone).first()
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
        phone = request.data.get("phone")
        # 获取用户驾驶证
        license = request.data.get("license")
        # 用户驾驶证后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(phone=phone).first()
        # 驾驶证处理
        if license != '' and suffix != '':
            img = LicenseParsing(license, suffix)
            user_obj.driver_license = img
            user_obj.save()
            return Response(Common.tureReturn(Common, data='驾驶证上传成功'))
        else:
            return Response(Common.falseReturn(Common, data='驾驶证未上传'))