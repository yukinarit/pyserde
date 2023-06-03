SHELL:=/bin/bash
PYTHON ?= python
POETRY ?= poetry

.PHONY: all setup build test examples coverage fmt check docs open-docs bench

all: setup pep8 mypy docs test examples

setup:
	$(POETRY) install
	$(POETRY) run pip list
	$(POETRY) run pre-commit install

setup-bench:
	pushd bench && $(POETRY) install && popd

build:
	$(POETRY) build

test:
	$(POETRY) run pytest tests --doctest-modules serde -v -nauto

examples:
	pushd examples && $(POETRY) run $(PYTHON) runner.py && popd

coverage:
	$(POETRY) run pytest tests --doctest-modules serde -v -nauto --cov=serde --cov-report term --cov-report xml --cov-report html

fmt:
	$(POETRY) run pre-commit run black -a

check:
	$(POETRY) run pre-commit run -a
	$(POETRY) run mypy .

docs:
	mkdir -p docs out/api out/guide
	$(POETRY) run pdoc -e serde=https://github.com/yukinarit/pyserde/tree/main/serde/ serde -o out/api
	mdbook build -d out/guide

open-docs:
	$(POETRY) run pdoc -e serde=https://github.com/yukinarit/pyserde/tree/main/serde serde

bench:
	pushd bench && $(POETRY) run $(PYTHON) bench.py && popd
