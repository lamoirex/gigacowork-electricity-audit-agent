# Архитектура

Схема потока данных:

[GigaCowork] -> [GigaChat] -> [check_charges.py] -> [reconciliation.xlsx]
                                    |
                                    v
                            [JSON summary]

Модель только вызывает скрипт и пересказывает результат. Правила сверки - детерминированный код.
