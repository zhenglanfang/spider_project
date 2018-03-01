# -*- coding: utf-8 -*-
import scrapy

from urllib import request
from michelin.spiders import util

class OpentableSpider(scrapy.Spider):
    name = 'opentable'
    allowed_domains = ['opentable.com']
    host = 'https://www.opentable.com'

    # url:metroId=72 london,8 newyork  term 餐厅
    url = 'https://www.opentable.com/s/?covers=2&metroId=72&term=%s'
    names = util.get_names('newyork')
    start_urls = ['https://www.opentable.com/s/?covers=2&metroId=8&term=%s'%(name) for name in names]

    # start_urls = ['https://www.opentable.com/s/?covers=2&metroId=8&term=Caffe dei Fiori']

    def parse(self, response):
        name = response.url.split('term=')[-1]
        name = request.unquote(name)
        item = {'name':name,'dish':'','Operation time':'','url':response.url}
        start_a = response.xpath("//a[@class='rest-row-name rest-name ']")
        if start_a:
            start_a =start_a[0]
            first_name = start_a.xpath("./span[@class='rest-row-name-text']//text()").extract()
            first_name = ''.join(first_name)
            if first_name == name:
                url = '%s%s'%(self.host,start_a.xpath('./@href').extract()[0])
                yield scrapy.Request(url=url,callback=self.get_detail,meta={'name':name})
            else:
                yield item
        else:
            yield item


    def get_detail(self,response):
        name = response.meta.get('name')
        # print(name)
        detail_hours = response.xpath("//li[@class='restaurant-detail detail-hours']")
        if detail_hours:
            detail_hours = detail_hours.xpath("./div[@class='detail-content line-height-large']/text()").extract()
            detail_hours = '||'.join(detail_hours)
        else:
            detail_hours = ''
        dish = response.xpath("//div[@class='rest-menu-links content-block-body']/a/text()").extract()
        menu_ids = [response.xpath("//div[@id='menu-%d']"%(i))[0] for i in range(1,len(dish)+1)]
        dish_dict = {}
        for index, menu in enumerate(menu_ids):
            dish_dict[dish[index]] = {}
            menu_sections = menu.xpath(".//div[@class='rest-menu-section']")
            section_dict = {}
            for sections in menu_sections:
                title = sections.xpath(".//h5[@class='font-weight-bold']/text()").extract()
                if title:
                    title = title[0]
                else:
                    title = 'not title'
                section_dict[title] = sections.xpath(".//div[@class='rest-menu-item-title']/text()").extract()
                section_dict[title] = ','.join(section_dict[title])
            dish_dict[dish[index]] = section_dict
        # print(dish_dict)
        item = {
            'name':name,
            'dish':dish_dict,
            'Operation time':detail_hours,
            'url':response.url,
        }
        yield item














