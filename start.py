# -*- coding: utf-8 -*-

import sys
from scrapy import cmdline

reload(sys)
sys.setdefaultencoding('UTF-8')
cmdline.execute("scrapy crawl tianqi911".split())