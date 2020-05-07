import pandas as pd
import sqlalchemy
import numpy as np
import logging
from matplotlib import pyplot as plt
from scrape import start
from models import DatabaseController, Author, AuthorArticleRelation, Article
from grid_blog_crawl.settings import DATABASE_NAME

log = logging.getLogger("Report Generator")


def top_5_articles(dbc: DatabaseController):
    """:returns str containing a table with 5 newest articles"""

    log.info("Generating top 5 articles report")
    session = dbc.get_session()
    df = pd.read_sql_query(session.query(Article.title, Article.pub_date, Article.tags, Article.url,
                                         Author.name.label("authors"))
                           .join(AuthorArticleRelation, AuthorArticleRelation.article_url == Article.url)
                           .join(Author, Author.url == AuthorArticleRelation.author_url)
                           .statement, session.bind)

    df = df.groupby(['url', 'title', 'pub_date', 'tags'])['authors']\
        .apply(', '.join).reset_index().sort_values('pub_date', ascending=False).head(5)

    df.tags = df.tags.map(lambda x: x.replace(":::", ", "))
    return df


def get_top_7_tags(dbc: DatabaseController):
    """:returns a df showing top 7 most popular tags"""
    session = dbc.get_session()
    df = pd.read_sql_query(session.query(Article).statement, session.bind)
    df = df[df.tags.notnull()]
    df['tags'] = df['tags'].apply(lambda x: x.strip())
    new_df = pd.DataFrame(df.tags.str.split(':::').tolist(), df.title).stack().reset_index(name="tag")
    new_df = new_df.drop('title', axis=1)
    new_df = new_df.groupby(['tag'])["level_1"].count().reset_index(name="counts")
    new_df = new_df.sort_values('counts', ascending=False)
    return new_df.head(7)


def create_top_7_tags_plot(dbc: DatabaseController):
    """Creates a bar plot showing top 7 most popular tags"""

    log.info("Generating top 7 tags plot")
    top_tags = get_top_7_tags(dbc)
    plt.title("Popular tags")
    xrange = range(len(top_tags))
    plt.xticks(xrange, top_tags.tag, rotation='vertical')
    plt.bar(xrange, top_tags.counts, edgecolor="black", color='red')
    plt.tight_layout()


def get_top_5_authors(dbc: DatabaseController):
    """:returns a df comparison of the article counters of top 5 authors"""
    session = dbc.get_session()
    df_s = pd.read_sql_query(session.query(Author.name, Author.articles_count,
                                           sqlalchemy.func.count(AuthorArticleRelation.article_url)
                                           .label("article_relation_table_count"))
                             .group_by(Author.name)
                             .join(Author, AuthorArticleRelation.author_url == Author.url)
                             .statement
                             , session.bind)
    top5 = df_s.sort_values('articles_count', ascending=False).head(5)
    return top5


def create_top_5_authors_plot(dbc: DatabaseController):
    """Creates a bar comparison of the article counters and returns a table with top 5 authors"""

    log.info("Generating top 5 authors plot & report")

    top5 = get_top_5_authors(dbc)
    fig, ax1 = plt.subplots()
    plt.title("Top 5 Authors")
    plt.ylabel("num. of articles")
    y_range = range(max(top5.articles_count.max(), top5.article_relation_table_count.max()) + 2)
    row_range = np.arange(len(top5))
    plt.xticks(row_range, top5.name, rotation='vertical')

    width = 0.3
    ac_list = ax1.bar(row_range, top5.articles_count, edgecolor="black", width=width, color='b', align='center')
    ax2 = ax1.twinx()
    ac_rel = ax2.bar(row_range + width, top5.article_relation_table_count, edgecolor="black", width=width,
                     color='orange', align='center')
    plt.legend([ac_list, ac_rel],
               ["According to author specific page blog listings", "According to blog specific page"])
    ax1.set_yticks(y_range)
    ax2.set_yticks(y_range)
    plt.tight_layout()
    return top5


def run():
    start()
    dbc = DatabaseController(DATABASE_NAME)
    create_top_7_tags_plot(dbc)
    plt.figure(1)
    print(create_top_5_authors_plot(dbc).to_string(index=False))
    # print(top_5_articles(dbc).to_string(index=False))
    df = top_5_articles(dbc)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'max_colwidth', 200):
        print(df)

    plt.show()


if __name__ == "__main__":
    run()


