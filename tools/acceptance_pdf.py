"""Render a self-contained Russian report from measurements and project documents."""

from pathlib import Path
from xml.sax.saxutils import escape

from field_metrics import SCHEMA
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def render(root, target, runs):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font = next((Path(p) for p in candidates if Path(p).is_file()), None)
    if not font:
        raise RuntimeError("Для PDF установите Arial или DejaVu Sans с кириллицей.")
    pdfmetrics.registerFont(TTFont("Audit", str(font)))
    story = []
    body = ParagraphStyle("body", fontName="Audit", fontSize=9.5, leading=14, spaceAfter=6)
    title = ParagraphStyle(
        "title",
        parent=body,
        fontSize=17,
        leading=22,
        spaceAfter=12,
        textColor=colors.HexColor("#15524c"),
    )

    def para(value, style=body):
        story.append(Paragraph(escape(str(value)), style))

    def table(rows):
        t = Table(rows, repeatRows=1, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Audit"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#daeae6")),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f3f6f5")],
                    ),
                ]
            )
        )
        story.extend([t, Spacer(1, 10)])

    para("Сверка начислений за электроэнергию", title)
    para("Контрольный отчёт • Фабрика решений")
    para(
        "Задача сотрудника — проверить начисления, сопоставив расход и сумму без НДС с "
        "нормативом магазина за тот же месяц. На выходе доступны книга Excel и черновик "
        "уведомления."
    )
    para("Вопросы к заказчику", title)
    for line in (root / "docs/customer_questions.md").read_text().splitlines():
        if line[:1].isdigit():
            para(line)
    story.append(PageBreak())
    para("Правила и расчёт", title)
    for line in (root / "docs/algorithm.md").read_text().splitlines():
        if line.startswith("| ") and line.split("|")[1].strip().isdigit():
            para(" · ".join(s.strip() for s in line.strip("|").split("|")).replace("**", ""))
        elif line[:1].isdigit() or line.startswith("- "):
            para(line.replace("`", ""))
    para("Допущения", title)
    for line in (root / "docs/assumptions.md").read_text().splitlines():
        if line and not line.startswith("#"):
            para(line.strip().lstrip("- ").replace("`", ""))
    story.append(PageBreak())
    para("Данные и эталон", title)
    para(
        "Основной набор содержит 28 начислений за январь–март 2025 года, 26 строк "
        "нормативов и 8 магазинов. Включены ровно 10% и 10,01%, нулевой норматив, неверная "
        "единица норматива, разные написания ID, пропуски, дубль и конкурирующие версии. "
        "Ожидаемые решения заданы генератором независимо от скрипта навыка."
    )
    para(
        "Дополнительные наборы проверяют чужие заголовки на 2 строках и комбинации правил "
        "на 90 строках. В каждом наборе используется один и тот же вход для трёх повторов. "
        "Архив testdata.zip содержит основной набор, разметку и генератор."
    )
    para("Excel в порядке колонок", title)
    for name, columns in SCHEMA.items():
        para(name + " — " + ", ".join(columns) + ".")
    para("Метод измерения", title)
    para(
        "Для каждой строки проверяются значения или ожидаемая пустота, причина, журнал и "
        "принадлежность реестру. Подстановка — заполненная ячейка вместо ожидаемой пустой "
        "среди входных и расчётных полей. Стабильность определяется по SHA-256 содержимого "
        "всех листов. Порог точности — 95%, форма — 100%, допустимых подстановок — 0."
    )
    para(
        "В режиме API скрипт читает три книги, сохраняет Excel и передаёт модели "
        "синтетическую сводку для краткого ответа по шаблону. Время включает обработку "
        "файлов и ожидание API. Локальный режим измеряет только CLI. Отдельным этапом "
        "остаётся проверка пустого сообщения с вложениями в интерфейсе GigaCowork."
    )
    story.append(PageBreak())
    para("Результаты контрольных прогонов", title)
    para(
        "Инструмент: "
        + runs[0]["mode"]
        + ". Модель: "
        + ", ".join(sorted({r.get("model") or "не использовалась" for r in runs}))
    )
    if "replay_revision" in runs[0]:
        original = sum(r["original_chat_ok"] for r in runs)
        current = sum(r["chat_ok"] for r in runs)
        para(
            f"Повторная оценка тех же ответов GigaChat. Исходный валидатор: "
            f"{original}/{len(runs)}. После допуска переносов между счётчиками: "
            f"{current}/{len(runs)}. Время взято из первоначальных запусков API."
        )
    rows = [["Набор", "№", "Строки", "Подстановки", "Форма", "Время, с", "Чат"]]
    for r in runs:
        m = r["fields"]
        rows.append(
            [
                r["dataset"],
                str(r["repeat"]),
                f"{m['exact']}/{m['rows']}",
                str(m["substitutions"]),
                "OK" if m["shape"] and m["schema"] else "FAIL",
                str(r["seconds"]),
                {None: "—", True: "OK", False: "FAIL"}[r.get("chat_ok")],
            ]
        )
    table(rows)
    for name in dict.fromkeys(r["dataset"] for r in runs):
        part = [r for r in runs if r["dataset"] == name]
        para(
            f"{name}: совпадение содержимого книг в трёх повторах — "
            + ("да" if len({r["sha256"] for r in part}) == 1 else "нет")
        )
    story.append(PageBreak())
    para("Точность по полям за все повторы", title)
    denom = sum(r["fields"]["rows"] for r in runs)
    for key in runs[0]["fields"]["correct_by_field"]:
        n = sum(r["fields"]["correct_by_field"][key] for r in runs)
        para(f"{key} — {n}/{denom} ({n / denom:.1%})")
    story.append(PageBreak())
    para("Лог первого прогона", title)
    sample = runs[0]
    para(
        f"Набор {sample['dataset']}, повтор 1. Выходной файл reconciliation.xlsx. "
        f"Время {sample['seconds']} с."
    )
    for line in sample["transcript"].splitlines():
        if line.strip():
            para(line)
    para("Дальнейшая проверка", title)
    para(
        "Подтвердить правила с владельцами процесса и проверить обезличенную пачку с "
        "ручной разметкой специалиста. Замерить время сотрудника до и после внедрения. "
        "Подтверждение заказчика и запуск в его пространстве фиксируются отдельно."
    )
    SimpleDocTemplate(
        str(target),
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=40,
        bottomMargin=38,
        title="Сверка начислений за электроэнергию",
    ).build(story)
