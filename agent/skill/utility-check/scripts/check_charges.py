#!/usr/bin/env python3
"""Deterministic reconciliation of utility charges against norms."""
from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import openpyxl
from openpyxl import Workbook

HERE = Path(__file__).resolve().parent.parent
SYN = json.loads((HERE / "references" / "column_synonyms.json").read_text(encoding="utf-8"))
PARAMS = json.loads((HERE / "references" / "params.json").read_text(encoding="utf-8"))
THRESHOLD = float(PARAMS["threshold_percent"])
ALLOWED_UNITS = {u.strip().lower() for u in PARAMS["allowed_units"]["consumption"]}


def norm_header(h: Any) -> str:
    return re.sub(r"\s+", " ", str(h or "").strip().casefold())


def norm_id(v: Any) -> str:
    if v is None:
        return ""
    s = re.sub(r"\s+", "", str(v).strip().lower())
    s = re.sub(r"[^\w]", "", s, flags=re.UNICODE)
    if s.isdigit():
        return s.lstrip("0") or "0"
    return s


def to_float(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace("\u00a0", "").replace(" ", "").replace(",", "."))
    except (ValueError, TypeError):
        return None


def to_date(v: Any) -> date | None:
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y", "%Y.%m.%d"):
            try:
                return datetime.strptime(v.strip(), fmt).date()
            except ValueError:
                pass
    return None


def period_key(v: Any) -> str | None:
    if v is None or v == "":
        return None
    if isinstance(v, (date, datetime)):
        return f"{v.year:04d}-{v.month:02d}"
    s = str(v).strip()
    m = re.match(r"^(\d{4})[-./](\d{1,2})", s)
    if m:
        month = int(m.group(2))
        if not (1 <= month <= 12):
            return None
        return f"{int(m.group(1)):04d}-{month:02d}"
    m = re.match(r"^(\d{1,2})[-./](\d{4})", s)
    if m:
        month = int(m.group(1))
        if not (1 <= month <= 12):
            return None
        return f"{int(m.group(2)):04d}-{month:02d}"
    return None


def find_col(headers: list, synonyms: list) -> int | None:
    m = {norm_header(h): i for i, h in enumerate(headers)}
    for s in synonyms:
        k = norm_header(s)
        if k in m:
            return m[k]
    return None


def read_table(path: Path, kind: str) -> list[dict]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = rows[0]
    idx = {k: find_col(headers, v) for k, v in SYN[kind].items()}
    out = []
    for i, r in enumerate(rows[1:], start=2):
        rec = {"__row__": i}
        for k, j in idx.items():
            rec[k] = r[j] if (j is not None and j < len(r)) else None
        out.append(rec)
    return out


def full_month(start: date | None, end: date | None, period: str) -> bool:
    if start is None or end is None or period is None:
        return False
    py, pm = int(period[:4]), int(period[5:7])
    last = calendar.monthrange(py, pm)[1]
    return (start.year == py and start.month == pm and start.day == 1 and
            end.year == py and end.month == pm and end.day == last)


@dataclass
class Decision:
    row: int
    rule: int
    status: str
    reason: str
    store_id: str = ""
    period: str = ""
    consumption: float | None = None
    amount_net: float | None = None
    norm_consumption: float | None = None
    norm_amount: float | None = None
    version: Any = ""
    dev_kwh: float | None = None
    dev_kwh_pct: float | None = None
    dev_rub: float | None = None
    dev_rub_pct: float | None = None


def pick_norm(norms: list[dict], store_id: str, period: str) -> dict | None:
    py, pm = int(period[:4]), int(period[5:7])
    first = date(py, pm, 1)
    candidates = [n for n in norms
                  if norm_id(n.get("store_id")) == store_id
                  and period_key(n.get("period")) == period]
    valid = []
    for n in candidates:
        vf = to_date(n.get("valid_from"))
        if vf is None:
            continue
        if vf <= first:
            valid.append((vf, str(n.get("version") or ""), n))
    if not valid:
        return None
    valid.sort(key=lambda t: (t[0], t[1]))
    return valid[-1][2]


