# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeatherspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HistoryWeatherItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    year = scrapy.Field()
    content = scrapy.Field()
