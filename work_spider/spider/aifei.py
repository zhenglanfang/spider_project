#! /usr/bin/python
# coding=utf-8

import datetime
import re
import requests
import time
import random
from lxml import etree
from database import dbmysql
from util import request
from util import handle


start_url = 'http://www.aifei.com/airport/listall'

def parse():
    response = request.get(start_url)
    if response:
        html = etree.HTML(response.content)
        urls = html.xpath("//div[@class='link-n clearfix']/a/@href")
        for url in urls:
            response = request.get(url)
            get_airport(response)

def get_airport(response):
    if response:
        url = response.url
        html = etree.HTML(response.content)
        bont = html.xpath("//div[@class='jc-int-bont']/p//text()")
        city = bont[0] if bont else ''
        code = bont[1] if len(bont)>1 else ''
        zh_name = html.xpath("//div[@class='xt01']/h1/b/text()")
        en_name = html.xpath("//div[@class='mod-c01']/div/text()")
        zh_name = zh_name[0] if zh_name else ''
        en_name = en_name[0] if en_name else ''
        item = dict(
            city=city,
            code=code,
            url = url,
            zh_name = zh_name,
            en_name =en_name,
        )
        sql = 'insert into aifei(city,code,url,zh_name,en_name) values(:city,:code,:url,:zh_name,:en_name)'
        dbmysql.edit(sql,item)

if __name__ == '__main__':
    parse()


