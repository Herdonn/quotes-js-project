# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class QuoteItem(scrapy.Item):
    # define the fields for your item here like:
    href = scrapy.Field()
    phrase = scrapy.Field()
class SpiderItem(scrapy.Item):
    # Define the fields for your item here like:
    category = scrapy.Field()
    href = scrapy.Field()
    text = scrapy.Field()

    
