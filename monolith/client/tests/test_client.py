import unittest

from pyelasticsearch import ElasticSearch

from monolith.client import Client


start, end = '2012-01-01', '2012-01-31'


class TestClient(unittest.TestCase):

    def setUp(self):
        # XXX will use a monolith instance ran by the test fixture
        self.es_client = ElasticSearch('http://127.0.0.1:9213')
        self.client = Client('http://0.0.0.0:6543')
        self.es_client.create_index('time_2012-01')
        for i in range(1, 32):
            self.es_client.index('time_2012-01', 'downloads', {
                'date': '2012-01-%.2d' % i,
                'downloads_count': i,
                'add_on': str(i % 2 + 1),
            })
        for j in range(2, 6):
            self.es_client.index('time_2012-%.2d' % j, 'downloads', {
                'date': '2012-%.2d-01' % j,
                'downloads_count': j,
                'add_on': str(j % 2),
            })
        self.es_client.refresh()

    def tearDown(self):
        try:
            self.es_client.delete_index('time_*')
        except Exception:
            pass

    def test_global_daily(self):
        hits = list(self.client('downloads_count', start, end))
        self.assertEqual(len(hits), 31)

    def test_no_fill(self):
        client = Client('http://0.0.0.0:6543', zero_fill=False)
        hits = list(client('downloads_count', '2010-01-01', '2010-01-31'))
        self.assertEqual(len(hits), 0)

        # zero fill by default
        client = Client('http://0.0.0.0:6543')
        hits = list(client('downloads_count', '2010-01-01', '2010-01-31'))
        self.assertEqual(len(hits), 31)

    def test_global_weekly(self):
        hits = list(self.client('downloads_count', start, end,
                                interval='week'))

        # between 2012-01-01 and 2012-01-31, we have 4 weeks
        self.assertEqual(len(hits), 6)

    def test_monthly(self):
        # monthly for app_id == 1
        hits = list(self.client('downloads_count', start,
                                '2012-05-01', interval='month',
                                add_on='1'))

        # we should have the 5 first months of 2012
        res = [hit['date'].month for hit in hits]
        res.sort()
        self.assertEqual(res, [1, 2, 3, 4, 5])

        hits2 = list(self.client('downloads_count', start, '2012-05-01',
                                 interval='month', add_on='2'))
        self.assertNotEqual(hits, hits2)
