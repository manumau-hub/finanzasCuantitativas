# -*- coding: utf-8 -*-
"""
Internacionalización (i18n) para la webapp.
Soporta Español (es), English (en), Italiano (it) y Português (pt).
"""
import json
from pathlib import Path

import streamlit as st

_LOCALES_DIR = Path(__file__).resolve().parent / "locales"
_DEFAULT_LANG = "es"
_SUPPORTED = {"es": "Español", "en": "English", "it": "Italiano", "pt": "Português"}


def _load_translations(lang: str) -> dict:
    """Carga las traducciones desde el archivo JSON del idioma."""
    path = _LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        path = _LOCALES_DIR / f"{_DEFAULT_LANG}.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_lang() -> str:
    """Devuelve el idioma actual (session_state o default)."""
    return st.session_state.get("i18n_lang", _DEFAULT_LANG)


def set_lang(lang: str) -> None:
    """Establece el idioma y recarga traducciones."""
    if lang in _SUPPORTED:
        st.session_state["i18n_lang"] = lang
        st.session_state["i18n_translations"] = _load_translations(lang)


def _translations() -> dict:
    """Obtiene el diccionario de traducciones actual (cache en session_state)."""
    lang = get_lang()
    if "i18n_translations" not in st.session_state:
        st.session_state["i18n_translations"] = _load_translations(lang)
    return st.session_state["i18n_translations"]


def _(key: str, **kwargs) -> str:
    """
    Traduce una clave. Ej: _("home.title")
    Si la clave no existe, devuelve la clave.
    kwargs permite interpolación: _("msg", name="X") → "Hola X" si msg="Hola {name}"
    """
    trans = _translations()
    s = trans.get(key, key)
    if kwargs:
        try:
            s = s.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return s


def render_language_selector() -> None:
    """Renderiza el selector de idioma en el sidebar. Debe llamarse desde cada página."""
    st.sidebar.markdown("---")
    opts = list(_SUPPORTED.keys())
    lang = st.sidebar.selectbox(
        _("lang.label"),
        options=opts,
        format_func=lambda k: _(f"lang.{k}"),
        index=opts.index(get_lang()) if get_lang() in opts else 0,
        key="i18n_lang_select",
    )
    if lang != get_lang():
        set_lang(lang)
        st.rerun()
