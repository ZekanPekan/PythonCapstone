import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from grid_blog_crawl.spiders.article_spider import ArticleSpider
from grid_blog_crawl.spiders.author_spider import AuthorSpider


def start_sequentially(process: CrawlerProcess, crawlers: list):
    """Starts sequential crawl of crawlers from the list"""

    logging.info('start crawler {}'.format(crawlers[0].__name__))
    deferred = process.crawl(crawlers[0])
    if len(crawlers) > 1:
        deferred.addCallback(lambda _: start_sequentially(process, crawlers[1:]))


def start():
    """Starts the blog.griddynamics scraping"""

    crawlers = [ArticleSpider, AuthorSpider]
    process = CrawlerProcess(settings=get_project_settings())
    start_sequentially(process, crawlers)
    process.start()


if __name__ == "__main__":
    start()
