import os
import sys
import time


def main():
    ret = {}

    os.system('rm -rf elasticsearch/data/monotest/')
    try:
        ret['es_start'] = os.system(
            'elasticsearch/bin/elasticsearch -p es.pid')
        ret['monolith_start'] = os.system(
            'bin/pserve --pid-file monolith.pid --daemon monolith.ini')
        time.sleep(5)
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
