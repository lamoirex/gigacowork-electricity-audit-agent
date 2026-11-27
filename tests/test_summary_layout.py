import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from summary_layout import matches_summary  # noqa: E402

HEAD = "Проверено: 28 | В норме: 13 | Превышений: 4 | Исключений: 4 | Уточнений: 7"
BODY = "Причины: нет периода (2).\nУведомление: Проверить строки (7)."
TEMPLATE = HEAD + "\n" + BODY


def test_accepts_original_mixed_and_multiline_layouts():
    for limit in (0, 2, 4):
        answer = HEAD.replace(" | ", "  \n", limit) + "\n" + BODY
        assert matches_summary(answer, TEMPLATE)


def test_rejects_changed_missing_reordered_or_extra_content():
    changes = [
        ("Превышений: 4", "Превышений: 5"),
        (" | В норме: 13", ""),
        ("Проверено: 28 | В норме: 13", "В норме: 13 | Проверено: 28"),
        ("нет периода (2)", "нет периода (3)"),
        ("Проверить строки (7)", "Проверить строки (8)"),
        ("Причины:", "Комментарий: всё верно. Причины:"),
    ]
    for old, new in changes:
        assert not matches_summary(TEMPLATE.replace(old, new), TEMPLATE)
