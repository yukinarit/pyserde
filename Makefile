SHELL:=/bin/bash
PYTHON ?= python
PIPENV ?= pipenv

.PHONY: all setup build test examples coverage pep8 mypy fmt docs open-docs bench

all: setup pep8 mypy docs test examples

setup:
	$(PIPENV) install --dev --skip-lock
	$(PIPENV) run pip list
	$(PIPENV) run pre-commit install
	pushd examples && $(PIPENV) install --dev && popd

setup-bench:
	pushd bench && $(PIPENV) install && popd

build:
	$(PIPENV) run $(PYTHON) setup.py sdist
	$(PIPENV) run $(PYTHON) setup.py bdist_wheel

test:
	$(PIPENV) run pytest tests --doctest-modules serde -v

examples:
	pushd examples && $(PIPENV) run $(PYTHON) runner.py && popd

coverage:
	$(PIPENV) run pytest tests --doctest-modules serde -v --cov=serde --cov-report term --cov-report xml

pep8:
	$(PIPENV) run flake8

mypy:
	$(PIPENV) run mypy serde

fmt:
	$(PIPENV) run pre-commit run -a

docs:
	mkdir -p docs
	$(PIPENV) run pdoc serde --html -o html --force --template-dir docs/template
	cp -f html/serde/* docs/

open-docs:
	$(PIPENV) run pdoc serde --html -o html --force --template-dir docs/template --http 127.0.0.1:5001

bench:
	pushd bench && $(PIPENV) run $(PYTHON) bench.py && popd
