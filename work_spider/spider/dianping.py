# -*- coding: utf-8 -*-
import datetime
import re
import requests
import time
import random
import json
from lxml import etree
from database import dbmysql
from util import request
from util import handle

# 菜单的URL shopId:  cityId=342(澳门) 341(香港)

dianping_shop_url = 'https://www.dianping.com/search/keyword/%s/0_%s'
start_url = 'https://www.dianping.com'
num = 220
headers = {
    'Host': 'www.dianping.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.dianping.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

def start_parse(city):
    response = request.get(start_url,headers=headers)
    if response:
        names = get_names(city.get('name'))
        cookies = response.cookies
        for name in names:
            url = dianping_shop_url%(city.get('code'),name)
            item = {}
            item['name'] = name
            item['links'] = url
            item['book_status'] = ''
            item['facilities'] = ''
            item['description'] = ''
            item['pyment'] = ''
            item['low_price'] = ''
            item['detail_price'] = ''
            item['price'] = ''
            item['michelin_star'] = ''
            item['cuisine'] = ''
            item['service_time'] = ''
            item['address'] = ''
            item['phone'] = ''
            item['district'] = ''
            item['landmark'] = ''
            item['quality'] = ''
            item['brand'] = ''
            item['recomm_dishes'] = ''
            item['taste'] = ''
            item['characters'] = ''
            item['category'] = ''
            item['people_group'] = ''
            item['lat'] = ''
            item['lng'] = ''
            item['country'] = ''
            item['city'] = city.get('name')
            item['other_name'] = ''
            item['dish'] = ''
            get_shop(url,item,cookies,city)

def get_shop(url,item,cookies,city):
    response = request.get(url, headers=headers,cookies=cookies)
    if response:
        html = etree.HTML(response.text)
        names = html.xpath("//div[@class='tit']/a/@title")
        name = names[0] if names else ''
        if name == item['name']:
            shop_url = html.xpath("//div[@class='tit']/a/@href")
            if shop_url:
                shop_url = shop_url[0]
                shop_id = shop_url.split('/')[-1]
                item['url'] = shop_url
                # headers['Referer'] = shop_url
                # shopinfo_url = 'http://www.dianping.com/ajax/json/shopDynamic/basicHideInfo?shopId=%s'%shop_id
                get_shopinfo(shop_url,item,response.cookies,city,shop_id)
                return
    save(item)

def get_shopinfo(url,item,cookies,city,shop_id):
    response = request.get(url,headers=headers,cookies=cookies)
    # 菜单的URL shopId:  cityId=342(澳门) 341(香港) cityEnName：macau hongkong  categoryURLName=food&power=5&shopType=10
    dish_url = 'http://www.dianping.com/overseas/shop/ajax/allReview?categoryURLName=food&power=5&shopType=10\
&shopId=%s&cityId=%s&cityEnName=%s' % (shop_id, city.get('code'), city.get('name'))
    item = get_dish(dish_url, item, headers, cookies)
    if response and response.text:
        html = etree.HTML(response.text)
        address = html.xpath("//div[@class='expand-info address']/span[@class='item']/text()")
        item['address'] = address[0].strip() if address else ''
        phone = html.xpath("//p[@class='expand-info tel']/span[@class='item']/text()")
        item['phone'] = phone[0] if phone else ''
        intents = html.xpath("//p[@class='info info-indent']")
        for intent in intents:
            info_name = intent.xpath("span[@class='info-name']/text()")
            info = intent.xpath(".//span[@class='item']/text()")
            info_name = info_name[0] if info_name else ''
            info = info[0] if info else ''
            if info_name == '别       名：':
                item['other_name'] = info.strip()
            elif info_name == '营业时间：':
                item['service_time'] = info.strip()
            elif info_name == '餐厅简介：':
                item['description'] = info.strip()

        banner = html.xpath("//div[@class='breadcrumb']/a/text()")
        item['district'] = banner[1].strip() if len(banner)>1 else ''
        item['cuisine'] = banner[2].strip() if len(banner)>2 else ''
        price = html.xpath("//span[@id='avgPriceTitle']/text()")
        item['price'] = price[0].split('：')[1][:-1] if price else ''
        headers['Referer'] = url
        save(item)
    else:
        save(item)

def get_dish(url, item, headers, cookies):
    '''
    :param response:
    :return: 获取菜单
    '''
    response = request.get(url,headers=headers,cookies=cookies)
    body = json.loads(response.text)
    dish = body.get('dishTagStrList',[])
    if dish == None:
        dish = []
    dish = ';'.join(dish)
    item['dish'] = dish
    return item


# def get_shop_detail(url,item,cookies,city,shop_id):
#     response = request.get(url,headers=headers,cookies=cookies)
#     if response:
#         body = response.json()
#         info = body.get('msg')
#         shopinfo = info.get('shopInfo') if info else ''
#         alias = shopinfo.get('altName') if shopinfo else ''
#         item['alias'] = alias
#
#     # 菜单的URL shopId:  cityId=342(澳门) 341(香港) cityEnName：macau hongkong  categoryURLName=food&power=5&shopType=10
#     dish_url = 'http://www.dianping.com/overseas/shop/ajax/allReview?categoryURLName=food&power=5&shopType=10\
# &shopId=%s&cityId=%s&cityEnName=%s' % (shop_id,city.get('code'),city.get('name'))
#     get_comment(dish_url,item,headers,cookies)

# def get_comment(url,item,headers,cookies):
#     response = request.get(url,headers=headers,cookies=cookies)
#     if response:
#         body = response.json()
#         summarys = body.get('summarys', [])
#         if summarys == None:
#             summarys = []
#         summarys = ['%s(%s)' % (summary['summaryString'], summary['summaryCount']) for summary in summarys]
#         summarys = ';'.join(summarys)
#         item['summarys'] = summarys
#     save(item)


def get_avg_price(self,response):
    body = json.loads(response.text)
    avg_price = body.get('avgPrice','')
    # print(avg_price)
    item = response.meta.get('item')
    shop_id = response.meta.get('shop_id')
    item['price'] = avg_price

    # 菜单的URL shopId:  cityId=342(澳门) 341(香港) cityEnName：macau hongkong  categoryURLName=food&power=5&shopType=10
    dish_url = 'http://www.dianping.com/overseas/shop/ajax/allReview?categoryURLName=food&power=5&shopType=10\
    &shopId=%s&cityId=342&cityEnName=hongkong'%(shop_id)
    # print(dish_url)
    # yield scrapy.Request(url=dish_url, callback=self.get_dish, meta={'item':item},dont_filter=True)

def get_book(self,node):
    book_status = 1
    if node:
        icon = node[-1].xpath("./div[@class='public-icon icon']/@data-icon")[0].root
        if icon == 'Ž':
            book_status = 2
            node.pop()
        elif icon == '‘':
            book_status = 0
            node.pop()
    return book_status

def get_payment(self,node):
    s = '现金;信用卡;借记卡;支付宝;微信'
    if node:
        icon = node[0].xpath("./div[@class='public-icon icon']/@data-icon")[0].root
        if icon == ':':
            s = '现金;借记卡;支付宝;微信'
            node.pop(0)
        elif icon == '`':
            s = '现金'
            node.pop(0)
    return s

def get_facilities(self,node):
    facis_list = []
    for item in node:
        faci = item.xpath(".//div[@class='restaurant-intro']/text()")[0].root
        facis_list.append(faci)
    return ';'.join(facis_list)

def get_michelin_star(self,node):
    flog = -1
    if node:
        icon = node[0].root
        icon_dict = {'J':-2,'=':0,'m':1,'n':2,'o':3}
        flog = icon_dict[icon]
    return flog

@classmethod
def get_lxs(cls):
    cls.num += 1
    yield cls.num

def get_names(city):
    '''
    获取开始urls
    :param city:
    :return:
    '''
    with open('../data/%s_lack' % city, 'r') as f:
        for line in f.readlines():
            name = line.strip()
            yield name

# 获取返回的json
def get_json(url):
    params = ''
    response = request.get(url,params=params)
    if response:
        return response.json()
    else:
        return None

def save(item):
    sql = 'insert into michelin(name,links,book_status,facilities,description,pyment,low_price,detail_price,michelin_star,cuisine,service_time,address,phone,district,landmark,quality,brand,recomm_dishes,taste,characters,category,people_group,lat,lng,country,city,price,other_name,dish) values(:name,:links,:book_status,:facilities,:description,:pyment,:low_price,:detail_price,:michelin_star,:cuisine,:service_time,:address,:phone,:district,:landmark,:quality,:brand,:recomm_dishes,:taste,:characters,:category,:people_group,:lat,:lng,:country,:city,:price,:other_name,:dish)'
    dbmysql.edit(sql, item)
    print('%s插入成功'%item['name'])

def get_dish(city,shop_id):
    dish_url = 'http://www.dianping.com/overseas/shop/ajax/allReview?categoryURLName=food&power=5&shopType=10\
    &shopId=%s&cityId=%s&cityEnName=%s' % (shop_id, city.get('code'), city.get('name'))
    response = request.get(dish_url)
    body = json.loads(response.text)
    dish = body.get('dishTagStrList', [])
    if dish == None:
        dish = []
    dish = ';'.join(dish)
    print(dish)

if __name__ == '__main__':
    # print(get_names('macau').next())
    macau = {
        'name':'macau',
        'code':'342',
    }
    hongkong = {
        'name':'hongkong',
        'code':'341',
    }
    # start_parse(macau)
    # start_parse(hongkong)
    get_dish(macau,3556015)










