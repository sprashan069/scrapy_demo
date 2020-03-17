from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import datetime, date, timedelta
from scrapy import signals
from scrapy import Spider
import re
import scrapy
import string
import json
import csv
import os


class PacsunSpider(scrapy.Spider):
    name = 'pacsun'
    allowed_domains = ['www.pacsun.com']
    status = True
    site_name = "www.pacsun.com"
    # header = { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36" }
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
    

    def start_requests(self):
        url = "https://www.pacsun.com/"
        yield scrapy.Request(url, headers=self.header, callback=self.parse)

    def parse(self, response):
        urls = response.xpath(
            '//div[@class="headermenu-wrp rwd-col-lrg-12-header"]/div/ul/li[2]/div/div/ul[2]/div/li/a/@href').extract()
        urls = urls + \
            response.xpath(
                '//div[@class="headermenu-wrp rwd-col-lrg-12-header"]/div/ul/li[2]/div/div/ul[3]/div/li/a/@href').extract()
        urls = list(dict.fromkeys(urls))
       

        for url in urls:
           
            yield scrapy.Request(url=url + "?country=IN", callback=self.parse_list,  headers=self.header, meta={"url": url + "?country=IN" + "?page=", "page": 0})

    def parse_list(self, response):
        urls = response.xpath(
            '//li[@class="rwd-col-2 rwd-col-lrg-3"]/div/div/a[1]/@href').extract()
        if(len(urls) > 0):
            for url in urls:
                yield scrapy.Request(url=url + "?country=IN", callback=self.parse_product, headers=self.header)
            yield scrapy.Request(url=response.meta['url'] + str(response.meta['page']+1), callback=self.parse_list, headers=self.header,
                                 meta={"url": response.meta['url'], "page": response.meta['page']+1})
    
    def parse_product(self, response):
        data = {}
        
        ################ Product details ################ 
        data['original_product_url'] = response.url
        data['product_name'] = response.xpath('normalize-space(//h1[@class="rwd-pdp-name rbto-bold"]/text())').extract_first()
       
        ################ Product Size ################ 
        data['size'] = response.xpath('//li[@class="rwd-attribute rwd-variant-dropdown"]/ul/li/a/text()').extract()
        for idx in range(len(data['size'])):
            data['size'][idx] = data['size'][idx].strip()
        data['size'] = list(dict.fromkeys(data['size']))

        ################ Product color ################ 
        data['color_image'] = response.xpath('//li[@class="rwd-swatch-pdp selectable selected selectorgadget_selected"]/img/@src').extract()
        if not data['color_image']:
            data['color_image'] = 'None'
        data['colors'] = response.xpath('normalize-space(//div[@class="rwd-swatch-value"]/text())').extract()

        if data['colors'] is None:
            data['colors'] = response.xpath('//li[@class="rwd-swatch-pdp selectable selected selectorgadget_selected"]/img/@alt').extract()
       
        data['description'] = response.xpath('normalize-space(//div[@class="rwd-pdp-desc-container"]/ul)').extract_first()
        data['gender'] = 'women'

        ################ Images ################
        # data['images'] =[]
        data['images'] = response.xpath('normalize-space(//div[@id="pdpMain"]/div/div/h1/text())').extract_first()
        # data['images'] = response.xpath('//div[@class="slick-track"]/div/div/a/img/@src').extract()
        print('~~~>  images', data['images'])
        
        # images = response.xpath('//div[@class="rwd-pdp-thumb slick-slide"]/div/a/img/@src').extract_first()
        # print('~~~~> image', data['images'])
        # data['images'] = response.xpath('//div[@class="pos-rel zi1"]/a/img/@src').extract_first()
        
        # print('~~~> images',data['images'])
        # for image in images:
        #     original_image = image.xpath('normalize-space(./img/@src)').extract_first()
        #     print('~~~~> image', original_image)
        
        ################ Product Price ################ 

        data['original_price'] = response.xpath('normalize-space(//div[@class="price-standard left"]/text())').extract_first().strip()[:]
        if not data['original_price']:
            data['original_price'] = response.xpath('normalize-space(//div[@class="price-standard left cart-promo-strike"]/text())').extract_first().strip()[:]

        
        data['sale_price'] = response.xpath('normalize-space(//div[@class="price-promo"]/text())').extract_first().strip()[:]
        
        data['special_offer'] = response.xpath('normalize-space(//span[@class="callout-message"]/p/span/strong/text())').extract_first()

        data['brand'] = response.xpath('normalize-space(//div[@id="pdpMain"]/div/div/a/img/@alt)').extract_first()
        
        data['website_name'] = self.name
        data['website_domain'] = self.site_name

        if not data['brand']:
            data['brand'] = "Pacsun"
        
        if not os.path.isfile('pacsun.csv'):
            with open('pacsun.csv', 'a', newline='', encoding= 'utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data.keys())
                writer.writeheader()

        with open('pacsun.csv', 'a', newline='',  encoding= 'utf-8') as csvfile2:
                writer2 = csv.DictWriter(csvfile2, fieldnames=data.keys())
                writer2.writerow(data)

process = CrawlerProcess(get_project_settings())
process.crawl(PacsunSpider)
process.start()

        

       
       
        