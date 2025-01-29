.PHONY: docs

default: install

all: install build


h help:
	@grep '^[a-z]' Makefile


install:
	pip install pip --upgrade
	pip install -r requirements.txt

upgrade:
	pip install pip --upgrade
	pip install -r requirements.txt --upgrade


s serve:
	mkdocs serve --config-file ../mkdocs.yml


b build:
	mkdocs build --config-file ../mkdocs.yml

d deploy:
	mkdocs gh-deploy --strict --force --config-file ../mkdocs.yml