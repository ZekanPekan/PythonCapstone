import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem, ArticleAuthorItem, extract_date


class ArticleSpiderOLD(scrapy.Spider):
    """Spider for the old format of the site"""
    name = 'article_spider_old'
    last_date = None

    def _gen_requests_regular_cp(self, response):
        regular_articles = response.css('article.regular > figure')
        requests = []
        for regular_article in regular_articles:
            url = regular_article.css('a.img::attr(href)').extract_first()
            if self.last_date is not None:
                date_formatted = extract_date(regular_article.css('.authwrp span:not([class])::text').extract_first())
                if self.last_date >= date_formatted:
                    continue
            requests.append(scrapy.Request(url=self.root_url + url, callback=self.parse_article_child_page))
        return requests

    def parse(self, response):
        for request in self._gen_requests_regular_cp(response):
            yield request

        article_series = response.css('article.series > figure > a.img::attr(href)').extract()
        for url in article_series:
            yield scrapy.Request(url=self.root_url+url, callback=self.parse_article_multi_record_page)

    def parse_article_multi_record_page(self, response):
        for request in self._gen_requests_regular_cp(response):
            yield request

    def parse_article_child_page(self, response):
        selector = response.css('article #postcontent')
        article_loader = ItemLoader(item=ArticleItem(), selector=selector)

        article_loader.add_value('url', response.url)
        article_loader.add_css('title', 'h1::text')
        article_loader.add_css('pub_date', 'meta[itemprop=datePublished]::attr(content)')
        article_loader.add_css('text', '#mypost *::text')
        article_loader.add_css('tags', 'article #postcontent a.tag.secondary::text')
        article_item = article_loader.load_item()

        article_author_loader = ItemLoader(item=ArticleAuthorItem(), selector=selector)
        article_author_loader.add_css('authors', 'span[itemprop=author] a.goauthor::attr(href)')
        article_author_loader.add_value('article_url', article_item['url'])
        article_author_item = article_author_loader.load_item()

        yield article_item
        yield article_author_item


class ArticleSpider(scrapy.Spider):
    """Spider that scrapes articles from blog.griddynamics"""

    name = 'article_spider'
    root_url = ""
    last_date = None

    def _gen_requests(self, response):
        """Generates requests for article child page from multi record page"""

        requests = []
        self._gen_request_regular_cards(response, requests)
        self._gen_request_featured_cards(response, requests)
        return requests

    def parse(self, response):
        """Yields requests for every article multi record page found on blog home page"""

        self.logger.info('Parsing home page {}'.format(response.url))
        article_series = response.css('.card.viewall::attr(href)').extract()
        for url in article_series:
            yield scrapy.Request(url=self.root_url+url, callback=self.parse_article_multi_record_page)

    def parse_article_multi_record_page(self, response):
        """Yields requests for child page of every article found on the article multi record page"""

        self.logger.info('Parsing multi-record article  page {}'.format(response.url))
        for request in self._gen_requests(response):
            yield request

    def parse_article_child_page(self, response):
        """Extracts and yields article item & author-article relation item from article child page"""

        self.logger.info('Parsing article child page {}'.format(response.url))
        article_loader = ItemLoader(item=ArticleItem(), response=response)

        article_loader.add_value('url', response.url)
        article_loader.add_css('title', '#woe #hero h2::text')
        article_loader.add_css('pub_date', '#woe #hero .authwrp .sdate::text')
        article_loader.add_css('text', '#woe .postbody *::text')
        article_loader.add_css('tags', "head meta[property='article:tag'] ::attr(content)")
        article_item = article_loader.load_item()

        article_author_loader = ItemLoader(item=ArticleAuthorItem(), response=response)
        article_author_loader.add_css('authors', '.goauthor::attr(href)')
        article_author_loader.add_value('article_url', article_item['url'])
        article_author_item = article_author_loader.load_item()

        yield article_item
        yield article_author_item

    def _gen_req_form_card(self, cards, requests):

        """Append request to requests list for child page of every article found in the article cards"""
        for card in cards:
            url = card.css('::attr(href)').extract_first()
            if self.last_date is not None:
                date_formatted = extract_date("".join(card.css('span.name::text').extract()))
                if self.last_date >= date_formatted:
                    continue
            requests.append(scrapy.Request(url=self.root_url + url, callback=self.parse_article_child_page))

    def _gen_request_regular_cards(self, response, requests):

        """Append request to requests list for child page of every regular article found in the response"""
        regular_cards = response.css('a.card.cardtocheck')
        self._gen_req_form_card(regular_cards, requests)

    def _gen_request_featured_cards(self, response, requests):

        """Append request to requests list for child page of every featured article found in the response"""
        featured_cards = response.css('.card.featured')
        self._gen_req_form_card(featured_cards, requests)



