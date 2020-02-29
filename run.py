# coding:utf-8
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort, marshal
from psql import FlaskAPI
import base64, time, os, re
import pytesseract
from PIL import Image
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

errors = {
    'UserAlreadyExistsError': {
        'message': "A user with that username already exists.",
        'status': 409,
    },
    'ResourceDoesNotExist': {
        'message': "A resource with that ID no longer exists.",
        'status': 410,
        'extra': "Any extra information you want.",
    },
}

api = Api(app)


class Common:
    def returnTrueJson(self, data, msg="请求成功"):
        return jsonify({
            "status": 1,
            "data": data,
            "msg": msg
        })
    def returnFalseJson(self, data=None, msg="请求失败"):
        return jsonify({
            "status": 0,
            "data": data,
            "msg": msg
        })


class DealWithPic(Resource):
    def post(self):
        # 获取图片文件
        img = request.files.get("picture")

        # 获取当前时间戳
        timestamp = str(int(time.time()))
        # 更改图片名称
        sa = img.filename.split('.')[0]
        img.filename = img.filename.replace(sa, timestamp)
        # 获取图片类型
        a = img.filename.split('.')[1]
        print(a)
        # 定义存放路径
        path = basedir + "/static/img/"
        print(path)
        # 图片path和名称组成的路径
        file_path = path+img.filename
        print(file_path)
        # 保存图片
        img.save(file_path)
        im = Image.open(file_path)
        # print(aa)

        # 二值化
        threshold = 140
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        # 转化到灰度图
        imgry = im.convert('L')
        # 保存图像
        imgry.save(file_path)
        # 二值化
        out = imgry.point(table, '1')
        out.save(file_path)

        # 识别
        text = pytesseract.image_to_string(out)
        print(text)
        try:
            b = text[int(text.index("Info")):int(text.index("Mobile"))]
            phone = b.split()[1] + b.split()[2] + b.split()[3]
            c = text[int(text.index("Mobile")):int(text.index("Username"))]
            name = c.split()[1].split('@')[1]
        except:
            name = ''
            FlaskAPI.insert_data(data1=phone, data2=name, data3=file_path)
        else:
            FlaskAPI.insert_data(data1=phone, data2=name, data3=file_path)

        return Common.returnTrueJson(Common, data={"phonenumber": phone, "username": name})


api.add_resource(DealWithPic, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
