# -*- coding: utf-8 -*-
import codecs
import csv

import re

from WeatherSpider.settings import FILE_SAVED_BASE_PATH
from bs4 import BeautifulSoup
import os


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class HistoryWeatherPipeline(object):
    def process_item(self, item, spider):
        province = item['province']
        city = item['city']
        year = item['year']
        content_map = item['content']

        dir_path = unicode("%s/%s/%s" % (FILE_SAVED_BASE_PATH, province, city), 'utf-8')
        file_path = dir_path + unicode("/%s%s.csv" % (year, city), 'utf-8')

        # files should be stored by /province/cities, to determine if dir is exits
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        if os.path.exists(file_path):
            print "file path error, file has already exist! -- " + str(file_path)
            return

        # write file
        print "Create file: " + file_path
        with open(file_path, 'wb') as csvf:
            csvf.write(codecs.BOM_UTF8)
            writer = csv.writer(csvf)
            # write first row data
            writer.writerow(["日期", "时间", "天气", "温度", "湿度", "风力", "风级", "降水量", "体感温度", "云量"])
            key_set = sorted(content_map.keys(), self.custom_sorted)
            for key in key_set:
                table = BeautifulSoup(content_map[key], "lxml")
                row_date = ""
                first_row = True
                for row in table.find_all('tr'):
                    if first_row:
                        first_row = False
                    else:
                        if row.th is not None:
                            row_date = row.th.a.get_text()
                        row_data = [column.get_text() for column in row.find_all('td') if column.img is None]
                        writer.writerow([row_date] + row_data)

        return item

    @staticmethod
    def custom_sorted(x, y):
        int_x = int(re.search(r'(.+)月', str(x)).group(1))
        int_y = int(re.search(r'(.+)月', str(y)).group(1))
        if int_x > int_y:
            return 1
        if int_x < int_y:
            return -1
        return 0
