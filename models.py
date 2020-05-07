import logging
import os
import sqlalchemy as db
from sqlalchemy import create_engine, desc, distinct, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Author(Base):
    """Author db model, consisting all the information to describe an author"""

    __tablename__ = "authors"
    url = db.Column(db.String(160), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(160))
    articles_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Author(url = {}, name = {}, job_title = {}, linkedin_url = {}, articles_count = {})>" \
            .format(self.url, self.name, self.job_title, self.linkedin_url, self.articles_count)

    def __str__(self):
        return "Author\nname = {}\nurl = {}\narticles_count = {}" \
            .format(self.name, self.url, self.articles_count)


class Article(Base):
    """Article db model, consisting all the information to describe an article"""

    __tablename__ = "articles"
    url = db.Column(db.String(160), primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    pub_date = db.Column(db.Date, nullable=False)
    text = db.Column(db.String(160), nullable=False)
    tags = db.Column(db.String(200))

    def __repr__(self):
        return "<Article(title = {}, url = {}, pub_date = {}, text = {}, tags = {})>" \
            .format(self.title, self.url, self.pub_date, self.text, self.tags)

    def __str__(self):
        return "Article\ntitle={}\nurl={}" \
            .format(self.title, self.url)


class AuthorArticleRelation(Base):
    """DB model, consisting all the information to describe a relation between author and article"""

    __tablename__ = "author_article"
    author_url = db.Column(db.String(160), primary_key=True)
    article_url = db.Column(db.String(160), primary_key=True)

    def __repr__(self):
        return "<AuthorArticleRelation(article_url = {}, author_url = {})>" \
            .format(self.article_url, self.author_url)


class DatabaseController:
    """Entry point to the database"""

    logger = logging.getLogger("Database Controller")

    def __init__(self, _database_name):
        self.URI = "sqlite:///{0}/{1}".format(os.path.dirname(os.path.abspath(__file__)), _database_name)
        self.engine = create_engine(self.URI)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """:return a database session"""
        return self.Session()

    def get_not_scraped_authors(self):
        """:returns a list of authors that are not scraped"""

        self.logger.info("Fetching not scraped authors from database")
        session = self.get_session()
        db_authors = session.query(distinct(AuthorArticleRelation.author_url))\
            .filter(~AuthorArticleRelation.author_url.in_(session.query(Author.url)))
        return list(map(lambda x: x[0], db_authors))

    def increment_author_counter_if_exist(self, author_url):
        """increments author article counter if the author exists"""

        session = self.get_session()
        author = session.query(Author).filter(Author.url == author_url).first()
        if author is not None:
            author.articles_count += 1
            session.commit()

    def compare_article_counts(self):
        """:returns a table with comparison of author article count between author page and blog pages information"""

        session = self.get_session()
        grouped = session.query(AuthorArticleRelation.author_url, Author.articles_count,
                                func.count(AuthorArticleRelation.article_url))\
            .group_by(AuthorArticleRelation.author_url).join(Author, AuthorArticleRelation.author_url == Author.url)
        return grouped

    def get_author(self, author_url):
        """:return an author with the given url"""

        return self.get_session().query(Author).filter(Author.url == author_url).first()

    def get_articles(self):
        """:returns all articles"""

        session = self.get_session()
        return session.query(Article)

    def get_article_author(self):
        """:returns all author article relations """

        session = self.get_session()
        return session.query(AuthorArticleRelation)

    def get_authors(self):
        """:returns all authors"""

        session = self.get_session()
        return session.query(Author)

    def add(self, *args):
        """Inserts into db"""

        session = self.get_session()
        for model in args:
            session.add(model)
        session.commit()

    def get_last_blog_date(self):
        """:returns the date of the newest blog in the database"""

        last_date = self.get_session().query(Article.pub_date).order_by(desc(Article.pub_date)).first()
        if last_date is not None:
            last_date = last_date[0]
        return last_date
