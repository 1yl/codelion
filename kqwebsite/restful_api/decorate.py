# coding:utf-8
import psycopg2
from psycopg2 import extras
from flask_restful import Resource
# 对每一个接口进程请求生成一个数据库游标，并在操作结束以后释放游标
def cur_p(fun):
    def connect(*args, **kwargs):
        conn = psycopg2.connect(database="admin", user="flectra", password="admin", host="0.0.0.0", port="5432")
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        res = fun(conn=conn, cur=cur, *args, **kwargs)
        conn.commit()
        cur.close()
        conn.close()
        return res
    return connect
