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

coverage:
	pip install pytest-cov
	pytest --cov=agent --cov-report=term-missing

format:
	ruff format .

security:
	pip install bandit
	bandit -r agent

scenarios:
	python testdata/scenarios/edge_mixed_ids.py
	python testdata/scenarios/edge_unicode.py
	python testdata/scenarios/edge_negative.py
	python testdata/scenarios/edge_bulk.py
