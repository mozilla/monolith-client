#!/bin/sh
set -e

echo "Starting build on executor $EXECUTOR_NUMBER..."

# Make sure there's no old pyc files around.
find . -name '*.pyc' -exec rm {} \;

make build

echo "Starting ElasticSearch and Pyramid..."

elasticsearch/bin/elasticsearch -p es.pid
bin/pserve --pid-file monolith.pid --daemon monolith.ini
sleep 5

echo "Starting tests..."

bin/nosetests -s -d -v --with-xunit --with-coverage --cover-package monolith monolith

echo "Stopping ElasticSearch and Pyramid"
kill `cat es.pid`
kill `cat monolith.pid`
rm -f es.pid
rm -f monolith.pid

echo "Calculating coverage..."

bin/coverage xml $(find monolith/client -name '*.py')

echo "FIN"
