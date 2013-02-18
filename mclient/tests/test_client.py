import unittest
from mclient import Client


start, end = '2012-01-01', '2012-01-31'


class TestClient(unittest.TestCase):

    def setUp(self):
        # XXX will use an ES instance ran by the test fixture
        self.client = Client('http://0.0.0.0:6543')

    def test_global_daily(self):
        hits = list(self.client('downloads_count', start, end))
        self.assertEqual(len(hits), 30)

    def test_global_weekly(self):
        hits = list(self.client('downloads_count', start, end,
                                interval='week'))
        self.assertEqual(len(hits), 6)

    def test_monthly(self):

        # monthly for app_id == 1
        hits = list(self.client('downloads_count', start,
                                '2012-05-01', interval='month',
                                add_on='1'))
        self.assertEqual(len(hits), 4)

        hits2 = list(self.client('downloads_count', start, '2012-05-01',
                                 interval='month', add_on='2'))
        self.assertNotEqual(hits, hits2)
