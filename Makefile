SHELL:=/bin/bash

.PHONY: all setup build test examples coverage pep8 mypy fmt docs open-docs bench

all: setup pep8 mypy docs test examples

setup:
	pipenv install --dev
	pipenv run pip list
	pushd examples && pipenv install --dev && popd

setup-bench:
	pushd bench && pipenv install --dev && popd

build:
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel

test:
	pipenv run pytest tests --doctest-modules serde -v

examples:
	pushd examples && pipenv run python runner.py && popd

coverage:
	pipenv run pytest tests --doctest-modules serde -v --cov=serde --cov-report term --cov-report xml

pep8:
	pipenv run flake8

mypy:
	pipenv run mypy serde

fmt:
	pipenv run black serde tests bench/bench.py
	pipenv run isort -rc --atomic serde tests bench/bench.py

docs:
	pipenv run pdoc serde --html -o html --force
	cp -f html/serde/* docs/

open-docs:
	pipenv run pdoc serde --html -o html --force --http 127.0.0.1:5001

bench:
	pushd bench && pipenv run python bench.py && popd
