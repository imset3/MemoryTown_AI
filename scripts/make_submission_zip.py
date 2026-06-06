from __future__ import annotations

import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "submission"
OUTPUT_PATH = OUTPUT_DIR / "MemoryTown_AI_submission.zip"

INCLUDE_PATHS = [
    "app.py",
    "memorytown",
    "data/sample_agents.json",
    "docs",
    "tests",
    "scripts/make_submission_zip.py",
    "README.md",
    "requirements.txt",
    ".env.example",
]

EXCLUDE_PARTS = {
    ".git",
    ".env",
    "__pycache__",
    ".venv",
    "venv",
    ".pytest_cache",
    "reports",
}


def should_include(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_PARTS:
        return False
    if path.suffix == ".pyc":
        return False
    return True


def iter_files() -> list[Path]:
    files: list[Path] = []
    for item in INCLUDE_PATHS:
        path = PROJECT_ROOT / item
        if path.is_file() and should_include(path.relative_to(PROJECT_ROOT)):
            files.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                relative = child.relative_to(PROJECT_ROOT)
                if child.is_file() and should_include(relative):
                    files.append(child)
    return sorted(files)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in iter_files():
            archive.write(path, path.relative_to(PROJECT_ROOT))
    print(f"배포용 zip 생성 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
