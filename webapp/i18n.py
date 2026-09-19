# -*- coding: utf-8 -*-
"""
Textos de la webapp UCEMA — solo español.
"""
import json
from pathlib import Path

_LOCALES_DIR = Path(__file__).resolve().parent / "locales"
_TEXTS: dict[str, str] = {}


def _load() -> dict[str, str]:
    global _TEXTS
    if _TEXTS:
        return _TEXTS
    path = _LOCALES_DIR / "es.json"
    try:
        with open(path, encoding="utf-8") as f:
            _TEXTS = json.load(f)
    except Exception:
        _TEXTS = {}
    return _TEXTS


def _(key: str, **kwargs) -> str:
    """Devuelve el texto en español para la clave."""
    text = _load().get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
