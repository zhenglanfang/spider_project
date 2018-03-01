#! /usr/bin/python
# coding=utf-8

import sys
sys.path.append('/Users/mrs/Desktop/project/spider_project/work_spider')

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

start_url = 'https://www.viamichelin.com/web/Restaurants/Restaurants-New_York-_-New_York-United_States'

city_list_url = 'http://www.dianping.com/ajax/citylist/getAllDomesticCity'

def parse():
    for i in range(1,24):
        url = start_url + '?page=%d'%i
        response = request.get(url)
        if response:
            html = etree.HTML(response.content)
            shops = html.xpath("//li[@class='poi-item poi-item-restaurant']")
            for shop in shops:
                name = shop.xpath("div[@class='poi-item-name truncate']/a/text()")[0]
                row_price = shop.xpath(".//div[@class='poi-item-price']//text()")
                row_price = [i for i in row_price if i.strip()]
                price =  int(row_price[1][1:]) + int(row_price[-1][1:])
                price = int(round(price/2 * 6.3279))
                row_price = ' '.join(row_price)
                item = dict(
                    name = name,
                    price = price,
                    row_price = row_price
                )
                sql = 'insert into price(name,price,row_price) values(:name,:price,:row_price)'
                dbmysql.edit(sql,item)

def handle_privce():
    sql = "select id,detail_price from price_detail"
    results = dbmysql.fetchall(sql)
    for item in results:
        id = item[0]
        # print(type(item[1]))
        # detail_price = item[1].decode('utf-8')
        detail_price = item[1].replace("'", '"')
        detail_price = json.loads(item[1].replace("'", '"'),encoding='utf-8')
        price_list = []
        for i in detail_price.values():
            if i['单点'.decode('utf-8')]:
                price_list.append(i['单点'.decode('utf-8')].replace('￥',''))
            if i['套餐'.decode('utf-8')]:
                price_list.append(i['套餐'.decode('utf-8')].replace('￥',''))
        max = 0
        max_index = 0
        for i in price_list:
            i = i.lower()
            i = re.sub(r'\(weekend.*?\)', '', i)
            if i.find('-') > -1:
                if int(i.split('-')[1]) > max:
                    max_index = i
                    max = int(i.split('-')[1])
            else:
                if int(i) > max:
                    max_index = i
                    max = int(i)

        if max_index.find('-')>-1:
            price = int(max_index.split('-')[0]) + int(max_index.split('-')[1])
            price = int(price/2)
        else:
            price = int(max_index)
        sql = 'update price_detail set price=:price where id=:id'
        dbmysql.edit(sql,{'price':price,'id':id})

def get_avg_price(response):
    try:
        body = json.loads(response.text)
        avg_price = body.get('avgPrice', '')
        return avg_price
    except Exception as e:
        print(e)
        return False
        # print(response.text)
        # print(response.url)


def get_dianping_city():
    response = request.get(city_list_url)
    if response:
        citys = json.loads(response.content)
        with open('data/dianping_city.json','w') as f:
            f.write(json.dumps(citys,ensure_ascii=False,indent=2))
        city_dict = {}
        for i in citys.get('cityMap').values():
            for city in i:
                city_dict[city.get('cityName')] = city.get('cityId')
        return city_dict

def update_price():

    # sql1 = "select vendor_id,name,price from vendor_miqilin where vendor_city='香港'"
    # result_raws = dbmysql.fetchall(sql1)
    # print(len(result_raws))
    # return
    # for item in result_raws:
    #     sql2 = "select price from price where name=:name"
    #     price = dbmysql.first(sql2,params={'name':item[1]})
    #     if price:
    #         pass
    #         # sql3 = "update vendor_miqilin set price = :price where vendor_id=:vendor_id"
    #         # dbmysql.edit(sql3,params={'price':price[0],'vendor_id':item[0]})
    #     else:
    #         print(item[1])


    # sql = "select name,price from price"
    # names = dbmysql.fetchall(sql)
    # for item in names:
    #     sql2 = "select name,price from vendor_miqilin where vendor_city='纽约' and name=:name"
    #     flag = dbmysql.first(sql2,params={'name':item[0]})
    #     if not flag:
    #         print (str(item[0])+':'+str(item[1]))
    

    # 香港
    sql1 = "select vendor_id,name,vendor_url,vendor_city from vendor_miqilin_price"
    results = dbmysql.fetchall(sql1)
    print(len(results))
    city_list = get_dianping_city()
    city_list[u'纽约'] = 2395
    city_list[u'伦敦'] = 2464
    # print([item[0] for item in results])
    for item in results:
        shop_url = item[2]
        shop_id = shop_url.split('/')[-1]
        city_code = city_list.get(item[3])
        avg_price_url = 'http://www.dianping.com/overseas/shop/ajax/reviewAndStar?shopId=%s&cityId=%s\
&mainCategoryId=102' % (shop_id,city_code)
        response = request.get(avg_price_url)
        price = get_avg_price(response)
        # sql2 = "select name,price from price_detail where name=:name"
        # price = dbmysql.first(sql2,{'name':item[1]})
        if price:
            print(price)
            sql3 = "update vendor_miqilin_price set price = :price,flag = 0 where vendor_id=:vendor_id"
            dbmysql.edit(sql3, params={'price': price, 'vendor_id': item[0]})
        else:
            sql3 = "update vendor_miqilin_price set flag = 1 where vendor_id=:vendor_id"
            dbmysql.edit(sql3, params={'vendor_id': item[0]})
            print(str(item[0]) + ' ' + item[1])

def get_price_class(price):
    flag = 3
    if price < 100:
        flag = 0
    elif price < 300:
        flag = 1
    elif price < 800:
        flag = 2
    return flag

def update_price_class():
    sql = 'select vendor_id,price from vendor_miqilin_price'
    results = dbmysql.fetchall(sql)
    for item in results:
        price_class = get_price_class(item[1])
        sql2 = "update vendor_miqilin_price set price_class=:price_class where vendor_id=:vendor_id"
        dbmysql.edit(sql2,params={'price_class':price_class,'vendor_id': item[0]})


if __name__ == '__main__':
    # get_dianping_city()
    # parse()
    update_price_class()
    # handle_privce()

