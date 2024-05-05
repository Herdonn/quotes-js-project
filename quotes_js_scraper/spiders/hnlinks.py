import scrapy
from scrapy_playwright.page import PageMethod
from quotes_js_scraper.items import LinkItem
import time
import re
import queue
import logging

logger = logging.basicConfig(filename='completed_urls.log', filemode='a', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')
scrolling_script = """
(async () => {
    const scrollDelay = 1500;  // Time to wait between scrolls (ms)
    const maxScrolls = 1000;  // Maximum number of scrolls
    let lastScrollHeight = document.body.scrollHeight;  // Starting scroll height
    let scrollsDone = 0;
    
    while (scrollsDone < maxScrolls) {
        window.scrollTo(0, document.body.scrollHeight);
        scrollsDone++;
        
        // Wait for content to load after scrolling
        await new Promise(resolve => setTimeout(resolve, scrollDelay));
        
        // Check the new scroll height
        let newScrollHeight = document.body.scrollHeight;
        
        // If the scroll height hasn't changed, stop scrolling
        if (newScrollHeight === lastScrollHeight) {
            break;
        }
        
        // Update the last scroll height
        lastScrollHeight = newScrollHeight;
    }
})();
"""

class HackerNoonSpider(scrapy.Spider):
    name = 'hnlinks'
    
    def __init__(self, topics_with_hrefs = None, *args, **kwargs):
        super(HackerNoonSpider, self).__init__(*args, **kwargs)
        self.topics_with_hrefs = topics_with_hrefs if topics_with_hrefs is not None else []
        logging.getLogger('scrapy-playwright').setLevel(logging.INFO)

    def start_requests(self):
        for pair in self.topics_with_hrefs:
            yield scrapy.Request(url=pair[1], meta=dict(
                    playwright = True,
                    playwright_include_page = True, 
                    playwright_page_methods =[
                        PageMethod("evaluate", scrolling_script),
                        PageMethod('wait_for_timeout',  8000),
                        # PageMethod("wait_for_selector", "div.quote:nth-child(60)"),  # 10 per page
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
        next_url = None
        if selectors:
            for selector in selectors:
                item = LinkItem()   
                item['category'] = category
                item['href'] = "https://hackernoon.com" + selector.xpath("./@href").get()  # The URL of the page being parsed
                yield item
            logging.info(f"Completed URL: {response.url}")
            # cat_url = re.sub(r'\?.*', '', response.url)
            # match = re.search(r'(\d+)(?!.*\d)', response.url)
            # if match:
            #     current_page = int(match.group(0))
            # else:
            #     current_page = 1
            # # Calculate the next page
            # next_page = current_page + 1
            # next_url = cat_url + "?page=" + str(next_page)
            # print(f"Queueing next page: {next_url}")
            # yield scrapy.Request(next_url, meta=response.meta, callback=self.parse) 

            await page.close()
            with open("finished.txt", "a") as file:
                file.write(response.url)
    async def errback(self, failure):
        # Check if the page object is available in the meta and close it.
        logging.error(f"Failed to process page: {failure.request.url}")
        page = failure.request.meta.get('playwright_page')
        if page:
            await page.close()

