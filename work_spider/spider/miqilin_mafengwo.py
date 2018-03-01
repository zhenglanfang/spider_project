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

raw_item = {
    'vendor_name':'',
    'description':'',
    'price_class':None,
    'cuisine':'',
    'characters':'', #特点
    'category':'', #类型
    'price':'',
    'address':'',
    'vendor_url':'',
    'vendor_city':'香港',
    'business_hours':'', #营业时间
    'score_details':'',  #评级
    'comment':'' #推荐理由
}

mafengwo_url = 'https://m.mafengwo.cn/cy/10189/gonglve.html?page=%s&is_ajax=1'

mafengwo_host = 'https://m.mafengwo.cn'

user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) \
CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'

def parse():
    for page in range(22,3850):
        print('%s页---开始'%page)
        headers = {
            'user-agent':user_agent,
            'x-requested-with':'XMLHttpRequest',
        }
        response = request.get(mafengwo_url%page,headers=headers)
        if response:
            try:
                html = json.loads(response.content)
            except Exception as e:
                print(e)
                html = {}
            html = etree.HTML(html.get('html',''))
            shop_list = html.xpath("//section[@class='poi-list']/div")
            for shop in shop_list:
                shop_item = raw_item.copy()
                name = shop.xpath("./a[@class='poi-li']/div[@class='hd']/text()")[0]
                score_details = shop.xpath(".//div[@class='star']/span/@style")[0]
                shop_url = shop.xpath("./a[@class='poi-li']/@href")[0]
                cuisine = shop.xpath(".//p[@class='m-t']/strong/text()")
                comment = shop.xpath(".//div[@class='comment']/text()")
                if exist(name):
                    print(name + '已经存在')
                    continue
                shop_item['vendor_name'] = name
                shop_item['score_details'] = score_details.replace('width:','').replace('%;','')
                shop_item['cuisine'] = cuisine[0].replace('&nbsp;','') if cuisine else ''
                shop_item['comment'] = comment[0] if comment else ''
                shop_detail(shop_url,shop_item)
            print('第%s页完成'%page)
        else:
            print ('请求失败%s'%shop_url)



def shop_detail(url,item):
    url = mafengwo_host + url
    item['vendor_url'] = url
    headers = {
        'user-agent': user_agent,
    }
    response = request.get(url,headers=headers)
    if response:
        html = etree.HTML(response.content)
        description = html.xpath("//div[@class='tips']/p[@style='max-height: 3.9em;overflow: hidden;']/text()")
        sub_info = html.xpath("//div[@class='tips']/p[@style='max-height: 2.5em;overflow: hidden;']")
        get_sub_info(sub_info,item)
        address = html.xpath("//div[@class='maps']/ul[@class='context']/li")
        get_sub_info(address,item)
        item['description'] = handle_desctrip(description)
    else:
        print('请求失败%s'%url)
    save_date(item)


def handle_desctrip(nodes):
    nodes = [node.strip().strip('·') for node in nodes]
    return ''.join(nodes)


def get_sub_info(node,item):
    key_dict = {
        u'门  票':'price',
        u'开放时间':'business_hours',
        u'地址':'address'
    }
    for i in node:
        key = i.xpath("./strong/text()")[0]
        value = i.xpath("./text()")
        key = key_dict.get(key,'')
        if key:
            item[key] = handle_node(value)
    return item


def get_price_class(price):
    flag = 3
    if price < 100:
        flag = 0
    elif price < 300:
        flag = 1
    elif price < 800:
        flag = 2
    return flag



# 计数器
def generate_counter(func):
    '''
        计数器
    '''
    cont = [0]

    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            cont[0] = cont[0] + 1
            print '第%s条数据插入成功！--%s'%(cont[0],args[0]['vendor_name'])
        return result
    return inner


@generate_counter
def save_date(item):
    sql = 'insert into vendor_miqilin_mafengwo(vendor_name,description,price_class,cuisine,characters,category,price,address,vendor_city,'+\
            'vendor_url,business_hours,score_details,comment)' +\
            ' values(:vendor_name,:description,:price_class,' +\
            ':cuisine,:characters,:category,:price,:address,:vendor_city,' +\
            ':vendor_url,:business_hours,:score_details,:comment)'
    return dbmysql.edit(sql,item)


def exist(name):
    sql = 'select vendor_name from vendor_miqilin_mafengwo where vendor_name=:vendor_name'
    return dbmysql.first(sql,{'vendor_name':name})


# 处理xpath获取的数据,返回str
def handle_node(node_list):
    if node_list:
        nodes = [node.strip() for node in node_list if node.strip()]
        return ';'.join(nodes)
    else:
        return ''


# 处理xpath获取的数据,返回list
def handle_node_arr(node_list):
    if node_list:
        nodes = [node.strip() for node in node_list if node.strip()]
        return nodes
    else:
        return []


def get_node_list(node):
    if not node:
        node = []
    return ';'.join(node)


def get_book_status(node):
    flag = 1
    if node:
        flag = 0 #预定
    return flag


def handle_book(node):
    for item in node:
        if not item.find('订座') == -1:
            return True
    return False


def handle_no_book(node):
    for item in node:
        if not item.find('订座') == -1:
            return True

    return False


def get_price_class(price):
    flag = 3
    if price < 100:
        flag = 0
    elif price < 300:
        flag = 1
    elif price < 800:
        flag = 2
    return flag


def handle_price(node):
    price = node.replace('$','').replace('以下','').replace('以上','')
    price_list = [int(item) for item in price.split('-')]
    price = sum(price_list)/len(price_list)
    return price


def handle_emjoy(str):
    highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return highpoints.sub(u'', str)

def check(name,address,check_name,check_address):
    name = name.lower()
    name = switch_lang.Traditional2Simplified(name)
    address = address.lower()
    address = switch_lang.Traditional2Simplified(address)
    check_name = check_name.lower()
    check_name = switch_lang.Traditional2Simplified(check_name)
    check_address = check_address.lower()
    check_address = switch_lang.Traditional2Simplified(check_address)
    if len(name) > len(check_name):
        name,check_name = check_name,name
    if len(address) > len(check_address):
        address,check_address = check_address,address
    if check_name.find(name) == -1:
        return False
    if check_address.find(address) == -1:
        return False
    else:
        return True

def update_data():
    pass

def update_shop():
    raw_shops_sql = "select vendor_id,vendor_name,description,address,recomm_dish from vendor_miqilin where description = ''"
    check_shops_sql = "select vendor_name,description,address,recomm_dish from vendor_miqilin_quna where description != ''"
    raw_shops = dbmysql.fetchall(raw_shops_sql)
    check_shops = dbmysql.fetchall(check_shops_sql)
    for shop in raw_shops:
        shop_name = shop['vendor_name']
        shop_address = shop['address']
        for check_shop in  check_shops:
            flag = check(shop_name,shop_address,check_shop['vendor_name'],check_shop['address'])
            if flag:
                update_sql = 'update vendor_miqilin set description=:description where vendor_id=:vendor_id'
                update_data = {
                    'description':check_shop['description'],
                    'vendor_id':shop['vendor_id']
                }
                dbmysql.edit(update_sql,update_data)

if __name__ == '__main__':
    parse()




