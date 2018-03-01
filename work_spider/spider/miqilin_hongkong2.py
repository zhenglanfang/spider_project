#! /usr/bin/python
# coding=utf-8

import re
import json
import time
import datetime
import requests
import random
from lxml import etree
from database import dbmysql
from util import request
from util import handle
from util.langconv import switch_lang

ctrip_host = 'http://you.ctrip.com'
ctrip_search_shop_url = 'http://you.ctrip.com/restaurantlist/HongKong38/list-p1.html?keywords=%s&ordertype=0'


def parse(item):
    url = ctrip_search_shop_url % item['vendor_name']
    response = request.get(url)
    if response:
        html = etree.HTML(response.content)
        box = html.xpath("//div[@class='rdetailbox']")
        if box:
            box = box[0]
            name = box.xpath("./dl/dt/a/text()")[0].decode('utf-8').lower()
            name = switch_lang.Traditional2Simplified(name)
            address = box.xpath("./dl/dd[@class='ellipsis']/text()")[0].decode('utf-8').lower()
            address = switch_lang.Traditional2Simplified(address)
            check_name = item['vendor_name'].lower()
            check_name = switch_lang.Traditional2Simplified(check_name)
            check_address = item['address'].lower()
            check_address = switch_lang.Traditional2Simplified(check_address)
            item['ctrip_address'] = address
            if name.find(check_name) == -1:
                return
            if address.find(check_address) == -1:
                flag = False
            else:
                flag = True
            shop_url = box.xpath("./dl/dt/a/@href")[0]
            get_shop_detail(shop_url, item, flag)
    else:
        print('请求失败：%s'%url)

def get_shop_detail(url, item, flag):
    url = ctrip_host + url
    response = request.get(url)
    if response:
        html = etree.HTML(response.content)
        description = get_one(html.xpath("//div[@itemprop='description']/text()"))
        dish = get_shop_dish(html.xpath("//div[@class='text_style']/p/text()"))
        price = get_one(html.xpath("//em[@class='price']/text()")).replace('¥','')
        if flag:
            item['description'] = description
        else:
            item['ctrip_description'] = description
        item['ctrip_dish'] = switch_lang.Traditional2Simplified(dish)
        item['ctrip_url'] = url
        item['ctrip_price'] = price
        save_data(item)
    else:
        print('shop 请求失败%s'%url)

def save_data(item):
    sql = 'update vendor_miqilin set description=:description,ctrip_dish=:ctrip_dish,'+\
          'ctrip_price=:ctrip_price,ctrip_url=:ctrip_url,ctrip_address=:ctrip_address,ctrip_description=:ctrip_description'+\
          ' where vendor_id=:vendor_id'
    data = {
        'description':item['description'],
        'ctrip_dish':item['ctrip_dish'],
        'ctrip_price':item['ctrip_price'],
        'ctrip_url':item['ctrip_url'],
        'ctrip_address':item['ctrip_address'],
        'ctrip_description':item['ctrip_description'],
        'vendor_id':item['vendor_id']
    }
    dbmysql.edit(sql,data)

def get_one(node):
    if node:
        return node[0].strip()
    else:
        return ''

def get_shop_dish(node):
    if node:
        node = node[0].replace('\r\n', '').replace(' ', '')
        return node.replace(',', ';').strip()
    else:
        return ''

def main():
    sql = "select * from vendor_miqilin where description = '' and ctrip_description is null"
    results = dbmysql.fetchall(sql)
    for item in results:
        item = dict(item)
        parse(item)

if __name__ == '__main__':
    main()



