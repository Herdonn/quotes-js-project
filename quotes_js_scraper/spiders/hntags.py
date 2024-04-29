# spiders/quotes.py

import scrapy
from quotes_js_scraper.items import QuoteItem
from scrapy_playwright.page import PageMethod
from bs4 import BeautifulSoup

class QuotesSpider(scrapy.Spider):
    name = 'hntags'

    def start_requests(self):
        url = "https://hackernoon.com/tagged"
        yield scrapy.Request(url, meta=dict(
                playwright = True,
                playwright_include_page = True, 
                playwright_page_methods =[
                    PageMethod('wait_for_timeout',  5000),
                    # PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    # PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
                ],
                errback=self.errback,
                ), callback = self.parse)
    async def parse_test(self, response):
        # Retrieve the Playwright page from response meta
        page = response.meta["playwright_page"]

        # Retrieve the entire HTML content of the page
        html_content = await page.content()

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Prettify the HTML content
        prettified_html = soup.prettify()

        # Save the prettified HTML content to a file
        filename = 'page.html'  # Specify the filename you want
        with open(filename, 'w') as file:
            file.write(prettified_html)

        # Close the Playwright page
        await page.close()

        # Yield the prettified HTML content as an item (or process it as needed)
        yield {'html': prettified_html}
    async def parse(self, response):
        page = response.meta["playwright_page"]
        current_page = 1  # Initialize the page counter
        max_pages = 7    # Set the maximum number of pages to crawl

        try:
            while current_page <= max_pages:  # Continue processing up to 7 pages
                # Extract and yield items
                counter = 0
                for quote in response.xpath('//li/div/a'):
                    quote_item = QuoteItem()
                    counter += 1
                    if counter > 13:
                        quote_item['href'] = "https://hackernoon.com/" + quote.xpath('./@href').get()
                        quote_item['phrase'] = quote.xpath('./text()').get().strip()
                        yield quote_item

                # Click the next page button
                next_page_selector = '.ais-Pagination-item--nextPage .ais-Pagination-link'
                next_page_element = await page.query_selector(next_page_selector)
                if next_page_element and current_page < max_pages:
                    await next_page_element.click()
                    await page.wait_for_timeout(3000)  # Wait for 3 seconds to allow the page to load

                    # Update the response object with new page content
                    html_content = await page.content()
                    response = scrapy.http.HtmlResponse(url=page.url, body=html_content, encoding='utf-8')

                    print(f"Navigated to page {current_page + 1}. Continuing to parse.")
                    current_page += 1  # Increment the page counter
                else:
                    print("Reached the maximum number of pages or no next page available.")
                    break
        finally:
            await page.close()


    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()


