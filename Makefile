.PHONY: all setup build test unittest pep8 mypy bench

all: setup test pep8 mypy

setup:
	pipenv install --dev --skip-lock
	pipenv run pip list

build:
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel

test: 
	pipenv run pytest -s

pep8:
	pipenv run pytest --codestyle

mypy:
	pipenv run mypy serde

fmt:
	pipenv run yapf --recursive -i serde test_serde.py bench.py
	pipenv run isort -rc --atomic serde test_serde.py bench.py

bench:
	pipenv run python bench.py
