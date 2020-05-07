import unittest

from models import DatabaseController
from report import top_5_articles, get_top_5_authors, get_top_7_tags


class ReportTests(unittest.TestCase):

    def setUp(self):
        self.dbc = DatabaseController("test_data.db")

    def test_top_5_articles(self):
        expected = ['Launch new digital services faster with distributed teams and agile co-creation delivery model',
                    'Customer2Vec: Representation learning for customer analytics and personalization',
                    'Boosting product discovery with semantic search',
                    'Smart autocomplete for Replacements.com drives revenue',
                    'Tiered machine learned ranking improves relevance for the retail search']

        self.assertEqual(top_5_articles(self.dbc).title.tolist(), expected)

    def test_top_5_authors(self):
        expected = ['Eugene Steinberg',
                    'Victoria Livschitz',
                    'Max Martynov',
                    'Ilya Katsov',
                    'Joseph Gorelik']
        self.assertEqual(get_top_5_authors(self.dbc).name.tolist(), expected)

    def test_top_7_tags(self):
        expected = ['E-commerce',
                    'Machine Learning and Artificial Intelligence',
                    'Data Science',
                    'Search',
                    'Big Data',
                    'Mobile',
                    'Data science toolkit']
        self.assertEqual(get_top_7_tags(self.dbc).tag.tolist(), expected)


if __name__ == '__main__':
    unittest.main()
