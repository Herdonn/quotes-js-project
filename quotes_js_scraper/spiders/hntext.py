import scrapy
from scrapy_playwright.page import PageMethod
from quotes_js_scraper.items import TextItem
import time
import re
import queue
import logging
class HNTextSpider(scrapy.Spider):
    name = 'hntext'
    
    def __init__(self, topics_with_hrefs = None, *args, **kwargs):
        super(HNTextSpider, self).__init__(*args, **kwargs)
        self.topics_with_hrefs = topics_with_hrefs if topics_with_hrefs is not None else []
    def start_requests(self):
        for pair in self.topics_with_hrefs:
            yield scrapy.Request(url=pair[1], meta=dict(
                    playwright = True,
                    playwright_include_page = True, 
                    playwright_page_methods =[
                        PageMethod('wait_for_timeout',  3000),
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
        category = response.meta['phrase']
        page_content = response.xpath("//p/text() | //h1/text() | //h2/text() | //h3/text()").getall()
        page_joined = " ".join(page_content)
        item = TextItem()
        item['category'] = category
        item['href'] = response.url
        item['text'] = page_joined
        yield item
        await page.close()
    async def errback(self, failure):
        # Check if the page object is available in the meta and close it.
        page = failure.request.meta.get('playwright_page')
        if page:
            await page.close()

