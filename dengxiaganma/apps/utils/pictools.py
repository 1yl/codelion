# coding:utf-8


import base64
import time
# from dengxiaganma.dengxiaganma.settings import WEB_HOST_NAME, WEB_IMAGE_SERVER_PATH
from dengxiaganma.settings import WEB_HOST_NAME, WEB_IMAGE_SERVER_PATH, WEB_PICTURE_SERVER_PATH

# from apps.land.models import *
"""
头像上传处理
"""
def ImageParsing(imgbase, suffix):
    print(111)
    img = imgbase.split(',')
    imgdata = base64.b64decode(img[1])
    timestamp = str(int(time.time()))
    # file_url = WEB_HOST_NAME + WEB_IMAGE_SERVER_PATH + '%s.%s' % (timestamp, suffix)
    file_url = WEB_IMAGE_SERVER_PATH + '%s.%s' % (timestamp, suffix)
    print(file_url)
    file = open(file_url, 'wb')
    file.write(imgdata)
    file.close()
    return timestamp + '.' + suffix


"""
照片上传处理
"""
def PictureParsing(imgbase, suffix):
    img = imgbase.split(',')
    imgdata = base64.b64decode(img[1])
    timestamp = str(int(time.time()))
    # file_url = WEB_HOST_NAME + WEB_IMAGE_SERVER_PATH + '%s.%s' % (timestamp, suffix)
    file_url = WEB_PICTURE_SERVER_PATH + '%s.%s' % (timestamp, suffix)
    file = open(file_url, 'wb')
    file.write(imgdata)
    file.close()
    return timestamp + '.' + suffix


"""
行驶证上传处理
"""
def LicenceParsing(imgbase, suffix):
    img = imgbase.split(',')
    imgdata = base64.b64decode(img[1])
    timestamp = str(int(time.time()))
    # file_url = WEB_HOST_NAME + WEB_IMAGE_SERVER_PATH + '%s.%s' % (timestamp, suffix)
    file_url = WEB_LICENCE_SERVER_PATH + '%s.%s' % (timestamp, suffix)
    file = open(file_url, 'wb')
    file.write(imgdata)
    file.close()
    return timestamp + '.' + suffix


"""
驾驶证上传处理
"""
def LicenseParsing(imgbase, suffix):
    img = imgbase.split(',')
    imgdata = base64.b64decode(img[1])
    timestamp = str(int(time.time()))
    # file_url = WEB_HOST_NAME + WEB_IMAGE_SERVER_PATH + '%s.%s' % (timestamp, suffix)
    file_url = WEB_LICENSE_SERVER_PATH + '%s.%s' % (timestamp, suffix)
    file = open(file_url, 'wb')
    file.write(imgdata)
    file.close()
    return timestamp + '.' + suffix