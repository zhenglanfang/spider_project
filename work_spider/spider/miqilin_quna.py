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

item = {
    'vendor_name':'',
    'description':'',
    'price_class':'',
    'michelin_star':'', #无
    'quality':'', #无
    'dish':'',
    'recomm_dish':'',
    'cuisine':'',
    'characters':'', #特点
    'category':'', #类型
    'people_group':'', #无
    'price':'',
    'address':'',
    'vendor_url':'',
    'price_range':'',
    'vendor_city':'香港',
    'business_hours':'', #营业时间
    'score_details':'',  #评级
    'phone':'',
    'appraise':'' #评价
}

quna_url = 'http://travel.qunar.com/p-cs300027-xianggang-meishi?page=%s'

quna_host = 'http://travel.qunar.com'

def parse():
    for page in range(1000,3300):
        print('%s页---开始'%page)
        response = request.get(quna_url%page)
        if response:
            html = etree.HTML(response.content)
            shop_list = html.xpath("//ul[@class='list_item clrfix']/li[@class='item']")
            for shop in shop_list:
                shop_item = item.copy()
                name = shop.xpath(".//span[@class='cn_tit']/text()")[0]
                score_details = shop.xpath("//span[@class='cur_score']/text()")[0]
                if exist(name):
                    print(name + '已经存在')
                    continue
                sub_info = shop.xpath(".//div[@class='sublistbox']/dl[@class='sublist_item clrfix']")
                get_sub_info(sub_info,shop_item)
                shop_url = shop.xpath("./a[@data-beacon='poi']/@href")[0]
                shop_item['vendor_name'] = name
                shop_item['score_details'] = score_details
                shop_item['vendor_url'] = shop_url
                shop_detail(shop_url,shop_item)
            print('第%s页完成'%page)
        else:
            print ('请求失败%s'%shop_url)



def shop_detail(url,item):
    response = request.get(url)
    if response:
        html = etree.HTML(response.content)
        description = handle_node(html.xpath("//div[@class='e_db_content_box']/p/text()"))
        business_hours = handle_node(html.xpath("//dl[@class='m_desc_right_col']/dd/span/p/text()"))
        phone = handle_node(html.xpath("//td[@class='td_l']/dl[2]/dd/span/text()"))
        item['description'] = description
        item['business_hours'] = business_hours
        item['phone'] = phone
    else:
        print('请求失败%s'%url)
    save_date(item)


def get_sub_info(node,item):
    key_dict = {
        u'人　均':'price',
        u'类　型':'category',
        u'地　址':'address',
        u'推荐菜':'recomm_dish',
    }
    for i in node:
        key = i.xpath("./dt[@class='sub_tit']/text()")[0]
        value = i.xpath("./dd[contains(@class, 'sub_des')]/text()")[0]
        value = value.replace('¥ ','').replace('/',';').replace('\t',';')
        if key_dict[key] == 'price':
            value = int(value)
        item[key_dict[key]] = value
    if not item['price']:
        item['price'] = 0
    item['price_class'] = get_price_class(item['price'])
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
    sql = 'insert into vendor_miqilin_quna(vendor_name,description,price_class,michelin_star,quality,'+\
            'dish,recomm_dish,cuisine,characters,category,people_group,price,address,vendor_city,'+\
            'vendor_url,business_hours,score_details,phone,appraise)' +\
            ' values(:vendor_name,:description,:price_class,:michelin_star,:quality,' +\
            ':dish,:recomm_dish,:cuisine,:characters,:category,:people_group,:price,:address,:vendor_city,' +\
            ':vendor_url,:business_hours,:score_details,:phone,:appraise)'
    return dbmysql.edit(sql,item)


def exist(name):
    sql = 'select vendor_name from vendor_miqilin_quna where vendor_name=:vendor_name'
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


def get_business_hours(shop_id):
    url = 'https://www.openrice.com/api/poi/status?uiCity=hongkong&uiLang=zh-cn&poiId=%s'%shop_id
    response = request.get(url)
    if response:
        opening_info = {}
        business_hours = json.loads(response.content)
        opening_info['business_hours'] = business_hours
        open_tiem = set()
        if business_hours:
            for item in business_hours.get('openingHourInfo',{}).get("normalHours",[]):
                for i in item.get('times',{}):
                    time_list = i['timeDisplayString'].split('-')
                    if len(time_list)>1:
                        start, end = time_list
                        if end == '00:00':
                            end = '24:00'
                        open_tiem.update([start,end])
                        time_digit = [float(i.replace(':','.')) for i in open_tiem]
                        opening_info['open_time'] = str(min(time_digit)).replace('.',':')
                        opening_info['close_time'] = str(max(time_digit)).replace('.',':')
        return opening_info


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


if __name__ == '__main__':
    parse()




