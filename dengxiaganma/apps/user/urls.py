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
    # TODO: 更换头像
    path('user_changeheadimg/', ChangeHeadImg.as_view()),
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
    # TODO: 黑名单
    path('user_addblacklist/', AddBlackList.as_view()),
    # TODO: 我的关注
    path('user_myfocus/', MyFocus.as_view()),
    # TODO: 我的粉丝
    path('user_myfans/', MyFans.as_view()),
    # TODO: 我的黑名单
    path('user_myblacklist/', MyBlackList.as_view()),
    # TODO: 我的车库
    path('user_mycars/', Mycars.as_view()),
    # TODO: 行驶证上传
    path('user_uploadlicence/', UploadLicence.as_view()),
    # TODO: 驾驶证上传
    path('user_uploadlicense/', UploadLicense.as_view()),
]