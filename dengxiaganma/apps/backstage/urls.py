# coding:utf-8
from django.urls import path
from ..backstage.views import *


app_name = 'apps.user'

urlpatterns = [
    # TODO: 初始化
    path('', InitView.as_view()),
    # TODO: 车品牌
    path('brand/', ShowCarBrand.as_view()),
    # TODO: 车系列
    path('series/', ShowCarSeries.as_view()),
    # TODO: 车型
    path('model/', ShowCarModel.as_view()),
]