from __future__ import annotations
from pathlib import Path

IDEAS_DIR = Path(__file__).resolve().parent
IDEA_RANGE = range(1, 6)

# Try UTF-8 first, then common Windows encodings
PREFERRED_ENCODINGS = ("utf-8", "utf-8-sig", "cp1252", "latin-1")

def _normalize_text(s: str) -> str:
    # Normalize newlines and optionally replace “smart” quotes/dashes
    s = s.replace("\r\n", "\n")
    replacements = {
        "\u2018": "'", "\u2019": "'",      # ‘ ’
        "\u201c": '"', "\u201d": '"',      # “ ”
        "\u2013": "-", "\u2014": "—",      # – —
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s

def _read_text_fallback(path: Path) -> str:
    for enc in PREFERRED_ENCODINGS:
        try:
            return _normalize_text(path.read_text(encoding=enc))
        except UnicodeDecodeError:
            continue
    # Last resort: replace undecodable bytes
    return _normalize_text(path.read_bytes().decode("utf-8", errors="replace"))

def _read_idea(n: int) -> str:
    path = IDEAS_DIR / f"idea{n}.md"
    try:
        return _read_text_fallback(path)
    except FileNotFoundError:
        return ""

IDEAS = {i: content for i in IDEA_RANGE if (content := _read_idea(i))}

def all_as_list() -> list[str]:
    return [IDEAS[i] for i in sorted(IDEAS)]

def all_as_markdown(delimiter: str = "\n\n---\n\n") -> str:
    parts = [f"# Idea {i}\n\n{IDEAS[i]}".strip() for i in sorted(IDEAS)]
    return delimiter.join(parts)

def write_bundle(filename: str = "all_ideas.md", delimiter: str = "\n\n---\n\n") -> Path:
    out = IDEAS_DIR / filename
    out.write_text(all_as_markdown(delimiter), encoding="utf-8")
    return out
