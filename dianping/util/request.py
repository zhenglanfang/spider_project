#! /usr/bin/python
# coding=utf-8
'''
作用：对post和get请求进行封装
'''

import requests
import random
import urllib
import time

# User-Agent：列表
ua_list = [
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
]

cookies = 'user_trace_token=20171229140822-1173f42b-7651-4775-807d-1d15c92b8583; _ga=GA1.2.452548855.1514527703; LGUID=20171229140823-ad118fa6-ec5e-11e7-b6b0-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD; JSESSIONID=ABAAABAAAGGABCBF8AC449D3A918158039BB7E4043B6BED; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1514527704,1514606718; _gid=GA1.2.1346778819.1514775097; X_HTTP_TOKEN=fe3b7d8455518a53a92a677154122af9; TG-TRACK-CODE=index_navigation; LGSID=20180102165624-cf968a27-ef9a-11e7-9fc4-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fzhaopin%2FC%2F9%2F; SEARCH_ID=a5165c7677f64c4a9f0a9fed92792a5a; _gat=1; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1514884692; LGRID=20180102171811-dab9537b-ef9d-11e7-ba00-525400f775ce'

def get(url, session=None,params=None,headers={}, timeout=5,timeout_retry=5, **kwargs):
    '''
    作用：发送get请求
    :param url: 目标链接
    :param session: requests.session() 对象
    :param params: 参数
    :param headers: 请求头部
    :param timeout: 请求超时时间
    :param timeout_retry: 超时重试次数
    :param kwargs:  Optional arguments that ``request`` takes.
    :return: 响应对象
    '''
    if not url:
        print ('GetError url not exit')
        return None
    headers['User-Agent'] = random.choice(ua_list)
    headers['Cookie'] = cookies
    try:
        time.sleep(random.randint(1,3))
        # 如果传递了session，使用该对象发送请求,否则使用requests发送请求
        if session:
            response = session.get(url, params=params, headers=headers, timeout=timeout,verify=False,**kwargs)
        else:
            response = requests.get(url, params=params, headers=headers, timeout=timeout,verify=False,**kwargs)
    except Exception as e:
        print ('GetExcept %s' % e.message)
        if timeout_retry > 0:
            htmlCode = get(url=url,session=session,params=params,headers=headers, timeout=timeout,timeout_retry=(timeout_retry-1), **kwargs)
        else:
            htmlCode = None
    else:
        # 请求成功
        if response.status_code == 200 or response.status_code == 302:
            htmlCode = response
        else:
            htmlCode = None
        request_url = url
        if params:
            request_url = '%s?%s'%(url,urllib.urlencode(params))
        print ('Get %s %s' % (response.status_code, request_url))

    return htmlCode

def post(url, session=None,data=None,headers={}, timeout=5,timeout_retry=5,**kwargs):
    '''
    作用：发送post请求
    :param url: 目标链接
    :param session: requests.session() 对象
    :param data: 参数
    :param headers: 请求头部
    :param timeout: 请求超时时间
    :param timeout_retry: 超时重试次数
    :param kwargs:  Optional arguments that ``request`` takes.
    :return: 响应对象
    '''
    if not url:
        print ('PostError url not exit')
        return None
    headers['User-Agent'] = random.choice(ua_list)
    try:
        time.sleep(1)
        # 如果传递了session，使用该对象发送请求,否则使用requests发送请求
        if session:
            response = session.post(url, data=data, headers=headers, timeout=timeout, verify=False,**kwargs)
        else:
            response = requests.post(url, data=data, headers=headers, timeout=timeout, verify=False,**kwargs)
    except Exception as e:
        print ('PostExcept %s' % e.message)
        if timeout_retry > 0:
            htmlCode = post(url=url,session=session,data=data,headers=headers, timeout=timeout,timeout_retry=(timeout_retry-1), **kwargs)
        else:
            htmlCode = None
    else:
        # 请求成功
        if response.status_code == 200 or response.status_code == 302:
            htmlCode = response
        else:
            htmlCode = None
        print ('Post %s %s data:%s' % (response.status_code, url , data))

    return htmlCode
