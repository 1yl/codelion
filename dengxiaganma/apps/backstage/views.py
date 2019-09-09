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
from ..utils.pictools import PictureParsing, ImageParsing, LicenceParsing, LicenseParsing, ModelPasing
from ..user.models import *
from django.contrib.auth.hashers import make_password, check_password
import time, datetime, os
from rest_framework.pagination import PageNumberPagination
from ..backstage.serializer import BrandSerializer, SeriseSerializer, ModelSerializer
from django.core import serializers
# basedir = os.path.abspath(os.path.dirname(__file__))


# Create your views here.
# TODO：初始化
class InitView(APIView):
    def get(self, request):
        return Response("111")

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


# TODO: 我的车库
class BsMycars(APIView):
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


# TODO: 获取所有车型
class BsGetAllCarBrand(APIView):
    def post(self, request):
        all_brand_objects = CarBrand.objects.all()
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_brand_objects, request=request, view=self)
        # 实例化对象
        ser = BrandSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            dic = {
                "brand_id": i["id"],
                "name": i["name"],
                "initial": i["initial"],
                "image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(i["image_filename"]),
            }
            lis.append(dic)
        lis[0]["number"] = all_brand_objects.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 根据某一车型获取该车型系列
class BsGetAllCarSeriseByBrand(APIView):
    def post(self, request):
        car_brand_id = request.data.get("car_brand_id")
        car_series_list = CarSeries.objects.filter(brand_id=car_brand_id)
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=car_series_list, request=request, view=self)
        # 实例化对象
        ser = SeriseSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            carbrand_obj = CarBrand.objects.filter(id=i["brand"]).first()
            data = {
                "series_id": i["id"],
                "brand_id": carbrand_obj.id,
                "series_name": i["name"],
                "brand_name": carbrand_obj.name,
                "initial": carbrand_obj.initial,
                "image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(carbrand_obj.image_filename),
            }
            lis.append(data)
        lis[0]["number"] = car_series_list.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 根据某一车系和车品牌获取该车型
class BsGetAllCarModelBySeries(APIView):
    def post(self, request):
        car_series_id = request.data.get("car_series_id")
        car_brand_id = request.data.get("car_brand_id")
        car_model_list = CarModel.objects.filter(brand_id=car_brand_id, series_id=car_series_id)
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=car_model_list, request=request, view=self)
        # 实例化对象
        ser = ModelSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            carbrand_obj = CarBrand.objects.filter(id=i["brand"]).first()
            carseries_obj = CarSeries.objects.filter(id=i["series"]).first()
            data = {
                "model_id": i["id"],
                "series_id": carseries_obj.id,
                "brand_id": carbrand_obj.id,
                "series_name": carseries_obj.name,
                "brand_name": carbrand_obj.name,
                "initial": carbrand_obj.initial,
                "image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(carbrand_obj.image_filename),
                "model_name": i["name"],
                "price": i["price"]
            }
            lis.append(data)
        lis[0]["number"] = car_model_list.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: Admin登录
class BsAdminLogin(APIView):
    def post(self, request):
        uname = request.data.get("username")
        upwd = request.data.get("password")
        if uname == "admin" and upwd == "admin":
            return Response(Common.tureReturn(Common, data=True))
        else:
            return Response(Common.falseReturn(Common, data=False))


# TODO: 添加车品牌
class BsAddBrand(APIView):
    def post(self, request):
        model_name = request.data.get("model_name")
        brand_obj = CarBrand.objects.filter(name=model_name).first()
        if not brand_obj:
            model_initial = request.data.get("model_initial")
            # 车标
            car_logo = request.data.get("car_logo")
            for i in car_logo:
                if i["base64"] != '' and i["type"]:
                    img = ModelPasing(i["base64"], i["type"])
                else:
                    img = ""
                CarBrand.objects.create(name=model_name, initial=model_initial, image_filename=img)
            return Response(Common.tureReturn(Common, data="添加成功"))
        else:
            return Response(Common.falseReturn(Common, data="添加失败,该品牌已存在"))


# TODO: 修改车品牌
class BsDelBrand(APIView):
    def post(self, request):
        model_id = request.data.get("model_id")
        new_model_name = request.data.get("new_model_name")
        brand_obj = CarBrand.objects.filter(id=model_id).first()
        if not brand_obj:
            brand_obj = CarBrand.objects.filter(name=model_name).first()
            model_initial = request.data.get("model_initial")
            # 车标
            car_logo = request.data.get("car_logo")
            for i in car_logo:
                if i["base64"] != '' and i["type"]:
                    img = ModelPasing(i["base64"], i["type"])
                else:
                    img = ""
            brand_obj.name = new_model_name
            brand_obj.initial = model_initial
            brand_obj.image_filename = img
            brand_obj.save()
            return Response(Common.tureReturn(Common, data="修改成功"))
        else:
            return Response(Common.falseReturn(Common, data="修改失败,该品牌已存在"))




