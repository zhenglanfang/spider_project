#! /usr/bin/python
# coding=utf-8

'''
对数据表的操作，数据表的增删查改操作
'''

import uuid
import dbmysql


# 判断url是否在数据库中存在
def isexist_url(url):
    '''
    作用：判断url是否在数据库中存在
    :param url: 查询的url
    :return: True:存在; None:不存在,False:出现异常
    '''
    sql = 'select url from urls where url=:url'
    result = dbmysql.first(sql, {'url':url})
    if result:
        return True
    else:
        return result

# 更新职位
def update_position(params):
    sql = 'update positions set position_name=:position_name,publish_date=:publish_date,education=:education,\
work_year=:work_year,job_nature=:job_nature,job_detail=:job_detail,salary=:salary,city=:city,district=:district,job_address=:job_address,\
company_name=:company_name,second_type=:second_type,first_type=:first_type where url=:url'
    result = dbmysql.edit(sql,params)
    return result

# 插入职位数据,应该设置回滚
def insert_position(params):
    '''
    作用：插入数据
    position_name       # 职位名称
    publish_date        # 发布时间
    education           # 学历
    work_year           # 工作经验
    job_nature          # 工作性质
    job_detail          # 职位描述
    salary              # 薪资
    city                # 城市
    district            # 地区
    job_address         # 工作地址
    company_name        # 公司名称
    first_type          # 职位类型
    second_type         # 职位类型
    url                 # 职位链接
    :return: 受影响的行数,False:出现异常
    '''
    sql = 'insert into positions(position_id,position_name,publish_date,education,work_year,job_nature,job_detail,salary,city,district,job_address,company_name,second_type,first_type,url) \
values("%s",:position_name,:publish_date,:education,:work_year,:job_nature,:job_detail,:salary,:city,:district,:job_address,:company_name,:second_type,:first_type,:url)'%str(uuid.uuid4())
    result = dbmysql.edit(sql, params)
    if result:
        result = insert_url(params.get('url'))
        # 如果url插入失败，这删除这条新闻
        if result==False:
            sql = 'delete from positions where url="%s"'%params.get('url')
            dbmysql.edit(sql)
    return result

# 插入url
def insert_url(url):
    '''
    作用：插入url
    :param url: 插入的url
    :return: 受影响的行数,False:出现异常
    '''
    sql = 'insert into urls(url,intime)  values(:url,now())'
    params = {
        'url':url
    }
    result = dbmysql.edit(sql, params)
    return result

def test():
    print isexist_url('py')
    params = {
        # 'uuid': 'uuid',
        'position_name':'java开发工程师',      
        'publish_date':'2017-12-30',        
        'education':'本科',           
        'work_year':'3-5年',     
        'job_nature':'全职',          
        'job_detail':'岗位职责--------',          
        'salary':'15k-25k',              
        'city':'杭州',               
        'district':'余杭区', 
        'job_address':'杭州-余杭区-....',
        'company_name':'认识医生',
        'first_type':'java',
        'second_type':'后端开发', 
        'first_type':'java',        
        'url':'https://www.lagou.com/jobs/3995898.html',                 
    }
    # print insert_position(params)
    print(update_position(params))
    # print insert_position(params).rowcount
    # print insert_position(params).returns_rows
    #print insert_url('www.baidu.com')

if __name__ == '__main__':
    test()