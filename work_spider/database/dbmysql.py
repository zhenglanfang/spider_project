#! /usr/bin/python
# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# import config 

# 配置文件中读取连接串
# DB_URI = config.DB.MYSQL_PROD
# pool_size连接池数量
# pool_recycle连接池中空闲时间超过设定时间后，进行释放
# echo输出日志
# create_engine 初始化数据库连接

MYSQL_PROD = "mysql+pymysql://root:root@127.0.0.1:3306/miqilin?charset=utf8"
DB_URI = MYSQL_PROD

engine = create_engine(DB_URI, echo=False, pool_size=50, pool_recycle=1800)

# 插入，修改，删除操作
def edit(sql,params=None):
    '''
    作用：插入，修改，删除 数据
    :param sql: 执行sql
    :return: 受影响的行数
    '''
    # 创建DBSession类型:
    DB_Session = sessionmaker(bind=engine)
    # 创建session对象:
    DB = DB_Session()
    try:
        # 执行sql语句
        result = DB.execute(text(sql),params)
        DB.commit()
        return result.rowcount
    except Exception, ex:
        print ("exec sql got error:%s" % (ex.message))
        DB.rollback()
        return False
    finally:
        DB.close()

# 查询第一条数据
def first(sql,params=None):
    '''
    作用：查询第一条数据
    :param sql: 查询语句
    :return: 查询数据
    first():返回元组，如果没有查询到数据返回None
    '''
    # 创建DBSession类型:
    DB_Session = sessionmaker(bind=engine)
    # 创建session对象:
    DB = DB_Session()
    try:
        # 执行sql语句，.first  session对象返回第一条数据
        #
        rs = DB.execute(text(sql),params).first()
        DB.commit()
        return rs
    except Exception, ex:
        print ("exec sql got error:%s" % (ex.message))
        DB.rollback()
        return False
    finally:
        DB.close()

# 查询多条数据
def fetchall(sql,params=None):
    '''
    作用：查询多条数据
    :param sql: 查询语句
    :return: 查询数据
    fetchall(): 返回列表，里面是元组；如果没有查询到返回 []
    '''
    # 创建DBSession类型:
    DB_Session = sessionmaker(bind=engine)
    # 创建session对象:
    DB = DB_Session()
    try:
        # 执行sql语句,.fetchall  session对象返回全部数据
        rs = DB.execute(text(sql),params).fetchall()
        DB.commit()
        return rs
    except Exception, ex:
        print ("exec sql got error:%s" % (ex.message))
        DB.rollback()
        return False
    finally:
        DB.close()

def test():
    # :url  代表参数
    sql = 'insert into urls(url,insert_time) values(:url,:insert_time)'
    from datetime import datetime
    rs = edit(sql,{'url':'py2','insert_time':datetime.now()})
    print(rs)
    sql = 'select * from urls where url=:url'
    rs = fetchall(sql,{'url':'py'})
    # 结果：[(2, u'py'), (4, u'py'), (5, u'py')]
    rs = fetchall(sql, {'url': 'p'})
    # 结果：[]
    rs = first(sql,{'url':'中国'})
    # 结果：(6, u'中国')
    rs = first(sql, {'url': '中'})
    # 结果：None
    print rs

if __name__ == '__main__':
    test()