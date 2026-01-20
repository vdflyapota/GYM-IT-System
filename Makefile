.PHONY: setup install start-dev start-docker lint test clean-pyc clean

PYTHON=python3

setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

install:
	. .venv/bin/activate && pip install -r requirements.txt

start-dev:
	. .venv/bin/activate && set -a && [ -f .env ] && . .env || true && set +a && $(PYTHON) -m src.app

lint:
	. .venv/bin/activate && flake8 && black --check . && bandit -r src

test:
	. .venv/bin/activate && pytest -q

clean-pyc:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean: clean-pyc
