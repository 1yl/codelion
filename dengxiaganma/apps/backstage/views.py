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
from rest_framework.pagination import PageNumberPagination
from ..backstage.serializer import BrandSerializer, SeriseSerializer, ModelSerializer
from django.core import serializers

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



# TODO: 车品牌展示
class ShowCarBrand(APIView):
    def get(self, request):
        all_brand_objects = CarBrand.objects.all()
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_brand_objects, request=request, view=self)
        # 实例化对象
        ser = BrandSerializer(instance=page_list, many=True) # 可允许多个
        lis = []
        for i in ser.data:
            dic = {
                "name": i["name"],
                "initial": i["initial"],
                "image_filename": i["image_filename"]
            }
            lis.append(dic)
        lis[0]["number"] = all_brand_objects.count()
        return Response(Common.tureReturn(Common, data=lis))



# TODO: 车系列展示
class ShowCarSeries(APIView):
    def get(self, request):
        all_series_objects = CarSeries.objects.all()
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_series_objects, request=request, view=self)
        # 实例化对象
        ser = SeriseSerializer(instance=page_list, many=True) # 可允许多个
        lis = []
        for i in ser.data:
            print(i)
            all_samebrand_objs = CarBrand.objects.filter(id=i["brand"])
            for j in all_samebrand_objs:

                dic = {
                    "name": i["name"],
                    "brand_name": j.name,
                    "initial": j.initial,
                    "image_filename": j.image_filename
                }
            lis.append(dic)
        lis[0]["number"] = all_series_objects.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 车型展示
class ShowCarModel(APIView):
    def get(self, request):
        all_model_objects = CarModel.objects.all()
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_model_objects, request=request, view=self)
        # 实例化对象
        ser = ModelSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            all_samebrand_objs = CarBrand.objects.filter(id=i["brand"])
            for j in all_samebrand_objs:
                dic = {
                    "price": i["price"],
                    "name": i["name"],
                    "brand_name": j.name,
                    "initial": j.initial,
                    "image_filename": j.image_filename
                }
            all_sameseries_objs = CarSeries.objects.filter(id=i["series"])
            for x in all_sameseries_objs:
                dic['serise_name'] = x.name
            lis.append(dic)
        lis[0]["number"] = all_model_objects.count()
        return Response(Common.tureReturn(Common, data=lis))