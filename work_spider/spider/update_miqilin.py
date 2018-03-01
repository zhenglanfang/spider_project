#coding:utf-8

import re
import json

from database import dbmysql
from util.langconv import switch_lang
from util import request

ak = 'pYsv49CQjUD25TDzSBYNZjsnpCkZetFz'

gaode_address = 'http://restapi.amap.com/v3/geocode/geo?key=7f425c69c2cd03dff3ff882ff72be07a&address=%s&city=香港'

gaode_latlng = 'http://restapi.amap.com/v3/geocode/regeo?location=114.227371,22.279678&key=7f425c69c2cd03dff3ff882ff72be07a'

google_address = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=AIzaSyBHdvNEymvYtFTQbQ6Co7CKjl1qHNYvEgM'

google_latlng = 'https://maps.google.cn/maps/api/geocode/json?latlng=22.281851,114.185185&key=AIzaSyC5xFbz-q11fdrZicGkaIoOVdPYcKNLm1M'

baidu_address = 'http://api.map.baidu.com/geocoder/v2/?address=%s&output=json&ak=pYsv49CQjUD25TDzSBYNZjsnpCkZetFz&city=%s'

baidu_latlng = 'http://api.map.baidu.com/geocoder/v2/?callback=renderReverse&location=22.284665,114.222243&output=json&pois=1&ak=pYsv49CQjUD25TDzSBYNZjsnpCkZetFz'

# 转换简体
def update_langconv():
    sql = 'select * from vendor_miqilin'
    data = dbmysql.fetchall(sql)
    for item in data:
        name = switch_lang.Traditional2Simplified(item['vendor_name'])
        description = switch_lang.Traditional2Simplified(item['description'])
        dish = switch_lang.Traditional2Simplified(item['dish'])
        recomm_dish = switch_lang.Traditional2Simplified(item['recomm_dish'])
        address = switch_lang.Traditional2Simplified(item['address'])
        update_sql = 'update vendor_miqilin set vendor_name=:vendor_name,description=:description,dish=:dish,' \
                     'recomm_dish=:recomm_dish,address=:address where vendor_id=:vendor_id'
        params = {
            'vendor_name':name,
            'description':description,
            'dish':dish,
            'recomm_dish':recomm_dish,
            'address':address,
            'vendor_id':item['vendor_id']
        }
        dbmysql.edit(update_sql,params)


def update_latlng():
    sql = 'select * from vendor_miqilin_hongkong where vendor_id'
    data = dbmysql.fetchall(sql)
    for item in data:
        address = item['address']
        result = request.get(baidu_address%(address,'香港'))
        result = json.loads(result.content)
        if result.get('status') == 0:
            update_sql = 'update vendor_miqilin set lat=:lat,lng=:lng where vendor_id=:vendor_id'
            params = {
                'lat':result['result']['location'].get('lat'),
                'lng':result['result']['location'].get('lng'),
                'vendor_id': item['vendor_id']
            }
            dbmysql.edit(update_sql, params)
        else:
            update_sql = 'update vendor_miqilin set lat_flag = 1 where vendor_id=:vendor_id'
            dbmysql.edit(update_sql,{'vendor_id': item['vendor_id']})
            print(str(item['vendor_id']))


def get_price_class(price):
    flag = 3
    if price < 100:
        flag = 0
    elif price < 300:
        flag = 1
    elif price < 800:
        flag = 2
    return flag


def check(name,address,check_name,check_address):
    name = name.lower()
    # name = switch_lang.Traditional2Simplified(name)
    address = address.lower()
    # address = switch_lang.Traditional2Simplified(address)
    check_name = check_name.lower()
    # check_name = switch_lang.Traditional2Simplified(check_name)
    check_address = check_address.lower()
    # check_address = switch_lang.Traditional2Simplified(check_address)
    if len(name) > len(check_name):
        name,check_name = check_name,name
    if len(address) > len(check_address):
        address,check_address = check_address,address
    # 判断name
    if check_name.find(name) == -1:
        return 0
    # 判断地址
    if check_address.find(address) == -1:
        # 判断 需要判断 经纬度
        return  2
    else:
        return 1


def check_address(address,check_address):
    address = address.lower()
    address = switch_lang.Traditional2Simplified(address)
    if not check_address:
        check_address = ''
    check_address = check_address.lower()
    check_address = switch_lang.Traditional2Simplified(check_address)
    if len(address) > len(check_address):
        address,check_address = check_address,address
    if check_address.find(address) == -1:
        return False
    else:
        return True


def update_shop():
    raw_shops_sql = "select vendor_id,vendor_name,description,address,recomm_dish from vendor_miqilin where dish = ''"
    check_shops_sql = "select vendor_name,description,address,recomm_dish from vendor_miqilin_quna where recomm_dish != ''"
    raw_shops = dbmysql.fetchall(raw_shops_sql)
    check_shops = dbmysql.fetchall(check_shops_sql)
    num = 0
    for shop in raw_shops:
        shop_name = shop['vendor_name']
        shop_address = shop['address']
        for check_shop in  check_shops:
            flag = check_address(shop_name,shop_address,check_shop['vendor_name'],check_shop['address'])
            if flag:
                update_sql = 'update vendor_miqilin set dish=:dish where vendor_id=:vendor_id'
                update_data = {
                    'dish':check_shop['recomm_dish'],
                    'vendor_id':shop['vendor_id']
                }
                effect = dbmysql.edit(update_sql,update_data)
                if effect:
                    num += 1
                    print(shop_name)

    print(num)


