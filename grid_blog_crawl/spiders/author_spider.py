import scrapy
from scrapy.loader import ItemLoader
from ..items import AuthorItem


class AuthorSpider(scrapy.Spider):
    """Spider that scrapes author child pages"""

    name = "author_spider"

    def parse(self, response):
        """Yields Author item extracted from author child page"""

        self.logger.info('parsing author {} page'.format(response.url))
        selector = response.css('.authorcard.popup')
        author_loader = ItemLoader(item=AuthorItem(), selector=selector)

        author_loader.add_css('name', 'h3::text')
        author_loader.add_css('job_title', '.jobtitle::text')
        author_loader.add_css('linkedin_url', '.linkedin::attr(href)')
        author_loader.add_value('articles_count',
                                len(selector.css('.postsrow > .row > a::attr(href)')))
        author_loader.add_value("url", response.url)

        item = author_loader.load_item()

        yield item

