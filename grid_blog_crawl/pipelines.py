from models import DatabaseController, Author, Article, AuthorArticleRelation
from .items import ArticleAuthorItem, ArticleItem
from .spiders.article_spider import ArticleSpider
from .spiders.author_spider import AuthorSpider


class GridBlogSpiderPipeline(object):

    def __init__(self, db_name, root_url):
        self.db_controller = DatabaseController(db_name)
        self.root_url = root_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_name=crawler.settings.get('DATABASE_NAME'),
            root_url=crawler.settings.get('ROOT_URL')
        )

    def open_spider(self, spider):
        if spider.name == AuthorSpider.name:
            spider.start_urls = self.db_controller.get_not_scraped_authors()
        elif spider.name == ArticleSpider.name:
            spider.root_url = self.root_url
            spider.start_urls = [self.root_url]
            spider.last_date = self.db_controller.get_last_blog_date()

    def process_item(self, item, spider):
        if spider.name == AuthorSpider.name:
            author = Author(**item)
            self.db_controller.add(author)
        elif spider.name == ArticleSpider.name:
            if isinstance(item, ArticleItem):
                article = Article(**item)
                self.db_controller.add(article)
            elif isinstance(item, ArticleAuthorItem):
                for author_url in item['authors']:
                    self.db_controller.increment_author_counter_if_exist(author_url)
                    self.db_controller.add(
                        AuthorArticleRelation(author_url=author_url, article_url=item['article_url'])
                    )

        return item
