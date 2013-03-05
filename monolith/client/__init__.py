import requests
import datetime
import json
from time import strptime


DAY = 1
WEEK = 2
MONTH = 3
YEAR = 4

_interval2str = {DAY: 'day',
                 WEEK: 'week',
                 MONTH: 'month',
                 YEAR: 'year'}


def _iso2date(data):
    data = data.split('T')[0]
    data = strptime(data, "%Y-%m-%d")
    return datetime.date(data.tm_year, data.tm_mon, data.tm_mday)


class Client(object):

    def __init__(self, server):
        self.server = server.rstrip('/')
        self.session = requests.session()
        # getting monolith info
        info = self.session.get(server).json
        if callable(info):
            info = info()

        self.es = self.server + info['es_endpoint']
        self.fields = info['fields']

    def __call__(self, field, start, end, interval=DAY, **terms):
        if isinstance(start, str):
            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')

        if interval == DAY:
            delta = (end - start).days
        elif interval == WEEK:
            delta = (end - start).weeks
        elif interval == MONTH:
            delta = (end.year - start.year) * 12 + end.month - start.month
        else:
            delta = end.year - start.year

        # building the query
        start_date_str = start.strftime('%Y-%m-%d')
        end_date_str = end.strftime('%Y-%m-%d')

        if isinstance(interval, int):
            interval = _interval2str[interval]

        # XXX we'll see later if we want to provide a
        # nicer query interface

        # we need a facet query
        query = {
            "query": {
                "match_all": {},
            },
            "size": delta,
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
                                "gte": start_date_str,
                                "lte": end_date_str,
                            }
                        }
                    }
                }
            }
        }

        if len(terms) > 0:
            term = {}

            for key, value in terms.items():
                term[key] = value

            range = query['facets']['histo1']['facet_filter']['range']
            filter = {'and': [{'term': term},
                              {'range': range}]}
            query['facets']['histo1']['facet_filter'] = filter

        res = self.session.post(self.es, data=json.dumps(query)).json

        if callable(res):
            res = res()

        if not isinstance(res, dict):
            raise ValueError(res)

        if 'errors' in res:
            raise ValueError(res['errors'][0]['description'])

        for entry in res['facets']['histo1']['entries']:
            date_ = datetime.datetime.fromtimestamp(entry['time'] / 1000.)
            if 'total' in entry:
                count = entry['total']
            else:
                count = entry['count']

            yield {'count': count, 'date': date_}


def main():
    raise NotImplementedError("add a CLI here")


if __name__ == '__main__':
    main()