def update2_shop():
    raw_shops_sql = "select vendor_id,vendor_name,address,ctrip_address,ctrip_dish from vendor_miqilin where dish = '' and ctrip_dish != ''"
    # check_shops_sql = "select vendor_name,description,address,recomm_dish from vendor_miqilin_quna where recomm_dish != ''"
    raw_shops = dbmysql.fetchall(raw_shops_sql)
    # check_shops = dbmysql.fetchall(check_shops_sql)
    num = 0
    for shop in raw_shops:
        # shop = dict(shop)
        shop_name = shop['vendor_name']
        shop_address = shop['address']
        flag = check_address(shop_address, shop['ctrip_address'])
        if flag:
            update_sql = 'update vendor_miqilin set dish=:dish where vendor_id=:vendor_id'
            update_data = {
                'dish': shop['ctrip_dish'],
                'vendor_id': shop['vendor_id']
            }
            effect = dbmysql.edit(update_sql, update_data)
            if effect:
                num += 1
                print(shop_name)

    print(num)


def update_price():
    sql = 'select vendor_id,price from vendor_miqilin'
    result = dbmysql.fetchall(sql)
    i = 0
    for item in result:
        price = item['price'] * 0.8054
        price = int(price)
        price_class = get_price_class(price)
        update_sql = 'update vendor_miqilin set price=:price,price_class=:price_class where vendor_id=:vendor_id'
        params = {
            'price':price,
            'price_class':price_class,
            'vendor_id':item['vendor_id'],
        }
        i += 1
        dbmysql.edit(update_sql,params)
    print(i)


def filter_facilities(facilities):
    facilities = facilities.decode('utf-8')
    del_facilities = [u'酒精饮料', u'网上订座', u'加一服务费', u'深夜营业', u'电话订座', u'外卖服务', u'切蛋糕费', u'当面支付', u'24小时营业', u'自带酒水', u'电视播放', u'球赛直播',
                      u'赏订座积分', u'到会服务', u'详细介绍', u'任食火锅', u'一人一锅']
    facilities = facilities.split(';')
    facilities = set(facilities) - set(del_facilities)
    return ';'.join(facilities)


def filter_preferential(preferential):
    preferential = preferential.replace(u'乙',u'一').replace(u'饮嘢',u'享')
    del_preferencetial = [u'最后召集75折优惠',u'提供网上订座',u'送 25里数 / 30积分',u'现凡使用Open rice订座於8:00前离座可享10%off',u'送 50里数 / 60积分',
                          u'餐厅优惠月: 网上订座享晚市单点食品8折', u'来佬经典套餐再现',u'Openrice会员专享优惠',u'2月最新订坐优惠。现凡於openrice 订坐 可享9折优惠 （优惠只限於星期日至星期四晚市时段入座）',
                          u'经openrice订座9折优惠',u'经Openrice订座可享有88折优惠',u'成功经OpenRice订座及下午1点前结账离座 全单85折！',u'以$320每位享用OPENRICE尊享午市套餐或',
                          u'OpenRice 专享 所有食品一律8折',u'OpenRice 专享原价$588 避风塘炒蟹特惠价$288(真材实料1斤2两重)']
    preferential = preferential.split(';')
    preferential = set(preferential) - set(del_preferencetial)
    return ';'.join(preferential)


def filter_data():
    sql = 'select * from vendor_miqilin'
    data = dbmysql.fetchall(sql)
    for item in data:
        cuisine = re.sub(r'\(.*?\)','',item['cuisine']).replace('、',';')
        facilities = filter_facilities(item['facilities'])
        preferential = filter_preferential(item['preferential'])

        update_sql = 'update vendor_miqilin set cuisine=:cuisine,facilities=:facilities,preferential=:preferential where vendor_id=:vendor_id'
        params = {
            'cuisine':cuisine,
            'facilities':facilities,
            'preferential':preferential,
            'vendor_id':item['vendor_id']
        }
        dbmysql.edit(update_sql,params=params)

def add_guanjia():
    guanjia_hongkong = 'select * from vendor_miqilin_hongkong where vendor_city = "香港"'
    guanjia_hongkong = dbmysql.fetchall(guanjia_hongkong)
    add_hongkong = 'select * from vendor_miqilin'
    add_hongkong = dbmysql.fetchall(add_hongkong)
    add_id = []
    for item in add_hongkong:
        for i in guanjia_hongkong:
            flag = check(item['vendor_name'],item['address'],i['name'],i['address'])
            if flag == 2:
                if item['lat'] == i['lat'] and item['lng'] == i['lng']:
                    flag = 1
                else:
                    flag = 0
            if flag == 1:
                add_id.append(item['vendor_id'])
                break

        if flag == 0:
            add_sql = "insert into vendor_miqilin_hongkong(name, book_status, facilities,district, landmark, preferential, environment, " \
                      "description, payment, price_class,michelin_star,quality, dish,recomm_dish, cuisine, taste,category, " \
                      "people_group,open_time, close_time, price, address, lat, lng, vendor_city, vendor_url)" \
                      " values(:vendor_name, :book_status, :facilities,:district, :landmark, :preferential, " \
                      ":environment, :description, :payment, :price_class,:michelin_star,:quality, :dish," \
                      ":recomm_dish, :cuisine, :taste, :category, :people_group, :open_time, " \
                      ":close_time, :price, :address, :lat, :lng, :vendor_city, :vendor_url)"

            dbmysql.edit(add_sql, item)
    print(add_id)





if __name__ == '__main__':
    # update_shop()
    # filter_data()
    # update_price()
    # update_langconv()
    # print(switch_lang.Traditional2Simplified('舖'))
    # update_latlng()
    add_guanjia()