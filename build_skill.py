"""Build agent.zip and testdata.zip."""

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def main():
    DIST.mkdir(parents=True, exist_ok=True)

    # 0. Ensure testdata exists
    out_dir = ROOT / "testdata" / "out"
    if not (out_dir / "charges.xlsx").exists():
        print("Testdata missing, generating...")
        subprocess.run([sys.executable, "testdata/generate.py"], cwd=ROOT, check=True)

    required = ["charges.xlsx", "norms.xlsx", "stores.xlsx", "expected.json"]
    for req in required:
        if not (out_dir / req).exists():
            raise FileNotFoundError(f"Missing {req} after generation!")

    # 1. Skill
    skill_src = ROOT / "agent" / "skill" / "utility-check"
    skill_zip = DIST / "utility-check.zip"
    with zipfile.ZipFile(skill_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in skill_src.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc"):
                z.write(p, Path("utility-check") / p.relative_to(skill_src))

    # 2. Agent
    agent_zip = DIST / "agent.zip"
    with zipfile.ZipFile(agent_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(skill_zip, "utility-check.zip")
        z.write(ROOT / "agent" / "system_prompt.txt", "system_prompt.txt")
        z.write(ROOT / "agent" / "INSTALL.md", "INSTALL.md")

    # 3. Testdata
    testdata_zip = DIST / "testdata.zip"
    with zipfile.ZipFile(testdata_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT / "testdata" / "generate.py", "generate.py")
        for name in required:
            z.write(out_dir / name, name)

    print("Built:")
    for f in DIST.glob("*.zip"):
        print(f"  {f.name} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
