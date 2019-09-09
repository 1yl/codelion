from dengxiaganma.settings import WEB_HOST_NAME, WEB_IMAGE_SERVER_PATH, WEB_PICTURE_SERVER_PATH, WEB_LICENCE_SERVER_PATH, WEB_LICENSE_SERVER_PATH, WEB_ACTIVITY_SERVER_PATH
from ..user.models import *
from ..utils.pictools import PictureParsing, ImageParsing, LicenceParsing, LicenseParsing, Parsing
import time, datetime
"""
活动发布
"""


def postActivity(request):
    # 获取发布人手机号
    pid = request.data.get("pid")
    # 获取该用户对象
    user_obj = User.objects.filter(id=pid).first()
    # 发布点数
    issue_coin = request.data.get("issue_coin")
    # 获取活动类型
    activity_type = request.data.get("activity_type")
    # 获取活动类型种类(单人/多人)
    activity_kind = request.data.get("activity_kind")
    # 获取该用户话题
    activity_topic = request.data.get("activity_topic")
    # 获取该用户活动时间
    activity_time = request.data.get("activity_time")
    # # 判断活动时间得出活动状态
    # at = datetime.datetime.strptime(activity_time, '%Y-%m-%d %H:%M:%S')
    # # 获取现在时间
    # nt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 获取活动出发地
    activity_area_start = request.data.get("activity_area_start")
    # 获取活动目的地
    activity_area_end = request.data.get("activity_area_end")
    # 获取参与人群性别
    activity_person_sex = request.data.get("activity_person_sex")
    # 获取参与人群车辆
    activity_person_num = request.data.get("activity_person_num")
    # 携带人数
    activity_person_take = request.data.get("activity_person_take")
    # 参与点数
    activity_coin_take = request.data.get("activity_coin_take")
    # 获取出行方式
    activity_car = request.data.get("activity_car")
    # 获取你的想法
    activity_content = request.data.get("activity_content")
    # 获取添加图片
    activity_img = request.data.get("activity_img")
    # 存图片# 照片 [{"base64": "xxx", "type": "jpg"}, ...]
    img = Parsing(activity_img[0]["base64"], activity_img[0]["type"], WEB_ACTIVITY_SERVER_PATH)
    # str 转 datetime
    activity_time = datetime.datetime.strptime(activity_time, '%Y-%m-%d %H:%M:%S')
    # 获取出行车辆,先根据车型获取car_model_id, 在获取carbarn的id
    carmodel_obj = CarModel.objects.filter(name=activity_car).first()
    carbarn_obj = CarBarn.objects.filter(car_model_id=carmodel_obj.id, car_person_id=user_obj.id).first()
    # 获取活动类型
    like_obj = Like.objects.filter(likename=activity_type).first()
    # 话题发布时间
    add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 话题添加
    Topic.objects.create(topic_name=activity_topic, topic_user_id=user_obj.id, topic_time=add_time)
    topic_obj = Topic.objects.filter(topic_name=activity_topic).first()
    # 添加活动
    Activity.objects.create(topic_name_id=topic_obj.id, activity_name_id=like_obj.id, activity_issue_id=user_obj.id, activity_time=activity_time, activity_kind=activity_kind,
                            activity_area_start=activity_area_start, activity_area_end=activity_area_end,
                            activity_person_sex=activity_person_sex, activity_status='未开始',
                            activity_person_num=activity_person_num, activity_car_id=carbarn_obj.id,
                            activity_content=activity_content, activity_img=img, activity_coin_take=activity_coin_take, activity_person_take=activity_person_take)
    # 人员点数扣除
    user_obj.coin = int(user_obj.coin) - int(issue_coin)
    user_obj.save()

def putActivity(request):
    # 获取发布人手机号
    phone = request.data.get("phone")
    # 获取活动编号
    activity_id = request.data.get("activity_id")
    # 获取话题编号
    # XXXXXXXXXXXXXXXXX
    # 获取该用户对象
    user_obj = User.objects.filter(phone=phone).first()
    # 获取活动类型
    activity_type = request.data.get("activity_type")
    # 获取活动类型种类(单人/多人)
    activity_kind = request.data.get("activity_kind")
    # 获取该用户话题
    activity_topic = request.data.get("activity_topic")
    # 获取该用户活动时间
    activity_time = request.data.get("activity_time")
    # 获取活动出发地
    activity_area_start = request.data.get("activity_area_start")
    # 获取活动目的地
    activity_area_end = request.data.get("activity_area_end")
    # 获取参与人群性别
    activity_person_sex = request.data.get("activity_person_sex")
    # 获取参与人群人数
    activity_person_num = request.data.get("activity_person_num")
    # 获取出行方式
    activity_car = request.data.get("activity_car")
    # 获取你的想法
    activity_content = request.data.get("activity_content")
    # 获取添加图片
    activity_img = request.data.get("activity_img")
    # 存图片# 照片 [{"base64": "xxx", "type": "jpg"}, ...]
    img = Parsing(activity_img[0]["base64"], activity_img[0]["type"], WEB_ACTIVITY_SERVER_PATH)
    # str 转 datetime
    activity_time = datetime.datetime.strptime(activity_time, '%Y-%m-%d %H:%M:%S')
    # 获取出行车辆,先根据车型获取car_model_id, 在获取carbarn的id
    carmodel_obj = CarModel.objects.filter(name=activity_car).first()
    carbarn_obj = CarBarn.objects.filter(car_model_id=carmodel_obj.id, car_person_id=user_obj.id).first()
    # 获取活动类型
    like_obj = Like.objects.filter(likename=activity_type).first()
    # 添加活动
    Activity.objects.filter(id=activity_id).update(activity_name_id=like_obj.id, activity_issue_id=user_obj.id,
                                                   activity_time=activity_time, activity_kind=activity_kind,
                                                   activity_area_start=activity_area_start, activity_area_end=activity_area_end,
                                                   activity_person_sex=activity_person_sex, activity_person_num=activity_person_num,
                                                   activity_car_id=carbarn_obj.id, activity_content=activity_content,
                                                   activity_img=img)
    # 话题发布时间
    add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 话题添加
    Topic.objects.create(topic_name=activity_topic, topic_user_id=user_obj.id, topic_time=add_time)