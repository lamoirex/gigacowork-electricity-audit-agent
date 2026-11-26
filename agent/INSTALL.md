# Установка в GigaCowork

1. Соберите навык: `python build_skill.py` → `dist/utility-check.zip`.
2. Загрузите `dist/utility-check.zip` в GigaCowork как навык.
3. Загрузите `agent/system_prompt.txt` как системный промпт агента.
4. Приложите три Excel и отправьте пустое сообщение.

# Локальный запуск

~~~bash
pip install -r requirements-dev.txt
python testdata/generate.py
python agent/skill/utility-check/scripts/check_charges.py \
  testdata/out/charges.xlsx \
  testdata/out/norms.xlsx \
  testdata/out/stores.xlsx \
  runs/
python tools/evaluate.py runs/reconciliation.xlsx testdata/out/expected.json
~~~
