import os
import sys
import time

from pyelasticsearch import ElasticSearch


def wait_until_es_is_ready():
    client = ElasticSearch('http://localhost:9213')
    time.sleep(2)
    now = time.time()
    while time.time() - now < 30:
        try:
            # check to see if our process is ready
            health = client.health()
            status = health['status']
            name = health['cluster_name']
            if status == 'green' and name == 'monotest':
                return 0
        except Exception:
            # wait a bit before re-trying
            time.sleep(0.5)
    return 1


def main():
    ret = {}

    os.system('rm -rf elasticsearch/data/monotest/')
    try:
        ret['es_start'] = os.system(
            'elasticsearch/bin/elasticsearch -p es.pid')
        ret['monolith_start'] = os.system(
            'bin/pserve --pid-file monolith.pid --daemon monolith.ini')
        ret['es_client'] = wait_until_es_is_ready()
        if not any(ret.values()):
            ret['test'] = os.system(
                'bin/nosetests -s -d -v --with-xunit --with-coverage '
                '--cover-package monolith monolith')
    finally:
        ret['es_stop'] = os.system('kill `cat es.pid`')
        ret['monolith_stop'] = os.system('kill `cat monolith.pid`')
        os.system('rm -f es.pid')
        os.system('rm -f monolith.pid')

    if any(ret.values()):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
