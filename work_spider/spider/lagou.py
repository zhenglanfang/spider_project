#! /usr/bin/python
# coding=utf-8

import sys
sys.path.append('/Users/mrs/Desktop/project/mytest/lagou/lagou_spider')

import datetime
import re
import requests
from lxml import etree
from database import db_operate
from util import request
from util import handle

start_url = 'https://www.lagou.com/'
second_url = 'https://www.lagou.com/jobs/list_%s?px=new&city=全国#order'

i = 0

def start_spider():
    response = request.get(start_url)
    if response:
        cookies = response.cookies
        html = etree.HTML(response.content)
        menu = html.xpath("//div[@class='menu_sub dn']")[0]
        positions_dict = {}
        types = menu.xpath("dl")
        for item in types:
            type_name = item.xpath("dt/span/text()")[0]
            # print(type_name)
            positions_dict[type_name] = {}
            positions = item.xpath("dd/a")
            for position in positions:
                position_name = position.text
                position_url = position.xpath('@href')[0]
                positions_dict[type_name][position_name] = position_url
                position_data = {'first_type':position_name,'second_type':type_name}
                get_positons_list(position_url,position_data,cookies)

        # return positions_dict


# 获取职位列表页
def get_positons_list(url,item,cookies):
    response = request.get(url,cookies=cookies)
    if response:
        html = etree.HTML(response.content)
        if html.xpath('//title/text()')[0] == '找工作-互联网招聘求职网-拉勾网':
            print(url + '  error ')
            return
        get_positions_urls(response,item,cookies)
        html = etree.HTML(response.content)
        page_num = html.xpath("//span[@class='span totalNum']/text()")
        page_num = int(page_num[0]) if page_num  else 1
        if page_num > 1:
            for num in range(2,page_num+1):
                list_url = '%s%d/'%(url,num)
                response = request.get(list_url,cookies=cookies)
                get_positions_urls(response,item,cookies)
        
# 获取列表页的urls
def get_positions_urls(response,item,cookies):
    if response:
        html = etree.HTML(response.content)
        print(html.xpath('//title/text()')[0] if html.xpath('//title/text()') else 'title error')
        item_list = html.xpath("//ul[@class='item_con_list']/li")
        for position in item_list:
            publish_date = position.xpath(".//span[@class='format-time']/text()")[0]
            publish_date = switch_publish_date(publish_date)
            url = position.xpath(".//a[@class='position_link']/@href")[0]
            # 判断url是否存在
            if not db_operate.isexist_url(url):
                position_name = position.xpath("@data-positionname")[0]
                salary = position.xpath("@data-salary")[0]
                other = position.xpath(".//div[@class='li_b_l']/text()")[2].strip()
                add = position.xpath(".//span[@class='add']/em/text()")[0]
                city = add.split('·')[0]
                company_name = position.xpath("@data-company")[0]
                item['position_name'] = position_name
                item['publish_date'] = publish_date
                item['salary'] = salary
                item['education'] = other.split('/')[1]
                item['work_year'] = other.split('/')[0][2:]
                item['city'] = city
                item['company_name'] = company_name
                item['url'] = url
                response = request.get(url,cookies=cookies)
                get_position_detail(response,item)
            else:
                print('此url%s已经存在！'%url)

# 获取详情页的数据
def get_position_detail(response,position):
    if response:
        html = etree.HTML(response.content)
        print(html.xpath('//title/text()')[0] if html.xpath('//title/text()') else 'error')
        # education = html.xpath("//dd[@class='job_request']/p[1]/span[4]/text()")
        # work_year = html.xpath("//dd[@class='job_request']/p[1]/span[3]/text()")
        job_nature = html.xpath("//dd[@class='job_request']/p[1]/span[5]/text()")
        # education = str(education[0]).strip('/') if education else ''
        # work_year = str(work_year[0]).strip('/') if work_year else ''
        job_nature = job_nature[0] if job_nature else ''
        job_detail = html.xpath("//dd[@class='job_bt']/div//text()")
        job_detail = [item.strip() for item in job_detail if item.strip()]
        job_detail = '\n'.join(job_detail).strip()
        job_address = html.xpath("//div[@class='work_addr']//text()")
        job_address = [item.strip() for item in job_address]
        job_address = ''.join(job_address[:-2])
        district = html.xpath("//div[@class='work_addr']/a[2]/text()")
        district = district[0] if district else ''
        position['job_nature'] = job_nature
        position['job_detail'] = job_detail
        position['job_address'] = job_address
        position['district'] = district
        save_infos(position)

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

# 过滤url和时间
def filter_url(info):
    '''
    作用：
    :param info: 单个新闻数据
    :return:
    '''
    url = info.get('url')
    # print url
    # 如果url已经存在
    if db_operate.isexist_url(url):
        return False
    # 得到职位发布时间
    pass
    # 判断是不是当天的时间
    # if not handle.compare_datetime(ctime):
    #     return False

def generate_counter(func):
    '''
    计数器
    '''
    cont = [0]
    def inner(*args,**kwargs):
        result = func(*args,**kwargs)
        if result:
            cont[0] = cont[0] + 1
            print('第%s条数据插入成功！'%(cont[0]))
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


if __name__ == '__main__':
    # for i in range(20):
    #     save_infos().next()
    start_spider()



