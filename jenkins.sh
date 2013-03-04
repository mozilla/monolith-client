#!/bin/sh
set -e

echo "Starting build on executor $EXECUTOR_NUMBER..."

# Make sure there's no old pyc files around.
find . -name '*.pyc' -exec rm {} \;

make build

echo "Running tests"

bin/python runtests.py

echo "Calculating coverage..."

bin/coverage xml $(find monolith/client -name '*.py')

echo "FIN"
