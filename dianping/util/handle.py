#! /usr/bin/python
# coding=utf-8

import uuid
import time
import re
from datetime import datetime
from datetime import date

def get_uuid():
    '''
    涉及到并发的情况下，不要使用id自增的方式对数据库表设置自增字段，
    uuid局域网内的计算机由操作系统产生的一串字符，不会重复
    只要涉及到并发，我们可以采用UUID作为主键
    数据表当中还要配合一个时间字段（insertTime）使用，这样无论是反应日志或是部门之间的对接，
    都能有很有效的证据
    '''
    return str(uuid.uuid4())

def get_datetime(timestamp):
    '''
    作用：时间戳转换为格式化的时间
    :param timestamp: 时间戳,type:str
    :return: '2017-10-27 19:59:12' 格式的时间
    '''
    time_local = time.localtime(float(timestamp))
    return time.strftime("%Y-%m-%d %H:%M:%S",time_local)

def get_timestamp(strtime):
    '''
    作用：字符串转换为时间戳
    :param str_date:
    :return:时间戳
    '''
    localtime1 = time.strptime(strtime, '%Y-%m-%d %H:%M:%S')
    return time.mktime(localtime1)

# 日期的比较 时间戳
# def compare_timestamp(timestamp):
#     time1 = timestamp
#     time2 = date.today()
#     delta = time2 - time1
#     if delta==0:
#         return True
#     else:
#         return False

# 判断一个字符串日期是否是当天日期
def compare_datetime(strtime):
    '''
       判断一个字符串日期是否是当天日期
       strtime: '%Y-%m-%d %H:%M:%S' or '%Y-%m-%d'
    '''
    return True
    strtime = strtime.split()[0]
    time1 = datetime.strptime(strtime, '%Y-%m-%d')
    time1 = date(time1.year,time1.month,time1.day)
    now = date.today()
    if time1 == now:
        return True
    else:
        return False

def getNoHtmlBody(content):
    '''
    去除html标签的方法，如果我们不想要获取到的数据中有html标签，可调用此方法进行处理
    '''
    body = None
    try:
        # dr = re.compile(r'<[^>]+>', re.S)
        dr = re.compile(r'</?\w+[^>]*>', re.S)
        body = dr.sub('', content)
    except Exception, ex:
        print (ex.message)
    return body

def test():
    # print get_datetime('1509171516')
    # print get_datetime('1509173115')
    # print get_datetime('1509173142')
    #print get_datetime('1509368593')
    # print time.mktime(time.strptime('2017-10-28 0:0:0', '%Y-%m-%d %H:%M:%S'))
    # print compare_datetime('2017-10-29 19:12:1')
    print compare_datetime('2018-1-2 23:12:1')
    print compare_datetime('2018-1-1')
    

if __name__ == '__main__':
    test()