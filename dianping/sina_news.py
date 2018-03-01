#! /usr/bin/python
# coding=utf-8
import requests

from database import dbmysql

url = 'http://blog.sina.com.cn/' # 博客
url2 = 'http://feed.mix.sina.com.cn/api/roll/get?pageid=143&lid=1528&num=30&page=1&encode=utf-8' # ajax请求
params = {
    'pageid':143,
    'lid':1528,
    'encode':'utf-8',
    'num':30,
    'page':1,
}
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
}

'''
    时间戳转换为格式化时间
    time_local = time.localtime(1509076987)
    time.strftime("%Y-%m-%d %H:%M:%S",time_local)
'''
with requests.Session() as s:
    s.get(url,headers=headers)
    response = s.get(url2,params=params)
    infos = response.json()


