# -*- coding: utf-8 -*-

import csv
import httplib
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import datetime
import codecs
import sys
import os
import logging

logging.basicConfig()

reload(sys)
sys.setdefaultencoding('UTF-8')


def init_result_file(result_file):
    if os.path.exists(result_file_path) and os.path.isfile(result_file_path):
        return
    with open(result_file, 'wb') as f:
        f.write(codecs.BOM_UTF8)
        writer = csv.writer(f)
        writer.writerow(["经度", "纬度", "硬件经度", "硬件纬度", "天气概况", "温度", "pm25值", "云量", "相对湿度", "降水强度", "风力", "风向", "时间"])


def get_config(config_file_path):
    with open(config_file_path, 'r') as f:
        config_dict = json.load(f)
    return config_dict


def request_data(config_dict):
    conn = httplib.HTTPSConnection("api.caiyunapp.com")
    result_list = []
    for location in config_dict['locations']:
        url = "/v2/Y2FpeXVuIGFuZHJpb2QgYXBp/%s,%s/realtime.json" % (location[1][0], location[1][1])
        print "url: " + url
        conn.request("GET", url)
        response = conn.getresponse()
        if response.status == 200:
            result = json.loads(response.read())
            origin_location = location[0]
            result_list.append((origin_location, result))
    return result_list


def write_file(r_list, file_path):
    with open(file_path, 'ab') as f:
        writer = csv.writer(f)
        count = 0
        for origin_location, result in r_list:
            if result['result']['status'] == "ok":
                count += 1
                if result['result']['precipitation']['local']['status'] == 'ok':
                    precipitation = result['result']['precipitation']['local']['intensity']
                else:
                    precipitation = -1
                skycon = result['result']['skycon']
                if skycon in config['weather_mapping']:
                    skycon = config['weather_mapping'][skycon]
                current_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                # ["经度", "纬度", "硬件经度", "硬件纬度", "天气概况", "温度", "pm25值", "云量", "相对湿度", "降水强度", "风速", "风向", "时间"]
                row_data = origin_location + [result['location'][1], result['location'][0], skycon,
                                              result['result']['temperature'],
                                              result['result']['pm25'], result['result']['cloudrate'],
                                              result['result']['humidity'], precipitation,
                                              result['result']['wind']['speed'], result['result']['wind']['direction'],
                                              current_time]
                writer.writerow(row_data)
        print "Finish to update, insert %d records" % count


def update_weather():
    print "current time: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    result_list = request_data(config)
    write_file(result_list, result_file_path)


if __name__ == '__main__':
    result_file_path = 'data.csv'
    config_file_path = 'config.json'

    init_result_file(result_file_path)
    config = get_config(config_file_path)
    update_time_cycle = config['time_delay']

    scheduler = BlockingScheduler()
    scheduler.add_job(update_weather, 'interval', seconds=update_time_cycle)
    print "Main thread start!"
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print "Exit!"
