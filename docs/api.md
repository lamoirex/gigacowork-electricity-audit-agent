# API скрипта

## Командная строка

    python check_charges.py charges.xlsx norms.xlsx stores.xlsx out_dir

## Возвращаемое значение

JSON в stdout:

- checked: всего строк проверено
- exceeded: сколько превышений
- ok: сколько в норме
- exceptions: сколько исключений (перерасчёт, дубль, неполный месяц)
- clarifications: сколько требуют уточнения
- reasons: словарь статус-причина
- xlsx: путь к созданному файлу

## Коды выхода

- 0 - успех
- 2 - неверные аргументы
