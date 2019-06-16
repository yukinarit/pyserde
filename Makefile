.PHONY: all setup build test unittest pep8 mypy bench

all: setup test pep8 mypy

setup:
	pipenv install --dev
	pipenv run pip list

build:
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel

test: 
	pipenv run pytest -v

coverage:
	pipenv run pytest --cov=serde --cov-report term --cov-report xml

pep8:
	pipenv run flake8

mypy:
	pipenv run mypy serde

fmt:
	pipenv run yapf --recursive -i serde test_serde.py bench.py
	pipenv run isort -rc --atomic serde test_serde.py bench.py

bench:
	pipenv run python bench.py
