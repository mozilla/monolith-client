import requests
import datetime
import json


DAY = 1
WEEK = 2
MONTH = 3
YEAR = 4


class Client(object):

    def __init__(self, server):
        self.server = server.rstrip('/')
        self.session = requests.session()
        # getting monolith info
        info = self.session.get(server).json()
        self.es = self.server + info['es_endpoint']
        self.fields = info['fields']

    def __call__(self, field, start, end, aggregate=DAY):
        if isinstance(start, str):
            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')

        # building the query
        delta = (end - start).days
        start_date_str = start.strftime('%Y-%m-%d')
        end_date_str = end.strftime('%Y-%m-%d')


        if aggregate == DAY:
            # simple day query
            query = {"query": {"match_all": {}},
                "filter": {"range": {"date":
                            {"gte": start_date_str, "lt": end_date_str}}},
                "sort": [{"date": {"order" : "asc"}}],
                "size": delta }

        else:
            # we need a facet query
            raise NotImplementedError()

        res = self.session.post(self.es, data=json.dumps(query)).json()
        for hit in res['hits']['hits']:
            yield hit['_source']



if __name__ == '__main__':
    c = Client('http://0.0.0.0:6543')
    for hit in c('downloads_count', '2012-01-01', '2012-01-31'):
        print hit
