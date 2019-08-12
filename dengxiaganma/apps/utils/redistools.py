# coding:utf-8
"""
redis的使用
"""


from django_redis import get_redis_connection
import random

# 短信验证码的有效期
SMS_CODE_REDIS_EXPIRES = 120

# 短信发送频次
SEND_SMS_CODE_INTERVAL = 60

class RedisTools(object):

    def __init__(self):
        # 创建redis连接对象（'verify_codes'表示settings文件中redis配置的选择）
        self.redis_conn = get_redis_connection("verify_codes")

    def linkredis(self, phone):
        print(type(phone))
        sms_code = "%06d" % random.randint(0, 999999)
        # 使用管道
        # print(redis_conn)
        pl = self.redis_conn.pipeline()
        # 存储短信验证码至redis数据库
        pl.setex("sms_%s" % phone, SMS_CODE_REDIS_EXPIRES, sms_code)
        # 记录用户发送短信的频次
        pl.setex('send_flag_%s' % phone, SEND_SMS_CODE_INTERVAL, 1)
        # 指令传递，将数据写入redis
        pl.execute()
        return sms_code
