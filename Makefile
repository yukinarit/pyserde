SHELL:=/bin/bash
PYTHON ?= python
UV ?= uv

.PHONY: all setup build test examples coverage fmt check docs open-docs bench

all: setup pep8 mypy docs test examples

setup:
	$(UV) sync
	$(UV) run pip list
	$(UV) run pre-commit install

setup-bench:
	pushd bench && $(UV) sync && popd

build:
	$(UV) build

test:
	$(UV) run pytest tests --doctest-modules serde -v -nauto

examples:
	$(UV) run $(PYTHON) examples/runner.py

coverage:
	$(UV) run pytest tests --doctest-modules serde -v -nauto --cov=serde --cov-report term --cov-report xml --cov-report html

fmt:
	$(UV) run pre-commit run black -a

check:
	$(UV) run pre-commit run -a

docs:
	$(UV) run mkdocs build

docs-serve:
	$(UV) run mkdocs serve

docs-deploy:
	$(UV) run mike deploy --push --update-aliases $(VERSION) latest

bench:
	pushd bench && $(UV) run $(PYTHON) bench.py && popd
