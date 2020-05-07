import scrapy
from datetime import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from .settings import ROOT_URL


def extract_date(date_extracted):
    """Extracts date from str in format that is consistent on blog.griddynamics"""

    return datetime.strptime(date_extracted.strip(), "%b %d, %Y •").date()


def relative_to_absolute_url(relative):
    """Converts author/article relative url to absolute url"""

    return ROOT_URL + relative


def shorten(string):
    """Takes first 160 characters from str"""

    return string[:160]


def normalise(string):
    """Strips the str"""

    return string.strip()


class MapComposeWithTakeFirst(MapCompose):
    """Processor that operates as MapCompose but Takes First from the result"""

    def __init__(self, *functions, **default_loader_context):
        super().__init__(*functions, **default_loader_context)

    def __call__(self,  value, loader_context=None):
        return super().__call__(value, loader_context)[0]


class TextInputNormaliser:
    """Processor that joins and normalises list of strings"""

    def __call__(self, values):
        return ''.join(map(lambda x: x.strip(), values))[:160]


class ArticleItem(scrapy.Item):
    """scrapy.Item consisting all the fields to describe an article"""

    title = scrapy.Field(
        output_processor=TakeFirst()
    )
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    pub_date = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=MapComposeWithTakeFirst(extract_date)
    )
    text = scrapy.Field(
        input_processor=TextInputNormaliser(),
        output_processor=TakeFirst()
    )
    tags = scrapy.Field(
        input_processor=Join(':::'),
        output_processor=TakeFirst()
    )


class ArticleAuthorItem(scrapy.Item):
    """scrapy.Item consisting all the fields to describe a relation between author and article"""

    article_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    authors = scrapy.Field(
        output_processor=MapCompose(relative_to_absolute_url)
    )


class AuthorItem(scrapy.Item):
    """scrapy.Item consisting all the fields to describe an author"""
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    name = scrapy.Field(
        output_processor=TakeFirst()
    )
    job_title = scrapy.Field(
        output_processor=TakeFirst()
    )
    linkedin_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    articles_count = scrapy.Field(
        output_processor=TakeFirst()
    )

