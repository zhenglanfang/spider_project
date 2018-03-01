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
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'
]

def get(url, session=None,params=None,headers=None, timeout=5,timeout_retry=5, **kwargs):
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
    if not headers:
        headers = {}
        headers['User-Agent'] = random.choice(ua_list)
    try:
        time.sleep(random.randint(1,2))
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
        # else:
        #     if timeout_retry > 0:
        #         htmlCode = get(url=url, session=session, params=params, headers=headers, timeout=timeout,
        #                        timeout_retry=(timeout_retry - 1), **kwargs)
        else:
            htmlCode = None
        request_url = url
        # print(url)
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
    if not headers:
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
        print ('Post %s %s' % (response.status_code, url))

    return htmlCode
