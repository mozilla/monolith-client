#!/bin/sh
set -e

echo "Starting build on executor $EXECUTOR_NUMBER..."

cd $WORKSPACE
VENV=$WORKSPACE/venv
ES_HOST='jenkins-es20:9200'

# Make sure there's no old pyc files around.
find . -name '*.pyc' -exec rm {} \;

# Handle virtualenv creation.
if [ ! -d "$VENV/bin" ]; then
  echo "No virtualenv found.  Making one..."
  virtualenv $VENV --system-site-packages
fi
source $VENV/bin/activate
pip install -U --exists-action=w --no-deps -q -r requirements/prod.txt -r requirements/test.txt

echo "Running tests"

make build
make test

echo "Calculating coverage..."

bin/coverage xml $(find monolith/client -name '*.py')

echo "FIN"
