HERE = $(shell pwd)
PYTHON = python

INSTALL = pip install --no-deps
VTENV_OPTS ?= --distribute

.PHONY: all clean test

all: build

build:
	$(INSTALL) -r requirements/prod.txt
	$(INSTALL) -r requirements/dev.txt
	$(INSTALL) -r requirements/test.txt
	$(PYTHON) setup.py develop

test:
	nosetests -s -d -v --with-xunit --with-coverage --cover-package "monolith.client" monolith
