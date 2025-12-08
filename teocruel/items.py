# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TeocruelItem(scrapy.Item):
    # 定义爬虫项目的字段
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    status = scrapy.Field()
    depth = scrapy.Field()
