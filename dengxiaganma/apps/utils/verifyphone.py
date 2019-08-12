# coding:utf-8
"""
手机验证码验证
"""
from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient

class VerifyPhone(object):
    def __init__(self, phone, sms_code):
        self.phone = phone
        self.sms_code = sms_code
        self.apikey = "31df217fdc515fdd2d53f48171917245"

    def send_sms(self):
        # 初始化client,apikey作为所有请求的默认值
        clnt = YunpianClient(self.apikey)
        # 自己定义的短信内容，但要和后台模板相匹配才行
        # param = {YC.MOBILE: self.mobile, YC.TEXT: self.text}
        # r = clnt.sms().single_send(param)
        param = {YC.MOBILE: self.phone, YC.TPL_ID: '2789228', YC.TPL_VALUE: '#code#=%s' % self.sms_code}
        r = clnt.sms().tpl_single_send(param)
        print(r.code(), r.data(), r.msg())
        return r.msg()
        # 获取返回结果, 返回码:r.code(),返回码描述:r.msg(),API结果:r.data(),其他说明:r.detail(),调用异常:r.exception()
        # 短信:clnt.sms() 账户:clnt.user() 签名:clnt.sign() 模版:clnt.tpl() 语音:clnt.voice() 流量:clnt.flow()