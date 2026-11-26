"""Input validation."""

from pathlib import Path


class ValidationError(Exception):
    pass


REQUIRED = {
    "charges": ["ID магазина", "Период", "Потребление"],
    "norms": ["ID магазина", "Период", "Норматив потребления"],
    "stores": ["ID магазина"],
}


def validate_file(path: Path, kind: str) -> None:
    if not path.exists():
        raise ValidationError(f"файл не найден: {path}")
    if path.suffix.lower() not in (".xlsx", ".xls"):
        raise ValidationError(f"неподдерживаемый формат: {path.suffix}")
