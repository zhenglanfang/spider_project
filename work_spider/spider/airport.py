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


start_url = 'http://airport.supfree.net/index.asp?page=%d'

def parse():
    for page in range(1,285):
        page_url = start_url%page
        time.sleep(random.randint(1,3))
        response = request.get(page_url)
        get_airport(response)

def get_airport(response):
    html = etree.HTML(response.content)
    datas = html.xpath("//table[@class='ctable']//tr")
    datas.pop(0)
    for item in datas:
        city = item.xpath(".//span[@class='bblue']/text()")[0]
        three_code = item.xpath("td[2]/text()")
        three_code = three_code[0] if three_code else ''
        four_code = item.xpath("td[3]/text()")
        four_code = four_code[0] if four_code else ''
        airport = item.xpath("td[4]/text()")
        airport = airport[0] if airport else ''
        english_name = item.xpath("td[5]/text()")
        english_name = english_name[0] if english_name else ''
        item = dict(
            city=city,
            three_code=three_code,
            four_code=four_code,
            airport_name=airport,
            english_name=english_name
        )
        sql = 'insert into airport(city,three_code,four_code,airport_name,english_name) values(:city,:three_code,:four_code,:airport_name,:english_name)'
        dbmysql.edit(sql,item)

if __name__ == '__main__':
    parse()


