from monolith.web import main
from pyelastictest import IsolatedTestCase
from webtest.http import StopableWSGIServer

from monolith.client import Client

start = '2012-01-01'
end = '2012-01-31'


class TestClient(IsolatedTestCase):

    def setUp(self):
        super(TestClient, self).setUp()
        settings = {'elasticsearch.host': self.es_cluster.urls}
        app = main({}, **settings)
        self.server = StopableWSGIServer.create(app)
        docs = []
        for i in range(1, 32):
            docs.append({
                'date': '2012-01-%.2d' % i,
                'downloads_count': i,
                'add_on': str(i % 2 + 1),
            })
        self.es_client.bulk_index('time_2012-01', 'downloads', docs)
        for j in range(2, 6):
            self.es_client.index('time_2012-%.2d' % j, 'downloads', {
                'date': '2012-%.2d-01' % j,
                'downloads_count': j,
                'add_on': str(j % 2),
            })
        self.es_client.refresh()
        self.server.wait()

    def tearDown(self):
        self.server.shutdown()
        super(TestClient, self).tearDown()

    def _make_one(self, **kw):
        return Client(self.server.application_url, **kw)

    def test_global_daily(self):
        client = self._make_one()
        hits = list(client('downloads_count', start, end))
        self.assertEqual(len(hits), 31)

    def test_no_fill(self):
        client = self._make_one(zero_fill=False)
        hits = list(client('downloads_count', '2010-01-01', '2010-01-31'))
        self.assertEqual(len(hits), 0)

        # zero fill by default
        client = self._make_one()
        hits = list(client('downloads_count', '2010-01-01', '2010-01-31'))
        self.assertEqual(len(hits), 31)

    def test_global_weekly(self):
        client = self._make_one()
        hits = list(client('downloads_count', start, end, interval='week'))

        # between 2012-01-01 and 2012-01-31, we have 4 weeks
        self.assertEqual(len(hits), 6)

    def test_monthly(self):
        client = self._make_one()
        # monthly for app_id == 1
        hits = list(client('downloads_count', start, '2012-05-01',
                           interval='month', add_on='1'))

        # we should have the 5 first months of 2012
        res = [hit['date'].month for hit in hits]
        res.sort()
        self.assertEqual(res, [1, 2, 3, 4, 5])

        hits2 = list(client('downloads_count', start, '2012-05-01',
                            interval='month', add_on='2'))
        self.assertNotEqual(hits, hits2)

    def test_global_daily_strict(self):
        client = self._make_one()
        hits = list(client('downloads_count', start, end, strict_range=True))
        self.assertEqual(len(hits), 29)

    def test_no_fill_strict(self):
        client = self._make_one(zero_fill=False)
        hits = list(client('downloads_count', '2010-01-01', '2010-01-31',
                           strict_range=True))
        self.assertEqual(len(hits), 0)

        # zero fill by default
        client = self._make_one()
        hits = list(client('downloads_count', '2010-01-01', '2010-01-31',
                           strict_range=True))
        self.assertEqual(len(hits), 29)

    def test_global_weekly_strict(self):
        client = self._make_one()
        hits = list(client('downloads_count', start, end, interval='week',
                           strict_range=True))

        # between 2012-01-01 and 2012-01-31, we have 4 weeks
        self.assertEqual(len(hits), 6)

    def test_monthly_strict(self):
        client = self._make_one()
        # monthly for app_id == 1
        hits = list(client('downloads_count', start, '2012-05-01',
                           interval='month', add_on='1', strict_range=True))

        # we should have the 5 first months of 2012
        res = [hit['date'].month for hit in hits]
        res.sort()
        self.assertEqual(res, [1, 2, 3, 4])

        hits2 = list(client('downloads_count', start, '2012-05-01',
                            interval='month', add_on='2', strict_range=True))
        self.assertNotEqual(hits, hits2)
