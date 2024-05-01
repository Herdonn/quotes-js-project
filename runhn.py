import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import queue
import re
from quotes_js_scraper.spiders.hnlinks import HackerNoonSpider 
df = pd.read_csv("test.csv")
tuple_list = list(zip(df.phrase, df.href))
tuple_list = tuple_list[:2]
process = CrawlerProcess(get_project_settings())

process.crawl(HackerNoonSpider, topics_with_hrefs = tuple_list)
process.start() 
