.PHONY: all setup test unittest pep8 mypy docs

all: setup test

setup:
	pipenv install --dev --skip-lock
	pipenv run pip list

test: unittest pep8 mypy

unittest:
	pipenv run pytest -s

pep8:
	pipenv run pytest --codestyle

mypy:
	pipenv run mypy serde

docs:
	pipenv run pdoc serde.py --html --html-dir docs --overwrite

serve-docs:
	pipenv run pdoc --http --http-dir docs
