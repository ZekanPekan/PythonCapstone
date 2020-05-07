ROOT_URL = 'https://blog.griddynamics.com'

BOT_NAME = 'grid_blog_crawl'

SPIDER_MODULES = ['grid_blog_crawl.spiders']
NEWSPIDER_MODULE = 'grid_blog_crawl.spiders'

DATABASE_NAME = "database.db"

ROBOTSTXT_OBEY = True

LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s;%(levelname)s: %(message)s'
# LOG_FILE = 'log.txt'
# LOG_STDOUT = True

ITEM_PIPELINES = {
   'grid_blog_crawl.pipelines.GridBlogSpiderPipeline': 300,
}