def reconcile(charges: list[dict], norms: list[dict], stores: list[dict]) -> list[Decision]:
    store_ids = {norm_id(s.get("store_id")) for s in stores}
    seen: set[tuple] = set()
    out: list[Decision] = []
    for r in charges:
        d = Decision(row=r["__row__"], rule=0, status="", reason="")
        sid = norm_id(r.get("store_id"))
        d.store_id = str(r.get("store_id") or "").strip()
        d.period = period_key(r.get("period")) or ""
        d.consumption = to_float(r.get("consumption"))
        d.amount_net = to_float(r.get("amount_net"))

        missing = []
        if not sid:
            missing.append("ID магазина")
        if not d.period:
            missing.append("периода")
        if d.consumption is None:
            missing.append("потребления")
        if missing:
            d.rule, d.status = 1, "требуется уточнение"
            d.reason = "нет " + ", ".join(missing)
            out.append(d); continue

        if sid not in store_ids:
            d.rule, d.status = 2, "требуется уточнение"
            d.reason = "магазин не найден в справочнике"
            out.append(d); continue

        key = (sid, d.period, str(r.get("doc_number") or ""), str(r.get("charge_type") or ""))
        if key in seen:
            d.rule, d.status = 3, "исключение: дубль"
            d.reason = "повтор строки (магазин+период+документ+тип)"
            out.append(d); continue
        seen.add(key)

        ctype = str(r.get("charge_type") or "").strip().lower()
        if ctype.startswith("перерасч"):
            d.rule, d.status = 4, "исключение: перерасчёт"
            d.reason = "с нормативом не сравнивается"
            out.append(d); continue

        if not full_month(to_date(r.get("period_start")), to_date(r.get("period_end")), d.period):
            d.rule, d.status = 5, "исключение: неполный месяц"
            d.reason = "даты периода не покрывают календарный месяц или не совпадают с ним"
            out.append(d); continue

        norm = pick_norm(norms, sid, d.period)
        if norm is None:
            d.rule, d.status = 6, "требуется уточнение"
            d.reason = "нет норматива"
            out.append(d); continue

        u = str(r.get("unit") or "").strip().lower()
        nu = str(norm.get("norm_unit") or "").strip().lower()
        if not u or not nu or u not in ALLOWED_UNITS or u != nu:
            d.rule, d.status = 7, "требуется уточнение"
            d.reason = f"несовпадение единиц: {u!r} vs {nu!r}"
            out.append(d); continue

        nk = to_float(norm.get("norm_consumption"))
        na = to_float(norm.get("norm_amount"))
        if nk is None or na is None or d.amount_net is None:
            d.rule, d.status = 6, "требуется уточнение"
            d.reason = "норматив неполный"
            out.append(d); continue

        d.rule = 8
        d.norm_consumption = nk
        d.norm_amount = na
        d.version = norm.get("version") or ""
        d.dev_kwh = round((d.consumption or 0.0) - nk, 3)
        d.dev_rub = round(d.amount_net - na, 2)
        
        if nk > 0:
            raw_kwh_pct = (d.dev_kwh / nk) * 100
            d.dev_kwh_pct = round(raw_kwh_pct, 2)
            exceeded_kwh = raw_kwh_pct > THRESHOLD
            pct_kwh_str = f"{d.dev_kwh_pct}%"
        else:
            d.dev_kwh_pct = None
            exceeded_kwh = d.dev_kwh > 0
            pct_kwh_str = "н/д"
            
        if na > 0:
            raw_rub_pct = (d.dev_rub / na) * 100
            d.dev_rub_pct = round(raw_rub_pct, 2)
            exceeded_rub = raw_rub_pct > THRESHOLD
            pct_rub_str = f"{d.dev_rub_pct}%"
        else:
            d.dev_rub_pct = None
            exceeded_rub = d.dev_rub > 0
            pct_rub_str = "н/д"
            
        exceeded = exceeded_kwh or exceeded_rub
        d.status = "превышение" if exceeded else "в норме"
        
        reason = f"факт {d.consumption} кВт·ч / {d.amount_net} руб. vs норматив {nk} кВт·ч / {na} руб.; откл. {pct_kwh_str} / {pct_rub_str}"
        if nk == 0 or na == 0:
            reason += " (Факт положительный при нулевом нормативе)"
        d.reason = reason
        out.append(d)
    return out


def write_output(decisions: list[Decision], out_dir: Path) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Отклонения"
    ws.append([
        "ID магазина", "Период", "Потребление, кВт·ч", "Начислено без НДС, руб.",
        "Норматив, кВт·ч", "Норматив, руб.", "Версия норматива",
        "Отклонение, кВт·ч", "Отклонение, % (кВт·ч)", "Отклонение, руб.",
        "Отклонение, % (руб.)", "Статус", "Обоснование",
    ])
    for d in decisions:
        ws.append([d.store_id, d.period, d.consumption, d.amount_net,
                   d.norm_consumption, d.norm_amount, d.version,
                   d.dev_kwh, d.dev_kwh_pct, d.dev_rub, d.dev_rub_pct,
                   d.status, d.reason])

    we = wb.create_sheet("Реестр исключений")
    we.append(["Строка", "ID магазина", "Период", "Статус", "Причина", "Действие"])
    for d in decisions:
        if d.status.startswith("исключение") or d.status == "требуется уточнение":
            action = "проверить вручную" if d.status.startswith("исключение") else "уточнить данные"
            we.append([d.row, d.store_id, d.period, d.status, d.reason, action])

    wj = wb.create_sheet("Журнал решений")
    wj.append(["Строка", "Правило", "Статус", "Основание"])
    for d in decisions:
        wj.append([d.row, d.rule, d.status, d.reason])

    out = out_dir / "reconciliation.xlsx"
    wb.save(out)
    return out


def summarize(decisions: list[Decision]) -> dict:
    s = {"checked": len(decisions), "exceeded": 0, "ok": 0,
         "exceptions": 0, "clarifications": 0}
    reasons: dict[str, int] = {}
    for d in decisions:
        if d.status == "превышение":
            s["exceeded"] += 1
        elif d.status == "в норме":
            s["ok"] += 1
        elif d.status.startswith("исключение"):
            s["exceptions"] += 1
        else:
            s["clarifications"] += 1
        if d.status != "в норме":
            reasons[d.status] = reasons.get(d.status, 0) + 1
    s["reasons"] = reasons
    return s


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("charges")
    ap.add_argument("norms")
    ap.add_argument("stores")
    ap.add_argument("out_dir")
    a = ap.parse_args(argv)
    charges = read_table(Path(a.charges), "charges")
    norms = read_table(Path(a.norms), "norms")
    stores = read_table(Path(a.stores), "stores")
    decisions = reconcile(charges, norms, stores)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    xlsx = write_output(decisions, out)
    summary = summarize(decisions)
    summary["xlsx"] = str(xlsx)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
