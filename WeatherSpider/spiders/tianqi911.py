# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from WeatherSpider.items import HistoryWeatherItem


class Tianqi911Spider(scrapy.Spider):
    name = 'tianqi911'
    allowed_domains = ['tianqi.911cha.com']
    start_urls = ['https://tianqi.911cha.com/']

    city_province_map = {}
    item_recroder = {}

    def parse(self, response):
        # leve0, get all provinces
        # print response.body
        province_links = LinkExtractor(allow=r'https://(.*)\.html',
                                       restrict_xpaths='//ul[@class="tl2"][position()<4]').extract_links(response)
        for link in province_links:
            yield scrapy.Request(link.url, callback=self.parse_province)

    def parse_province(self, response):
        title = response.xpath('//title/text()').extract()[0]
        current_area = re.search(r'(.+?)天气', str(title)).group(1)
        print "parse_province: " + current_area
        cities = response.xpath(
            '//div[@class="mcon"]/ul[@class="l2 f14 tqlist"]/li/a/span[@class="tqcity"]/text()').extract()
        for city in cities:
            if city not in self.city_province_map:
                self.city_province_map[city] = current_area
        city_links = LinkExtractor(allow=r'https://(.*)',
                                   restrict_xpaths='//div[@class="mcon"]/ul[@class="l2 f14 tqlist"]').extract_links(response)
        for link in city_links:
            print 'link.url: ' + link.url
            yield scrapy.Request(link.url, callback=self.parse_overview_page)

    def parse_overview_page(self, response):
        history_links = LinkExtractor(allow=r'https://(.*)\.html',
                                      restrict_xpaths='//span[@class="choice pr"]').extract_links(response)
        for link in history_links:
            yield scrapy.Request(link.url, callback=self.parse_history_page)

    def parse_history_page(self, response):
        year_links = LinkExtractor(allow=r'https://(.*)\.html',
                                   restrict_xpaths='//div[@class="otitle"]/div/span').extract_links(response)
        for link in year_links:
            yield scrapy.Request(link.url, callback=self.parse_one_year)

    def parse_one_year(self, response):
        month_links = LinkExtractor(allow=r'https://(.*)\.html',
                                    restrict_xpaths='//div[@class="mcon f14 center"]/a').extract_links(response)
        for link in month_links:
            yield scrapy.Request(link.url, callback=self.recording_item)

    def recording_item(self, response):
        year = response.xpath('//div[@class="otitle"]/div/span/a[position()=1]/text()').extract()[0]
        month = response.xpath('//div[@class="otitle"]/div/span/a[@class="current"]/text()').extract()[0]
        title = response.xpath('//title/text()').extract()[0]
        city = re.search(r'.+?年.+?月(.*?)天气', str(title)).group(1)
        key = city + year

        print "recording_item: " + key + month

        table = response.xpath('//table').extract()[0]

        if key in self.item_recroder:
            if month in self.item_recroder[key]:
                print 'duplicate month , it should never happen! ' + key + month
            else:
                self.item_recroder[key]['content'][month] = table
        else:
            item = HistoryWeatherItem()
            item['province'] = self.city_province_map[city.decode('utf-8')].encode('utf-8')
            item['city'] = city
            item['year'] = year.encode('utf-8')
            item['content'] = {}
            item['content'][month] = table
            self.item_recroder[key] = item

        if len(self.item_recroder[key]['content']) >= 12:
            print "12get! " + key
            yield self.item_recroder.pop(key)
