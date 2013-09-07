import datetime

import mock
from monolith.web import main
from pyelastictest import IsolatedTestCase
from webtest.http import StopableWSGIServer

from monolith.client import Client


START = '2012-01-01'
END = '2012-01-31'


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
                'add_on': str(j % 2 + 1),
                'is_something': True,
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
        hits = list(client('downloads_count', START, END))
        self.assertEqual(len(hits), 31)

    def test_no_fill(self):
        client = self._make_one(zero_fill=False)
        hits = list(client('downloads_count', '2010-01-01', '2010-01-31'))
        self.assertEqual(len(hits), 0)

        # zero fill by default
        client = self._make_one()
        hits = list(client('downloads_count', '2010-01-01', '2010-01-31'))
        self.assertEqual(len(hits), 31)
        self.assertEqual(hits[0]['count'], None)

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

    def test_global_weekly(self):
        client = self._make_one()
        hits = list(client('downloads_count', START, END, interval='week'))

        # Between 2012-01-01 and 2012-01-31, we have 5 weeks starting on
        # Monday.
        self.assertEqual(len(hits), 5)

    def test_monthly(self):
        client = self._make_one()
        # monthly for app_id == 1
        hits = list(client('downloads_count', START, '2012-05-01',
                           interval='month', add_on='1'))

        # we should have the 5 first months of 2012
        res = [hit['date'].month for hit in hits]
        res.sort()
        self.assertEqual(res, [1, 2, 3, 4, 5])

        hits2 = list(client('downloads_count', START, '2012-05-01',
                            interval='month', add_on='2'))
        self.assertNotEqual(hits, hits2)

    def test_multiple_terms(self):
        client = self._make_one()
        hits = list(client('downloads_count', START, '2012-05-01',
                           interval='month', add_on=1, is_something=True))
        self.assertEqual(len(hits), 5)
        self.assertEqual(len([h for h in hits if h['count']]), 2)

    def test_global_daily_strict(self):
        client = self._make_one()
        hits = list(client('downloads_count', START, END, strict_range=True))
        self.assertEqual(len(hits), 29)

    def test_global_weekly_strict(self):
        client = self._make_one()
        hits = list(client('downloads_count', START, END, interval='week',
                           strict_range=True))

        # Between 2012-01-01 and 2012-01-31, we have 5 weeks starting on
        # Monday.
        self.assertEqual(len(hits), 5)

    def test_monthly_strict(self):
        client = self._make_one()
        # monthly for app_id == 1
        hits = list(client('downloads_count', START, '2012-05-01',
                           interval='month', add_on='1', strict_range=True))

        # we should have the 5 first months of 2012, minus Jan and May.
        res = [hit['date'].month for hit in hits]
        res.sort()
        self.assertEqual(res, [2, 3, 4])

        hits2 = list(client('downloads_count', START, '2012-05-01',
                            interval='month', add_on='2', strict_range=True))
        self.assertNotEqual(hits, hits2)

    def test_bug864975(self):
        # see https://bugzilla.mozilla.org/show_bug.cgi?id=864975
        # Tests that no extra date range is not filtered out.

        # Populate ES with some data we want to query.
        docs = []
        for day in range(1, 5):
            docs.append({
                'date': '2013-04-%.2d' % day,
                'visits': 100,
            })
        self.es_client.bulk_index('time_2013-04', 'visits', docs)

        # ... And some we don't want to appear in the results.
        for month in ('04', '01'):
            self.es_client.index('time_2013-04', 'visits', {
                'date': '2013-01-%s' % month,
                'visits': 0,
            })

        self.es_client.refresh()
        self.server.wait()

        client = self._make_one()
        hits = list(client('visits', '2013-04-01', '2013-04-05', 'day'))
        self.assertEquals(len(hits), 5)

    def test_unicode_intervals(self):
        client = self._make_one()
        hits = list(client('downloads_count', START, END, interval=u'day'))
        self.assertEqual(len(hits), 31)

    @mock.patch('monolith.client.util.iterweeks')
    def test_datetime_ranges(self, _mock):
        "Test datetime ranges get converted to dates."
        client = self._make_one()
        start = datetime.datetime(2012, 1, 1, 12, 34, 56)
        end = datetime.datetime(2012, 1, 31, 12, 34, 56)
        list(client('downloads_count', start, end, interval='week'))
        self.assertEqual(_mock.call_args[0][0], datetime.date(2012, 1, 1))
        assert not isinstance(_mock.call_args[0][0], datetime.datetime)
        self.assertEqual(_mock.call_args[0][1], datetime.date(2012, 1, 31))
        assert not isinstance(_mock.call_args[0][1], datetime.datetime)

    def test_date_order(self):
        # Ensure fill doesn't change date ordering.
        client = self._make_one()
        prev_date = datetime.date(2000, 1, 1)

        # Addon 1 doesn't have downloads for every month and the client will
        # fill zeroes for the missing dates.
        hits = list(client('downloads_count', START, '2012-05-01',
                           interval='month', add_on='1'))
        for hit in hits:
            d = hit['date']
            assert prev_date < d
            prev_date = d
