# -*- coding: utf-8 -*-
"""
Engine de superficie de volatilidad implícita.

Migrado desde VolSurface. Suavizado Vega-weighted con kernel gaussiano
en espacio (Delta, TTM). Sin dependencia de pandas (solo numpy) para
compatibilidad con entornos con numpy/pandas desalineados.

Input: list[dict] o dict de arrays. Output: dict de arrays.
"""
from __future__ import annotations

import numpy as np
from itertools import product
from typing import List, Dict, Any


def _to_dict_of_arrays(rows: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
    """Convierte list[dict] a dict de arrays."""
    if not rows:
        return {}
    keys = list(rows[0].keys())
    out = {}
    for k in keys:
        out[k] = np.array([r[k] for r in rows])
    return out


def _to_list_of_dicts(d: Dict[str, np.ndarray]) -> List[Dict[str, Any]]:
    """Convierte dict de arrays a list[dict]."""
    if not d:
        return []
    n = len(next(iter(d.values())))
    return [{k: d[k][i] for k in d} for i in range(n)]


class log_normal_vol_surface:
    """Base para superficies de volatilidad en espacio Delta/TTM."""

    def __init__(self, daycount: int = 360):
        self._daycount = daycount
        self.define_std_ttm_list_days()
        self.define_std_delta_strike()

    def set_daycount_convention(self, daycount: int) -> None:
        self._daycount = daycount

    def get_daycount_convention(self) -> int:
        return self._daycount

    def define_std_ttm_list_days(
        self,
        std_ttm: np.ndarray | None = None,
    ) -> None:
        if std_ttm is None:
            std_ttm = np.array([30, 60, 91, 122, 152, 182, 273, 365, 547, 730])
        self._std_ttm_days = std_ttm
        self._std_ttm_year_fraction = std_ttm / self._daycount

    def define_std_ttm_list_year_fraction(
        self,
        std_ttm: np.ndarray | None = None,
    ) -> None:
        if std_ttm is None:
            std_ttm = np.array(
                [0.08242, 0.16484, 0.25, 0.3352, 0.4176, 0.5, 0.75, 1, 1.5, 2]
            )
        self._std_ttm_year_fraction = std_ttm
        self._std_ttm_days = (std_ttm * self._daycount).astype(int)

    def define_std_delta_strike(
        self,
        std_delta: np.ndarray | None = None,
    ) -> None:
        if std_delta is None:
            # linspace evita el problema de arange con flotantes (puede incluir 0.80)
            std_delta = np.linspace(0.20, 0.75, 12)
        self._std_delta = std_delta


class gaussian_smooth(log_normal_vol_surface):
    """
    Suavizado Vega-weighted con kernel gaussiano.
    Input: raw_data como dict con keys TTM, YearFraction, CallPut, Delta, Vega, ImpliedVol, Date, ExerciseStyle, Spot.
    Output: dict con TTM, Delta, CallPut, ImpliedVol, Dispersion, Days, etc.
    """

    H1, H2, H3 = 0.05, 0.005, 0.001
    _TTM_DAYS = [30, 60, 91, 122, 152, 182, 273, 365, 547, 730]
    _YEAR_FRACTIONS = [
        0.082192, 0.164384, 0.249315, 0.334247, 0.416438,
        0.49863, 0.747945, 1.0, 1.49863, 2.0,
    ]

    def _aux_single_point(
        self,
        df_vol_surface: Dict[str, np.ndarray],
        df_raw: Dict[str, np.ndarray],
        j: int,
    ) -> tuple[float, float]:
        num = 0.0
        denom = 0.0
        dnum = 0.0
        h1, h2, h3 = self.H1, self.H2, self.H3
        yf_j = df_vol_surface["YearFraction"][j]
        cp_j = df_vol_surface["CallPut"][j]
        delta_j = df_vol_surface["Delta"][j]
        n_raw = len(df_raw["YearFraction"])

        for i in range(n_raw):
            yf_i = df_raw["YearFraction"][i]
            x = np.log(yf_i / yf_j)
            cp_i = df_raw["CallPut"][i]
            di = float(df_raw["Delta"][i])
            if cp_i == "C":
                if cp_j == "C":
                    dj, z = delta_j, 0
                else:
                    dj, z = delta_j + 1, 1
            else:
                di = di + 1
                if cp_j == "C":
                    dj, z = delta_j, 1
                else:
                    dj, z = delta_j + 1, 0
            y = di - dj
            phi = np.exp(-x * x / (2 * h1) - y * y / (2 * h2) - z * z / (2 * h3))
            vega_i = float(df_raw["Vega"][i])
            iv_i = float(df_raw["ImpliedVol"][i])
            num += vega_i * iv_i * phi
            dnum += vega_i * iv_i * iv_i * phi
            denom += vega_i * phi

        if denom <= 0:
            return (np.nan, np.nan)
        smooth_iv = num / denom
        disp = np.sqrt(max(0, dnum / denom - smooth_iv * smooth_iv))
        return (float(smooth_iv), float(disp))

    def generate_volatility_surface(
        self,
        raw_data: Dict[str, np.ndarray] | List[Dict[str, Any]],
        vega_min: float = 0.5,
        ttm_min: int = 10,
    ) -> Dict[str, np.ndarray]:
        """Genera superficie. raw_data: dict de arrays o list[dict]."""
        if isinstance(raw_data, list):
            raw_data = _to_dict_of_arrays(raw_data)
        df_raw = {k: np.array(v, copy=True) for k, v in raw_data.items()}

        mask = (df_raw["Vega"] >= vega_min) & (df_raw["TTM"] > ttm_min)
        for k in df_raw:
            df_raw[k] = df_raw[k][mask]
        n = len(df_raw["TTM"])
        if n == 0:
            raise ValueError(
                "No hay datos después de filtrar por Vega>=%s y TTM>%s."
                % (vega_min, ttm_min)
            )

        std_ttms = self._std_ttm_days
        std_deltas = self._std_delta
        rows_vol = []
        for ttm, d, cp in product(std_ttms, std_deltas, ["C"]):
            rows_vol.append({"TTM": ttm, "Delta": d, "CallPut": cp})
        for ttm, d, cp in product(std_ttms, np.sort(self._std_delta * -1), ["P"]):
            rows_vol.append({"TTM": ttm, "Delta": d, "CallPut": cp})
        df_vol = _to_dict_of_arrays(rows_vol)
        df_vol["YearFraction"] = np.zeros(len(rows_vol))
        for j in range(len(rows_vol)):
            ttm_val = df_vol["TTM"][j]
            try:
                idx = self._TTM_DAYS.index(int(ttm_val))
                df_vol["YearFraction"][j] = self._YEAR_FRACTIONS[idx]
            except (ValueError, IndexError):
                df_vol["YearFraction"][j] = ttm_val / 365.0

        out_iv = []
        out_disp = []
        for j in range(len(df_vol["TTM"])):
            iv, disp = self._aux_single_point(df_vol, df_raw, j)
            out_iv.append(iv)
            out_disp.append(disp)

        df_vol["ImpliedVol"] = np.array(out_iv)
        df_vol["Dispersion"] = np.array(out_disp)
        df_vol["Date"] = np.array([df_raw["Date"][0]] * len(out_iv))
        df_vol["Delta"] = np.round(df_vol["Delta"] * 100, 0)
        df_vol["Days"] = df_vol["TTM"].copy()
        df_vol["ExerciseStyle"] = np.array([str(df_raw["ExerciseStyle"][0])] * len(out_iv))
        df_vol["Spot"] = np.array([float(df_raw["Spot"][0])] * len(out_iv))
        return df_vol

    def generate_volatility_surface_point(
        self,
        raw_data: Dict[str, np.ndarray] | List[Dict[str, Any]],
        Type: str = "C",
        Days: int = 30,
        Delta: int = 20,
    ) -> float:
        """Interpola IV en un punto."""
        if isinstance(raw_data, list):
            raw_data = _to_dict_of_arrays(raw_data)
        mask = raw_data["Vega"] >= 0.5
        df_raw = {k: v[mask] for k, v in raw_data.items()}
        n = len(df_raw["TTM"])
        if n == 0:
            return np.nan

        num = 0.0
        denom = 0.0
        dnum = 0.0
        h1, h2, h3 = self.H1, self.H2, self.H3
        dj = Delta / 100.0 if Type == "C" else Delta / 100.0 + 1

        for i in range(n):
            ttm_i = float(df_raw["TTM"][i])
            x = np.log(ttm_i / Days)
            cp_i = df_raw["CallPut"][i]
            di = float(df_raw["Delta"][i])
            if cp_i == "C":
                z = 0 if Type == "C" else 1
            else:
                di = di + 1
                z = 1 if Type == "C" else 0
            y = di - dj
            phi = np.exp(-x * x / (2 * h1) - y * y / (2 * h2) - z * z / (2 * h3))
            vega_i = float(df_raw["Vega"][i])
            iv_i = float(df_raw["ImpliedVol"][i])
            num += vega_i * iv_i * phi
            dnum += vega_i * iv_i * iv_i * phi
            denom += vega_i * phi

        if denom <= 0:
            return np.nan
        return float(num / denom)


def _safe_float(x: Any, default: float | None = None) -> float | None:
    """Convierte a float de forma segura (CSV devuelve strings)."""
    if x is None or x == "":
        return default
    if isinstance(x, str) and x.strip().lower() in ("nan", "none", ""):
        return default
    try:
        f = float(x)
        return default if (isinstance(f, float) and np.isnan(f)) else f
    except (ValueError, TypeError):
        return default


def chain_to_raw_iv_data(
    chain_rows: List[Dict[str, Any]],
    spot: float,
    r: float,
    div: float,
    eval_date: str | None = None,
    price_source: str = "mid",
) -> Dict[str, np.ndarray]:
    """
    Convierte options chain (list[dict]) al formato esperado por gaussian_smooth.
    Cada dict debe tener: strike, type, expiration, bid, ask, lastPrice,
    impliedVolatility (opcional), Spot (opcional). Acepta valores string (CSV).
    """
    from datetime import datetime

    from Codigo.analytics.gregas_bs import delta_bs, vega_bs
    from Codigo.analytics.vol_implicita import impvolfunc_bs

    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if eval_date:
        try:
            now = datetime.strptime(str(eval_date)[:10], "%Y-%m-%d")
        except ValueError:
            pass

    def _find_col(candidates: List[str]) -> str | None:
        for c in candidates:
            if any(c in r for r in chain_rows):
                return c
        return None

    exp_col = _find_col(["expiration", "expirationDate"])
    type_col = _find_col(["type", "optionType"])
    strike_col = _find_col(["strike", "strikePrice"])
    iv_col = _find_col(["impliedVolatility", "implied volatility"])

    if not all([exp_col, type_col, strike_col]):
        raise ValueError("chain_rows debe tener expiration, type, strike")

    rows = []
    for row in chain_rows:
        try:
            exp_str = str(row.get(exp_col, ""))[:10]
            exp_dt = datetime.strptime(exp_str, "%Y-%m-%d")
            delta_days = (exp_dt - now).days
            if delta_days <= 0:
                continue
            TTM = delta_days
            YearFraction = TTM / 365.0

            tval = str(row.get(type_col, "")).lower()
            if "call" in tval or tval == "c":
                tipo = "C"
            elif "put" in tval or tval == "p":
                tipo = "P"
            else:
                continue

            K = _safe_float(row.get(strike_col))
            if K is None or K <= 0:
                continue
            S = _safe_float(row.get("Spot"), spot) or spot
            if S <= 0:
                S = spot

            if price_source == "mid":
                bid = _safe_float(row.get("bid"))
                ask = _safe_float(row.get("ask"))
                if bid is not None and ask is not None and bid > 0 and ask > 0:
                    OptionPrice = (bid + ask) / 2.0
                else:
                    OptionPrice = _safe_float(row.get("lastPrice") or row.get("last") or row.get("Last"))
                    if OptionPrice is None or OptionPrice <= 0:
                        continue
            else:
                OptionPrice = _safe_float(row.get("lastPrice") or row.get("last") or row.get("Last"))
                if OptionPrice is None or OptionPrice <= 0:
                    continue

            iv_val = _safe_float(row.get(iv_col)) if iv_col else None
            if iv_val is not None and iv_val > 0 and iv_val < 5:
                ImpliedVol = iv_val
            else:
                try:
                    ImpliedVol = impvolfunc_bs(tipo, S, K, YearFraction, r, OptionPrice, div)
                    if ImpliedVol is None or ImpliedVol <= 0 or ImpliedVol >= 5:
                        continue
                except Exception:
                    continue

            Delta = delta_bs(tipo, S, K, YearFraction, r, ImpliedVol, div)
            Vega = vega_bs(tipo, S, K, YearFraction, r, ImpliedVol, div)
            if Vega < 0:
                Vega = abs(Vega)

            rows.append({
                "Date": now.strftime("%Y-%m-%d"),
                "TTM": TTM,
                "YearFraction": YearFraction,
                "CallPut": tipo,
                "Strike": K,
                "ImpliedVol": ImpliedVol,
                "OptionPrice": OptionPrice,
                "Spot": S,
                "Vega": Vega,
                "Delta": Delta,
                "ExerciseStyle": "E",
            })
        except (ValueError, TypeError, KeyError):
            continue

    if not rows:
        raise ValueError("No se pudo generar ninguna fila de raw IV.")

    return _to_dict_of_arrays(rows)
