#! /usr/bin/python
# coding=utf-8

import sys
sys.path.append('/Users/mrs/Desktop/project/spider_project/dianping')

import datetime
from lxml import etree
from database import db_operate
from util import request

def get_names(city):
    with open('../data/%s.txt' % city, 'r') as f:
        for line in f.readlines():
            name = line.strip()
            yield name

num = 0
def get_cookie_num():
    global num
    num += 5
    yield num

start_url = 'http://www.dianping.com/'
second_url = 'https://www.dianping.com/search/keyword/342/0_%s'
names = get_names('macau')
start_num = get_cookie_num()

headers = {
    'Host': 'www.dianping.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer':'http://www.dianping.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': '_lxsdk_cuid=1605e058099c8-0c85123882d008-32647e03-1fa400-1605e05809ac8; _lxsdk=1605e058099c8-0c85123882d008-32647e03-1fa400-1605e05809ac8; _hc.v=a385c03d-5aea-3ce6-e2ab-955a69b47ad8.1513405908; aburl=1; _tr.u=cRJ4IaRPLypZIJ6q; cy=1; cye=shanghai; s_ViewType=10; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; __mta=243171005.1513405935234.1515407551351.1515409225483.77; _lxsdk_s=160d544c1b4-d4c-5a9-3ab%7C%7C'
}

def start_spider():
    response = request.get(start_url)
    if response:
        html = etree.HTML(response.content)
        name = names.next()
        headers['Cookie'] = headers['Cookie'] + str(start_num.next())
        for name in names:
            get_shop_url(second_url%name,name,headers)
    else:
        print(response)
        # return positions_dict

def get_shop_url(url,name,headers):
    response = request.get(url,headers=headers)
    if response:
        html = etree.HTML(response.content)
        shop_names = html.xpath("//div[@class='txt']/div[@class='tit']/a")
        # and shop_names[0].xpath('h4/text()')[0] == name
        if shop_names:
            title = shop_names[0].xpath('h4/text()')[0]
            shop_url = shop_names[0].xpath('@href')[0]
            avg_price = html.xpath("//a[@class='mean-price']/b/text()")[0] \
                    if html.xpath("//a[@class='mean-price']/b/text()") else ''
            cuisine = html.xpath("//span[@class='tag']/text()")[0] \
                    if html.xpath("//span[@class='tag']") else ''
            tag_addr = html.xpath("//div[@class='tag-addr']/a")
            if len(tag_addr) > 2:
                tag_addr = tag_addr[1].xpath("span[@class='tag']/text()")[0]
            else:
                tag_addr = ''
            addr = html.xpath("//div[@class='tag-addr']/span[@class='addr']/text()")[0] \
                    if html.xpath("//div[@class='tag-addr']/span[@class='addr']/text()") else ''
            preferences = html.xpath("//div[@class='svr-info']/a[contains(@class,'tuan')]/text()")[0] \
                    if html.xpath("//div[@class='svr-info']/a[contains(@class,'tuan')]") else ''

            item = {
                'title':title,
                'shop_url' : shop_url,
                'avg_price' : avg_price,
                'cuisine' : cuisine,
                'tag-addr' : tag_addr,
                'addr' : addr,
                'preferences': preferences    


            }
            print(item)


# 转换时间
def switch_publish_date(publish_date):
    '''
    处理发布时间
    :param publish_date:
    :return:
    '''
    if publish_date.endswith('发布'):
        today = datetime.date.today()
        if publish_date.find(':') == -1:
            delta = int(publish_date[0])
            publish_date = today - datetime.timedelta(days=delta)
            return publish_date
        else:
            return today
    else:
        return publish_date

# 获取返回的json
def get_json(type,kw,url):
    params = ''
    response = request.get(url,params=params)
    if response:
        return response.json()
    else:
        return None

# 计数器
def generate_counter(func):
    '''
    计数器
    '''
    cont = [0]
    def inner(*args,**kwargs):
        result = func(*args,**kwargs)
        if result:
            cont[0] = cont[0] + 1
            print '第%s条数据插入成功！'%(cont[0])
        return result
    return inner

@generate_counter
def save_infos(data):
    '''
    作用：保存数据
    '''
    t = db_operate.insert_position(data)
    if not t:
        print('数据插入失败!')
    return t

if __name__ == '__main__':
    # for i in range(20):
    #     save_infos().next()
    start_spider()
    # names = get_names('macau')
    # print(names.next())
    # print(names.next())
    #
    # t = get_cookie_num()
    # print(t.next())


