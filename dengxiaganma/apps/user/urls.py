# coding:utf-8
from django.urls import path
from ..user.views import *


app_name = 'apps.user'

urlpatterns = [
    # TODO: 初始化
    path('', InitView.as_view()),
    # TODO: 发送验证码
    path('send_sms/', SendSMSView.as_view()),
    # TODO: 用户注册
    path('user_regist/', RegistView.as_view()),
    # TODO: 密码登录
    path('user_loginpwd/', LoginPwdView.as_view()),
    # TODO: 手机登陆
    path('user_loginphone/', LoginPhoneView.as_view()),
    # TODO: 个人信息编辑
    path('user_editinfo/', EditInfo.as_view()),
    # TODO: 首次登陆完善信息
    path('user_editinfofirst/', EditInfoFirst.as_view()),
    # TODO: 发布照片至照片墙
    path('user_publishpic/', PublishPic.as_view()),
    # TODO: 获取编辑信息
    path('user_geteditinfo/', GetEditInfo.as_view()),
    # TODO: 个人页(含关注、粉丝、黑名单)
    path('user_personalpage/', PersonalPage.as_view()),
    # TODO: 添加关注
    path('user_addfocus/', AddFocus.as_view()),
]