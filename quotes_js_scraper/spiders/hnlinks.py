import scrapy
from scrapy_playwright.page import PageMethod
from quotes_js_scraper.items import LinkItem
import time
import re
import queue
import logging

logging.basicConfig(filename='completed_urls.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
class HackerNoonSpider(scrapy.Spider):
    name = 'hnlinks'
    
    def __init__(self, topics_with_hrefs = None, *args, **kwargs):
        super(HackerNoonSpider, self).__init__(*args, **kwargs)
        self.topics_with_hrefs = topics_with_hrefs if topics_with_hrefs is not None else []
    def start_requests(self):
        for pair in self.topics_with_hrefs:
            yield scrapy.Request(url=pair[1], meta=dict(
                    playwright = True,
                    playwright_include_page = True, 
                    playwright_page_methods =[
                        PageMethod('wait_for_timeout',  8000),
                        # PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                        # PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
                    ],
                    errback=self.errback,
                    phrase = pair[0],
                    ), callback = self.parse)
    async def parse(self, response):
        if 'playwright_page' not in response.meta:
            logging.error("Playwright page not available in response.meta")
            return
        page = response.meta['playwright_page']
        await page.wait_for_timeout(3000)  # Wait for 3 seconds
        selectors = response.xpath("//article/div/h2/a")
        category = response.meta['phrase']
        if selectors:
            for selector in selectors:
                item = LinkItem()   
                item['category'] = category
                item['href'] = "https://hackernoon.com" + selector.xpath("./@href").get()  # The URL of the page being parsed
                yield item
            logging.info(f"Completed URL: {response.url}")
            cat_url = re.sub(r'\?.*', '', response.url)
            last_char = response.url[-1]
            if(last_char.isdigit()):
                current_page = int((str(response.url))[-1])
            else:
                current_page = 1
            next_page = current_page + 1
            next_url = cat_url + "?page=" + str(next_page)
            print(f"Queueing next page: {next_url}")
            yield scrapy.Request(next_url, meta=response.meta, callback=self.parse) 
        elif not selectors and next_url is None:
            await page.close()
    async def errback(self, failure):
        # Check if the page object is available in the meta and close it.
        logging.error(f"Failed to process page: {failure.request.url}")
        page = failure.request.meta.get('playwright_page')
        if page:
            await page.close()

