# GigaCowork electricity audit agent

Детерминированная сверка начислений за электроэнергию с нормативами.

## Быстрый старт

~~~bash
pip install -r requirements-dev.txt
python testdata/generate.py
python agent/skill/utility-check/scripts/check_charges.py \
  testdata/out/charges.xlsx testdata/out/norms.xlsx testdata/out/stores.xlsx runs/
python tools/evaluate.py runs/reconciliation.xlsx testdata/out/expected.json
~~~

Ожидаемо: `accuracy: 14/14 = 100.00%`.

## Структура

- `agent/skill/utility-check/` — навык (SKILL.md, scripts, references)
- `agent/system_prompt.txt` — системный промпт агента
- `tests/` — юнит-тесты и интеграционный тест
- `testdata/` — синтетический набор и эталон
- `tools/evaluate.py` — сверка с эталоном
- `docs/` — алгоритм, допущения, вопросы заказчику
