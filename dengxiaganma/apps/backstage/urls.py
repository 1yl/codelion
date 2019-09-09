# coding:utf-8
from django.urls import path
from ..backstage.views import *


app_name = 'apps.user'

urlpatterns = [
    # TODO: 初始化
    path('', InitView.as_view()),
    # TODO: 车品牌
    path('bsbrand/', BsGetAllCarBrand.as_view()),
    # TODO: 车系列
    path('bsseries/', BsGetAllCarSeriseByBrand.as_view()),
    # TODO: 车型
    path('bsmodel/', BsGetAllCarModelBySeries.as_view()),
    # TODO: Admin登陆
    path('bslogin/', BsAdminLogin.as_view()),
    # TODO: 添加车品牌
    path('bsbrandadd/', BsAddBrand.as_view()),
    # TODO: 修改车品牌
    path('bsbranddel/', BsDelBrand.as_view()),
]