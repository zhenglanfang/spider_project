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
    'book_status':'', #预定
    'facilities':'', # 设施
    'district':'', #区
    'landmark':'',
    'preferential':'', #优惠
    'environment':'', #环境
    'description':'',
    'payment':'',
    'price_class':'',
    'michelin_star':'', #无
    'quality':'', #无
    'brand':'', #无
    'dish':'',
    'recomm_dish':'',
    'cuisine':'',
    'taste':'', #无
    'characters':'', #特点
    'category':'', #类型
    'people_group':'', #无
    'open_time':'',
    'close_time':'',
    'price':'',
    'address':'',
    'lat':'',
    'lng':'',
    'vendor_city':'香港',
    'vendor_url':'',
    'price_range':'',
    'business_hours':'', #营业时间
    'score_details':'',  #评级
    'openrich_url':'',
    'tripadvisor_url':'',
    'tripadvisor_cuisine':'',
    'tripadvisor_character':'',#tripadvisor中的特点
    'create_time':'',
    'phone':'',
    'appraise':'' #评价
}

res_category = {'酒吧', '会所', '楼上cafe', '快餐/简餐', '自助餐', '茶馆', '咖啡店', '茶餐厅/冰室', '扒房','面包店',}

openrice_url = 'https://www.openrice.com/zh-cn/hongkong/restaurants'

openrice_district_url = 'https://www.openrice.com/zh-cn/hongkong/restaurants/district/%s?page=%s'

openrice_cuisine_url = 'https://www.openrice.com/zh-cn/hongkong/restaurants/cuisine/%s?page=%s'

openrice_host = 'https://www.openrice.com'

tripadvisor_url = 'https://www.tripadvisor.cn/Search?geo=294217&pid=3826&q=%s'

tripadvisor_host = 'https://www.tripadvisor.cn'


def parse():
    response = request.get(openrice_url)
    if response:
        html = etree.HTML(response.content)
        districts = html.xpath("//div[@class='flex-wrap js-flex-wrap']/div[contains(@class, 'btn')]/@data-tag")
        for district in districts[94:167]:
            print('%s---开始'%district)
            for i in range(1,18):
                if district.startswith('所有'):
                    continue
                district = district.replace(' (','-').replace(')','')
                url = openrice_cuisine_url%(district,i)
                response = request.get(url)
                if response:
                    html = etree.HTML(response.content)
                    shops = html.xpath("//div[@class='content-cell-wrapper']")
                    for shop in shops:
                        shop_item = item.copy()
                        name = shop.xpath(".//h2[@class='title-name']/a/text()")[0]
                        if exist(name):
                            print(name + '已经存在')
                            continue
                        recomm_dish = get_node_list(shop.xpath(".//ul[@class='dish-list']/li[@class='dish']/text()"))
                        book_status = get_book_status(shop.xpath(".//a[@class='info-button info-offer-button']/text()"))
                        preferential = get_node_list(shop.xpath(".//span[@class='info-text info-offer-text']/text()"))
                        shop_url = shop.xpath(".//h2[@class='title-name']/a/@href")[0]
                        shop_item['vendor_name'] = name
                        shop_item['recomm_dish'] = recomm_dish
                        shop_item['book_status'] = book_status
                        shop_item['preferential'] = handle_emjoy(preferential)
                        shop_detail(shop_url,shop_item)
                    print('第%s页完成'%i)
                else:
                    print ('请求失败%s'%url)

            print('%s完成' % district)


