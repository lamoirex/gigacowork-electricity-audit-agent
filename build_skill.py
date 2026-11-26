"""Build dist/agent.zip and dist/testdata.zip."""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def zip_dir(src: Path, out: Path):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src.parent))


def main():
    DIST.mkdir(parents=True, exist_ok=True)

    # 1. Skill zip
    skill_src = ROOT / "agent" / "skill" / "utility-check"
    skill_zip = DIST / "utility-check.zip"
    with zipfile.ZipFile(skill_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in skill_src.rglob("*"):
            if p.is_file():
                z.write(p, Path("utility-check") / p.relative_to(skill_src))

    # 2. Agent zip (skill + prompt + install)
    agent_zip = DIST / "agent.zip"
    with zipfile.ZipFile(agent_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(skill_zip, "utility-check.zip")
        z.write(ROOT / "agent" / "system_prompt.txt", "system_prompt.txt")
        z.write(ROOT / "agent" / "INSTALL.md", "INSTALL.md")

    # 3. Testdata zip
    testdata_src = ROOT / "testdata"
    testdata_zip = DIST / "testdata.zip"
    with zipfile.ZipFile(testdata_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(testdata_src / "generate.py", "generate.py")
        for p in (testdata_src / "out").glob("*"):
            if p.is_file():
                z.write(p, p.name)
        if (testdata_src / "scenarios").exists():
            for p in (testdata_src / "scenarios").glob("*.py"):
                z.write(p, f"scenarios/{p.name}")

    print("Built:")
    for f in DIST.glob("*.zip"):
        print(f"  {f.name} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
