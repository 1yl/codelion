from flask import Flask, jsonify, request
# from model import db, User
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort, marshal
import json
from psql_common import FlaskAPI
app = Flask(__name__)
app.config.from_object('config')

# db.init_app(app)

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

api = Api(app, catch_all_404s=True, errors=errors)

parser = reqparse.RequestParser()
parser.add_argument('user_name', required=True)
parser.add_argument('user_password', required=True)
# parser.add_argument('user_nickname')
# parser.add_argument('user_email', required=True)

resource_full_fields = {
    'user_id': fields.Integer,
    'user_name': fields.String,
    # 'user_email': fields.String,
    # 'user_nickname': fields.String
}

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

class Hello(Resource):
    def get(self):
        return 'Hello Flask!'

class User(Resource):
    # 用户注册
    def post(self):
        data = request.json
        if data and type(data) == dict:
            # 数据库匹配
            res = FlaskAPI.query_data(data["name"], 'web_user')
            if len(res) == 0:
                print("111")
                res = FlaskAPI.insert_data(data, 'web_user')
                if res == 'success':
                    return Common.returnTrueJson(Common, data={"name": data["name"]})
                else:
                    return Common.returnFalseJson(Common, data="添加用户失败")
            else:
                return Common.returnFalseJson(Common, data="用户已存在")
        else:
            return Common.returnFalseJson(Common, data="数据不正确")
        
class UserLogin(Resource):
    # 用户登陆
    def post(self):
        data = request.json
        # 数据是否符合要求
        if data and type(data) == dict:
            # 数据库匹配-查询用户是否存在
            res = FlaskAPI.query_data(data["name"], 'web_user')
            if len(res) != 0:
                # 用户存在
                res1 = FlaskAPI.oauth_data(data['name'], data['password'], 'web_user')
                if len(res1) != 0:
                    # 用户密码验证成功
                    return Common.returnTrueJson(Common, data='验证通过')
                else:
                    return Common.returnFalseJson(Common, data='密码验证错误')
            else:
                # 用户不存在
                return Common.returnFalseJson(Common, data='用户不存在')
        else:
            # 数据不符合要求
            return Common.returnFalseJson(Common, data='数据不正确')


api.add_resource(Hello, '/', '/hello')
api.add_resource(User, '/user')
api.add_resource(UserLogin, '/userlogin')


if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])