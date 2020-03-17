from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import datetime,date, timedelta
from scrapy import signals
from scrapy import Spider
import re
import scrapy
import string
import json
import csv
import os

class Tobispider(Spider):
    name = "tobi"
    allowed_domains = ["www.tobi.com"]
    status = True
    site_name = "www.tobi.com"
    header = { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36" }
    # download_delay =7
    def start_requests(self):
      url = "https://www.tobi.com/"
      yield scrapy.Request(url, headers = self.header, callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//div[@class="nav nav-header nav-inline"]/ul/li[1]/div/div/div/div/div/a/@href').extract()
        print('~~~~> urls1', urls)
        urls = urls + response.xpath('//div[@class="nav nav-header nav-inline"]/ul/li[2]/div/div/div/div/div/a/@href').extract()
        print('~~~~> urls2', urls)
        urls = urls + response.xpath('//div[@class="nav nav-header nav-inline"]/ul/li[3]/div/div/div/div/div/a/@href').extract()
        print('~~~~> urls3', urls)
        urls = list(dict.fromkeys(urls))
        for url in urls:
            yield scrapy.Request(url="https://www.tobi.com" + url, callback=self.parse_list, headers = self.header, meta = {"url":"https://www.tobi.com" + url + "?page=", "page": 0 })

    def parse_list(self, response):
        urls = response.xpath('//div[@class="product-list-item"]/div/div/div/a/@href').extract()
        if(len(urls) > 0):
            for url in urls:
                yield scrapy.Request(url="https://www.tobi.com" + url, callback=self.parse_product, headers=self.header)
            yield scrapy.Request(url=response.meta['url'] +str(response.meta['page']+1) , callback=self.parse_list, headers=self.header,
                                 meta={"url": response.meta['url'], "page": response.meta['page']+1})

    def parse_product(self, response):
        data = {}
        data['original_product_url'] = response.url
        data['product_name'] = response.xpath('normalize-space(//h1[@id="product-detail-title"]/text())').extract_first()

        ##################Size############
        data['size'] = response.xpath('//span[text()="Size"]/following-sibling::ul[1]/li[@data-sizeid]/text()').extract()
        for idx in range(len(data['size'])):
            data['size'][idx] = data['size'][idx].strip()
        data['size'] = list(dict.fromkeys(data['size']))

        ##################Color############
        data['color_image'] = response.xpath('//li[@data-colorid]/img/@src').extract()
        data['colors'] = response.xpath('//li[@data-colorid]/img/@alt').extract()


        data['description'] = response.xpath('normalize-space(//div[@id="description"])').extract_first()
        data['gender'] = 'women'
        data['category'] = response.xpath('normalize-space(//ol[@class="product-list-breadcrumb-desktop product-list-margin-top-offset breadcrumb clearfix"]/li[2]/a/text())').extract_first()
        data['subcategory'] = response.xpath('normalize-space(//ol[@class="product-list-breadcrumb-desktop product-list-margin-top-offset breadcrumb clearfix"]/li[3]/a/text())').extract_first()

        ################ Images ################
        data['images'] =[]
        images = response.xpath('//div[@class="desktop-thumbs"]/a')
        for image in images:
            thumb = image.xpath('normalize-space(./img/@data-lazy-src)').extract_first()
            large = image.xpath('normalize-space(./img/@data-image-large)').extract_first()
            data['images'].append({'thumb': thumb, 'origin': large})


        status = response.xpath('normalize-space(//span[@class="product-detail-label product-detail-status"]/text())').extract_first()
        
        ################ Original Price ################
        data['original_price'] = response.xpath('normalize-space(//span[@class="original-price"]/text())').extract_first().strip()[1:]
        if not data['original_price']:
            data['original_price'] = response.xpath(
                'normalize-space(//span[@class="retail-price"]/text())').extract_first().strip()[1:]

        data['sale_price'] = response.xpath('normalize-space(//span[@class="sale-price"]/text())').extract_first().strip()[1:]

        ################ Original Price ################
        try:
           data['sale_percent'] = 100 - int(int(data['sale_price'])/int(data['original_price'])*100)
        except:
            data['sale_percent'] = 0
        ########## Special Offer ###########################
        special_offer = response.xpath('normalize-space(//div[contains(@class, "product-detail-prices")]/span[1]/text())').extract_first()
        data['special_offer'] =[]
        if "FINAL SALE" in status:
            data['special_offer'].append('FINAL SALE')
        if "NEW" in special_offer:
            data['special_offer'].append('NEW')
        if "OFF" in special_offer:
            data['special_offer'].append('SALE')

        ########################### Brand #####################
        data['brand'] = response.xpath('normalize-space(//a[@class="product-detail-label product-detail-status"]/text())').extract_first()
        data['website_name'] = self.name
        data['website_domain'] = self.site_name
        if not data['brand']:
            data['brand'] = "Tobi"
        if not os.path.isfile('tobi.csv'):
            with open('tobi.csv', 'a', newline='', encoding= 'utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data.keys())
                writer.writeheader()

        with open('tobi.csv', 'a', newline='',  encoding= 'utf-8') as csvfile2:
                writer2 = csv.DictWriter(csvfile2, fieldnames=data.keys())
                writer2.writerow(data)

# process = CrawlerProcess(get_project_settings())
# process.crawl(Tobispider)
# process.start()
