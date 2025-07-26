"""Prompt loader. Loads large prompt templates from version-controlled text files."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_THIS_DIR: Final[Path] = Path(__file__).resolve().parent
_DATE_PKG: Final[str] = "v250718"
_DATE_DIR: Final[Path] = _THIS_DIR / _DATE_PKG
_TXT_DIR: Final[Path] = _DATE_DIR


def _load(filename: str) -> str:
    """Return the contents of *filename* located in the texts directory."""
    path = _TXT_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


RAG_PROMPT_TEMPLATE: str = _load("rag_prompt.txt")
EXTRACT_PROMPT_TEMPLATE: str = _load("extract_prompt.txt")


__all__ = [
    "RAG_PROMPT_TEMPLATE",
    "EXTRACT_PROMPT_TEMPLATE",
]
