# coding:utf-8
import psycopg2
from decorate import cur_p
import time, os, re, datetime, json


class FlaskAPI():

    # TODO: 关闭数据库
    @staticmethod
    def close_database(conn, cur):
        conn.commit()
        cur.close()
        conn.close()

    # TODO: 将字典类型数据转换成key, value元组类型数据
    @staticmethod
    def deal_data(data):
        if type(data) == dict and len(data) > 0:
            # key = [i for i in data.keys()]
            # key = '(' + ','.join(key) + ')'
            key = '(' + ','.join([i for i in data.keys()]) + ')'
            value = str([data[i] for i in data]).replace(']', ')').replace('[', '(')
            return key, value
        else:
            return 'error'

    # TODO: 数据插入
    @staticmethod
    @cur_p
    def insert_data(data, table, cur='',  conn=''):
        res = FlaskAPI.deal_data(data)
        if res == 'error':
            return res
        else:
            try:
                cur.execute("insert into {0} {1} values{2};".format(table, res[0], res[1]))
                return 'success'
            except psycopg2.Error as e:
                print('reason', e)
                return 'error'

    # TODO: 数据查询--用户是否存在
    @staticmethod
    @cur_p
    def query_data(data, table, cur='', conn=''):
        sql = "select id from {0} where name = '{1}';".format(table, data)
        try:
            cur.execute(sql)
            result = cur.fetchall()
            # print("数据查询", result)
            return result
        except psycopg2.Error as e:
            # print('reason', e)
            return 'error'

    # TODO: 数据查询--用户存在密码是否与之匹配
    @staticmethod
    @cur_p
    def oauth_data(data1, data2, table, cur='', conn=''):
        sql = "select id from {0} where name = '{1}' and password = '{2}';".format(table, data1, data2)
        try:
            cur.execute(sql)
            result = cur.fetchall()
            # print("用户名密码验证是否匹配", result)
            return result
        except psycopg2.Error as e:
            # print('reason', e)
            return 'error'