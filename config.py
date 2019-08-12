# coding:utf-8
import psycopg2
from psycopg2 import extras
from flask_restful import Resource
# 对每一个接口进程请求生成一个数据库游标，并在操作结束以后释放游标
def cur_p(fun):
    def connect(*args,**kw):
        conn = psycopg2.connect(database="HKMetro", user="keqi", password="123456", host="pgm-uf68mcuk63uqsf8s14830.pg.rds.aliyuncs.com", port="3433")
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        res = fun(*args, **kw, conn=conn, cur=cur)
        conn.commit()
        cur.close()
        conn.close()
        return res
    return connect