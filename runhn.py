import pandas as pd
import scrapy
from scrapy import CrawlerProcess

df = pd.read_csv("scrapy/quotes-js-project/test.csv")
tuple_list = list(zip(df.phrase, df.href))
for phrase, href in tuple_list:
    print(phrase, href)

process = CrawlerProcess(get_project_settings())
process.crawl(SearchSpider, topics_with_hrefs = topics_with_hrefs)
process.start() 
