.PHONY: install test lint skill clean

install:
	pip install -r requirements-dev.txt

test:
	pytest -q

lint:
	ruff check .
	ruff format --check .

skill:
	python build_skill.py

clean:
	rm -rf dist runs/reconciliation.xlsx .pytest_cache .ruff_cache