def shop_detail(url, item):
    url = openrice_host + url
    shop_id = url.rsplit('-r')[-1]
    response = request.get(url)
    if response:
        text = response.text
        html = etree.HTML(response.content)
        text = text.replace('\n', '').replace('\r', '')
        text = text.decode('utf-8')
        dish = re.search(r'主要菜式包括 (.*?), 。'.decode('utf-8'),text)
        if dish:
            dish = dish.group(1).replace(', ',';')
            item['dish'] = dish
        application_json = re.search(r'"application/ld\+json">(.*?)</script>',text)
        if application_json:
            try:
                application_json = application_json.group(1)
                application_json = json.loads(application_json)
                cuisine = application_json.get('servesCuisine','')
                price_range = application_json.get('priceRange','')
                phone = application_json.get('telephone','')
                url = application_json.get('url','')
                lat = application_json['geo']['latitude']
                lng = application_json['geo']['longitude']
                district = application_json['address']['addressLocality']
                address = district + application_json['address']['streetAddress']
                item['cuisine'] = cuisine
                item['price_range'] = price_range
                item['price'] = handle_price(price_range)
                item['price_class'] = get_price_class(item['price'])
                item['phone'] = phone
                item['lat'] = lat
                item['lng'] = lng
                item['district'] = district
                item['address'] = address
                item['openrich_url'] = url
            except Exception as e:
                print(e)
        description = handle_node(html.xpath("//section[@class='introduction-section']/div[@class='content js-text-wrapper']/text()"))
        characters = handle_node(html.xpath("//section[@class='good-for-section']/div[@class='content']/text()"))
        payment = handle_node(html.xpath("//div[@id='pois-filter-expandable-features']//div[@class='comma-tags']//text()"))
        facilities = handle_node(html.xpath("//span[@class='or-sprite-inline-block d_sr2_lhs_tick_desktop']/following-sibling::span/text()"))
        none_facilities = html.xpath("//span[@class='or-sprite-inline-block d_sr2_lhs_cross_desktop']/following-sibling::span/text()")
        category = handle_node(html.xpath("//div[@class='header-poi-categories dot-separator']/div/a[contains(@href,'/type/')]/text()"))
        score_details = html.xpath("//div[@class='header-score-details-right-item']")
        score_details = get_score_details(score_details)
        business_hours = get_business_hours(shop_id)
        if business_hours:
            item['business_hours'] = json.dumps(business_hours['business_hours'],ensure_ascii=False,indent=2)
            item['open_time'] = business_hours.get('open_time')
            item['close_time'] = business_hours.get('close_time')

        if handle_book(facilities.split(';')):
            item['book_status'] = 0

        if handle_no_book(none_facilities):
            item['book_status'] = 2

        item['description'] = description
        item['characters'] = characters
        item['payment'] = payment
        item['facilities'] = facilities
        item['category'] = category
        item['score_details'] = json.dumps(score_details,ensure_ascii=False,indent=2)
        # print(item)
        tripadvisor(item)
    else:
        print('请求失败%s'%url)


def tripadvisor(item):
    url = tripadvisor_url%item['vendor_name']
    response = request.get(url)
    if response:
        html = etree.HTML(response.content)
        title = html.xpath("//div[@class='title']/span/text()")
        address = html.xpath("//div[@class='address']/text()")
        if title and address:
            name = item['vendor_name'].lower()
            address2 = item['address'].lower().replace('楼','')
            if title[0].lower().find(name) == -1 or address[0].lower().find(address2) == -1:
                pass
            else:
                url = html.xpath("//div[@class='title']/@onclick")
                url = re.findall(r'\'(.*?)\'',url[0])[3]
                url = tripadvisor_host + url
                response = request.get(url)
                if response:
                    html = etree.HTML(response.content)
                    rows = html.xpath("//div[@class='row']")
                    for row in rows:
                        row_title = row.xpath("./div[@class='title']/text()")
                        if row_title:
                            row_title = row_title[0].strip()
                        row_content = row.xpath("./div[@class='content']//text()")
                        row_content = handle_node(row_content)
                        if row_title == '菜系':
                            item['tripadvisor_cuisine'] = row_content
                        elif row_title == '餐厅特点':
                            item['tripadvisor_character'] = row_content
                        elif row_title == '就餐氛围':
                            item['environment'] = row_content

                    item['tripadvisor_url'] = url
                else:
                    print('请求失败'+url)
    else:
        print('请求失败'+url)
    save_date(item)


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
    sql = 'insert into vendor_miqilin(vendor_name,book_status,facilities,district,landmark,preferential,environment,description,payment,price_class,'+\
            'michelin_star,quality,brand,dish,recomm_dish,cuisine,taste,characters,category,people_group,open_time,close_time,price,address,lat,lng,vendor_city,'+\
            'vendor_url,price_range,business_hours,score_details,openrich_url,tripadvisor_url,phone,tripadvisor_cuisine,tripadvisor_character,appraise)' +\
            ' values(:vendor_name,:book_status,:facilities,:district,:landmark,:preferential,:environment,:description,:payment,:price_class,' +\
            ':michelin_star,:quality,:brand,:dish,:recomm_dish,:cuisine,:taste,:characters,:category,:people_group,:open_time,:close_time,:price,:address,:lat,:lng,:vendor_city,' +\
            ':vendor_url,:price_range,:business_hours,:score_details,:openrich_url,:tripadvisor_url,:phone,:tripadvisor_cuisine,:tripadvisor_character,:appraise)'
    return dbmysql.edit(sql,item)


def exist(name):
    sql = 'select vendor_name from vendor_miqilin where vendor_name=:vendor_name'
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


def get_score_details(node):
    score_dict = {}
    for item in node:
        key = item.xpath("./div[1]/text()")[0]
        value = item.xpath("./div[2]/@class")[0]
        value = re.findall(r'common_rating(\d+)_red',value)[0].replace('0','')
        score_dict[key] = value
    return score_dict


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




