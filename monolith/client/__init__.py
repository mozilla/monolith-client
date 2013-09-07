import requests
import datetime
import json
from time import strptime

from statsd import StatsClient

from monolith.client import util


DAY = 1
WEEK = 2
MONTH = 3
YEAR = 4

_interval2str = {DAY: 'day',
                 WEEK: 'week',
                 MONTH: 'month',
                 YEAR: 'year'}

_str2interval = {'day': DAY,
                 'week': WEEK,
                 'month': MONTH,
                 'year': YEAR}


def _iso2date(data):
    data = data.split('T')[0]
    data = strptime(data, "%Y-%m-%d")
    return datetime.date(data.tm_year, data.tm_mon, data.tm_mday)


class Client(object):

    def __init__(self, server, zero_fill=True, **kw):
        self.server = server.rstrip('/')
        self.session = requests.session()
        # getting monolith info
        info = self.session.get(server).json
        if callable(info):
            info = info()

        self.es = self.server + info['es_endpoint']
        self.fields = info['fields']
        self.zero_fill = zero_fill

        # statsd settings
        statsd_host = kw.get('statsd.host', 'localhost')
        statsd_port = int(kw.get('statsd.port', 8125))
        statsd_prefix = kw.get('statsd.prefix', 'monolith.client')
        self.statsd = StatsClient(host=statsd_host, port=statsd_port,
                                  prefix=statsd_prefix)

    def __call__(self, field, start, end, interval=DAY, strict_range=False,
                 **terms):

        if isinstance(interval, basestring):
            interval = _str2interval[interval.encode()]

        if isinstance(start, basestring):
            start = datetime.datetime.strptime(start.encode(),
                                               '%Y-%m-%d').toordinal()
            start = datetime.date.fromordinal(start)
        elif isinstance(start, datetime.datetime):
            start = start.date()

        if isinstance(end, basestring):
            end = datetime.datetime.strptime(end.encode(),
                                             '%Y-%m-%d').toordinal()
            end = datetime.date.fromordinal(end)
        elif isinstance(end, datetime.datetime):
            end = end.date()

        if interval == DAY:
            drange = util.iterdays(start, end)
        elif interval == WEEK:
            drange = util.iterweeks(start, end)
        elif interval == MONTH:
            drange = util.itermonths(start, end)
        else:
            drange = util.iteryears(start, end)

        # building the query
        start_date_str = start.strftime('%Y-%m-%d')
        end_date_str = end.strftime('%Y-%m-%d')

        if isinstance(interval, int):
            interval = _interval2str[interval]

        # XXX we'll see later if we want to provide a
        # nicer query interface

        # we need a facet query
        if strict_range:
            greater = "gt"
            lower = "lt"
        else:
            greater = "gte"
            lower = "lte"

        query = {
            "query": {
                "match_all": {},
            },
            "size": 0,  # we aren't interested in the hits
            "facets": {
                "histo1": {
                    "date_histogram": {
                        "value_field": field,
                        "interval": interval,
                        "key_field": "date",
                    },
                    "facet_filter": {
                        "range": {
                            "date": {
                                greater: start_date_str,
                                lower: end_date_str,
                            }
                        }
                    }
                }
            }
        }

        if terms:

            range_ = query['facets']['histo1']['facet_filter']['range']

            query['facets']['histo1']['facet_filter'] = {
                'and': ([{'term': {k: v}} for k, v in terms.items()] +
                        [{'range': range_}])}

        with self.statsd.timer('elasticsearch-query'):
            res = self.session.post(self.es, data=json.dumps(query))
            if res.status_code != 200:
                raise ValueError(res.content)

            # getting the JSON content
            res = res.json
            if callable(res):
                res = res()

        # statsd calls
        self.statsd.incr('elasticsearch-call')

        if not isinstance(res, dict):
            raise ValueError(res)

        if 'errors' in res:
            raise ValueError(res['errors'][0]['description'])

        counts = {}

        for entry in res['facets']['histo1']['entries']:
            time_ = entry['time'] / 1000.0
            date_ = datetime.datetime.utcfromtimestamp(time_).date()
            if 'total' in entry:
                count = entry['total']
            else:
                count = entry['count']
            counts[date_] = count

        for date_ in drange:
            if strict_range and date_ in (start, end):
                continue

            if date_ in counts:
                yield {'count': counts[date_], 'date': date_}
            elif self.zero_fill:
                yield {'count': None, 'date': date_}


def main():
    raise NotImplementedError("add a CLI here")


if __name__ == '__main__':
    main()
