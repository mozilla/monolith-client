#!/bin/sh
set -e

echo "Starting build on executor $EXECUTOR_NUMBER..."

# Make sure there's no old pyc files around.
find . -name '*.pyc' -exec rm {} \;

make build

echo "Starting tests..."

bin/nosetests -s -d -v --with-xunit --with-coverage --cover-package mclient mlient
bin/coverage xml $(find mclient -name '*.py')

echo "FIN"
