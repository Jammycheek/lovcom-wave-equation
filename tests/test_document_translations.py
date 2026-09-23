"""Keep authored research prose paired without changing canonical instruments."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PROSE_DIRS = (ROOT, *(ROOT / name for name in ("data", "docs", "paper", "protocols", "registry")))


def _display_math(document: str) -> list[str]:
    # Terminal punctuation is prose; the expression itself must match exactly.
    return [
        re.sub(r"\s+", "", match).rstrip(".,;")
        for match in re.findall(r"\\\[(.*?)\\\]", document, flags=re.DOTALL)
    ]


def test_english_research_markdown_has_japanese_companion() -> None:
    for directory in PROSE_DIRS:
        for original in directory.glob("*.md"):
            if original.name.endswith(".ja.md"):
                continue
            companion = original.with_name(original.stem + ".ja.md")
            assert companion.is_file(), f"Missing Japanese companion for {original}"
            english = original.read_text(encoding="utf-8")
            japanese = companion.read_text(encoding="utf-8")
            assert f"[英語原本]({original.name})" in japanese
            assert len(re.findall(r"(?m)^```", english)) == len(
                re.findall(r"(?m)^```", japanese)
            ), original.name
            assert english.count(r"\[") == japanese.count(r"\["), original.name
            assert english.count(r"\]") == japanese.count(r"\]"), original.name
            assert _display_math(english) == _display_math(japanese), original.name


def test_japanese_companion_has_english_original() -> None:
    for directory in PROSE_DIRS:
        for companion in directory.glob("*.ja.md"):
            original = companion.with_name(companion.name.removesuffix(".ja.md") + ".md")
            assert original.is_file(), f"Orphaned Japanese companion: {companion}"
