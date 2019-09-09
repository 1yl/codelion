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
    # TODO: 发布邀约
    path('user_issueinvitation/', IssueInvitation.as_view()),
    # TODO: 发布活动点击单人或者多人跳转活动发布页面时话题的读取
    path('user_topic/', TopicExist.as_view()),
    # TODO: 唱歌泡吧活动发布
    path('user_singsingbar/', SingingBar.as_view()),
    # TODO: 互动聊天活动发布
    path('user_chatinteraction/', ChatInteraction.as_view()),
    # TODO: 美食咖啡活动发布
    path('user_gourmetcoffee/', GourmetCoffee.as_view()),
    # TODO: 运动户外活动发布
    path('user_sportsoutdoors/', SportsOutdoors.as_view()),
    # TODO: 电影展览活动发布
    path('user_filmfair/', FilmFair.as_view()),
    # TODO: 忘了密码-用户密码修改
    path('user_updatepwd/', UpdatePwdView.as_view()),
    # TODO: 获取所有车型
    path('user_getallcarbrand/', GetAllCarBrand.as_view()),
    # TODO: 根据某一品牌获取该车型系列
    path('user_getallcarseries/', GetAllCarSeriseByBrand.as_view()),
    # TODO: 根据某系列车获取该系列所有车型
    path('user_getallcarmodel/', GetAllCarModelBySeries.as_view()),
    # TODO: 他的主页
    path('user_hishomepage/', HisHomePage.as_view()),
    # TODO: 邀请他参与我的话题-获取话题列表
    path('user_invitetopic/', InviteTopic.as_view()),
    # TODO: 判断信息是否已全部完善
    path('user_judgestate/', JudgeState.as_view()),
    # TODO: 点击发布扣除点数
    path('user_reducecoin/', ReduceCoin.as_view()),
    # TODO: 个人活动列表
    path('user_activitypaging/', ActivityPaging.as_view()),
    # TODO: 活动首页列表
    path('user_activityindex/', ActivityIndex.as_view()),
]