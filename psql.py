# coding:utf-8
import psycopg2
import time, os, re, datetime, json
# from functools import reduce
from config import cur_p


class FlaskAPI():
    @staticmethod
    @cur_p
    def insert_data(data1, data2, data3, cur='', conn=''):
        try:
            sql = "insert into phone (phone_number, user_name, url) values ('{0}', '{1}', 'http://47.103.34.10:5001/{2}');"
            cur.execute(sql.format(data1, data2, data3))
            data = cur.fetchall()
            return data
        except:
            return 'error'
