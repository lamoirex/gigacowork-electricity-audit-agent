# Contributing

Установка локального окружения:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install

Перед push:
ruff check .
ruff format --check .
pytest -q

Conventional commits: feat(scope):, fix(scope):, docs:, test:, chore:, build:, ci:.
