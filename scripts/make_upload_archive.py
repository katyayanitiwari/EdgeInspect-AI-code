"""Create a shareable project archive without local/private material.

Run from the project root:
    python scripts/make_upload_archive.py

Output is written beside the project folder on the Desktop. The existing ZIP is
left untouched so the new package can be reviewed before replacing anything.
"""
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / "EdgeInspect-AI-Kria-Renesas-Stage.zip"
ARCHIVE_ROOT = ROOT.name

EXCLUDED_DIRS = {
    ".git", ".venv", "__pycache__", ".gradio", "runs", "logs",
    "EdgeInspect-AI-Private-Local-Files", "EdgeInspect-AI-Windows-First",
}
EXCLUDED_PREFIXES = {
    Path("dataset/raw"), Path("dataset/processed"),
    Path("datasets/raw"), Path("datasets/processed"),
    Path("inference/output"), Path("reports/showcase"), Path("reports/_figs"),
    Path("deployment/kaggle_upload/dataset"), Path("deployment/kaggle_upload/kernel"),
    Path("deployment/kaggle_upload/output"),
}
EXCLUDED_NAMES = {
    "MY_NOTES_Done_and_Left.pdf", "RESUME_PROMPT.md",
    "EdgeInspect-AI_RESUME_PROMPT.md", "edgeinspect-dashboard.err.log",
    "edgeinspect-dashboard.out.log", "tailscale-install.log",
}


def excluded(relative: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return True
    if any(relative == prefix or prefix in relative.parents for prefix in EXCLUDED_PREFIXES):
        return True
    name = relative.name
    lower = name.lower()
    if name in EXCLUDED_NAMES:
        return True
    if lower.endswith((".zip", ".msi", ".log", ".pem", ".key")):
        return True
    if lower == ".env" or lower.startswith(".env."):
        return True
    if name.startswith("_preview"):
        return True
    if relative.as_posix() == "app/samples/sample_people.jpg":
        return True
    return False


def main() -> None:
    included: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if excluded(relative):
            continue
        included.append(path)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(included):
            relative = path.relative_to(ROOT)
            archive.write(path, (Path(ARCHIVE_ROOT) / relative).as_posix())

    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"Created: {OUTPUT}")
    print(f"Files included: {len(included)}")
    print(f"Archive size: {size_mb:.2f} MiB")


if __name__ == "__main__":
    main()
