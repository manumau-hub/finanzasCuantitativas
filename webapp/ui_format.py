# -*- coding: utf-8 -*-
"""Helpers de formato para vencimientos y strikes en la webapp."""
from __future__ import annotations

from typing import Any, Sequence


def fmt_expiry(value: Any) -> str:
    """Normaliza expiry a YYYY-MM-DD."""
    if value is None:
        return ""
    s = str(value).strip()
    return s[:10] if len(s) >= 10 else s


def fmt_expiries(values: Sequence[Any]) -> list[str]:
    """Lista de expiries únicos ordenados como YYYY-MM-DD."""
    out: list[str] = []
    seen: set[str] = set()
    for v in values:
        e = fmt_expiry(v)
        if e and e not in seen:
            seen.add(e)
            out.append(e)
    return out


def norm_strike(value: Any) -> float:
    """Strike estable: entero si cabe, si no 2 decimales."""
    x = float(value)
    r = round(x)
    if abs(x - r) < 1e-6:
        return float(int(r))
    return round(x, 2)


def fmt_strike_label(value: Any) -> str:
    """Label legible para selectbox: $100 o $100.50."""
    x = norm_strike(value)
    if abs(x - round(x)) < 1e-9:
        return f"${int(round(x))}"
    return f"${x:.2f}"


def norm_strikes(values: Sequence[Any]) -> list[float]:
    """Strikes únicos ordenados, normalizados."""
    out: list[float] = []
    seen: set[float] = set()
    for v in values:
        try:
            s = norm_strike(v)
        except (TypeError, ValueError):
            continue
        if s not in seen:
            seen.add(s)
            out.append(s)
    return sorted(out)


def nearest_strike_index(opts: Sequence[float], target: Any) -> int:
    """Índice del strike más cercano a target (nunca falla si opts no está vacío)."""
    if not opts:
        return 0
    t = float(target)
    best_i = 0
    best_d = abs(float(opts[0]) - t)
    for i, s in enumerate(opts):
        d = abs(float(s) - t)
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def strikes_match(a: Any, b: Any, tol: float = 1e-6) -> bool:
    """Comparación tolerante de strikes."""
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False
