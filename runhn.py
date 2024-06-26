import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import queue
import re
from quotes_js_scraper.spiders.hnlinks import HackerNoonSpider 
from quotes_js_scraper.spiders.hntext import HNTextSpider
def run_spider(filepath, spider = HackerNoonSpider):
    df = pd.read_csv(filepath)

    # df.href = df.href + "?page=10"
    tuple_list = list(zip(df.phrase, df.href))
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider, topics_with_hrefs = tuple_list)
    process.start() 
# run_spider("categories.csv", HackerNoonSpider)
run_spider("links.csv", HNTextSpider)