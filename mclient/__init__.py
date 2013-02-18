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
        info = self.session.get(server).json()
        self.es = self.server + info['es_endpoint']
        self.fields = info['fields']

    def __call__(self, field, start, end, interval=DAY, query=None):
        if isinstance(start, str):
            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')

        # building the query
        delta = (end - start).days
        start_date_str = start.strftime('%Y-%m-%d')
        end_date_str = end.strftime('%Y-%m-%d')

        if isinstance(interval, int):
            interval = _interval2str[interval]

        # XXX we'll see later if we want to provide a
        # nicer query interface
        if query is None
            query = {"match_all": {}}

        if interval == 'day':
            # simple day query
            query = {
                 "query": {"match_all": {}},
                 "filter": {"range": {"date":
                            {"gte": start_date_str, "lt": end_date_str}}},
                 "sort": [{"date": {"order" : "asc"}}],
                 "size": delta }

            res = self.session.post(self.es, data=json.dumps(query)).json()

            for hit in res['hits']['hits']:
                data = hit['_source']
                yield {'count': data[field], 'date': _iso2date(data['date'])}
        else:
            # we need a facet query
            query = {
                 "query": {"match_all": {}},
                 "filter": {"range": {"date":
                            {"gte": start_date_str, "lt": end_date_str}}},
                 "sort": [{"date": {"order" : "asc"}}],
                 "size": delta ,
                 "facets": {"histo1": {
                                "date_histogram": {
                                           "value_field" : field,
                                           "interval": interval,
                                           "key_field": "date"}
                                }
                    }
                 }

            res = self.session.post(self.es, data=json.dumps(query)).json()

            for entry in res['facets']['histo1']['entries']:

                date_ = datetime.datetime.fromtimestamp(entry['time'] / 1000.)
                yield {'count': entry['total'], 'date': date_}



if __name__ == '__main__':
    c = Client('http://0.0.0.0:6543')

    for hit in c('downloads_count', '2012-01-01', '2012-01-31'):
        print hit

    for hit in c('downloads_count', '2012-01-01', '2012-01-31', interval='week'):
        print hit
