"""Build dist/utility-check.zip from agent/skill."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "agent" / "skill" / "utility-check"
OUT = ROOT / "dist" / "utility-check.zip"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in SRC.rglob("*"):
            if p.is_file():
                arc = Path("utility-check") / p.relative_to(SRC)
                z.write(p, arc)
    print(f"Built {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
