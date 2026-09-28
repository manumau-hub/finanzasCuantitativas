# -*- coding: utf-8 -*-
"""
Visualización didáctica de árboles binomiales CRR (recombinantes).

Layout: eje X = tiempo (pasos), eje Y = nivel del nodo (más ups arriba).
Cada nodo muestra S y/o el valor de la opción V.
"""
from __future__ import annotations

import math
from typing import Literal, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch


def build_crr_lattices(
    tipo: Literal["C", "P"],
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    div: float,
    pasos: int,
    *,
    americana: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    """
    Construye matrices (pasos+1)×(pasos+1) de spot y valor de opción.

    Convención de índices (igual que el notebook 05a):
      - fila i = 0 es el camino con más subidas (S más alto)
      - columna t = tiempo (0 = hoy, pasos = vencimiento)
      - nodos válidos: fila i = 0 .. t en la columna t

    Retorna
    -------
    S_lat, V_lat : ndarray
        NaN fuera del triángulo del árbol.
    meta : dict
        u, d, q, dt, descuento, exercise_lat (bool, nodos con early exercise), etc.
    """
    if pasos < 1:
        raise ValueError("pasos debe ser >= 1")
    tipo = tipo.upper()
    if tipo not in ("C", "P"):
        raise ValueError("tipo debe ser 'C' o 'P'")

    dt = T / pasos
    fwd = math.exp((r - div) * dt)
    desc = math.exp(-r * dt)
    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    q = (fwd - d) / (u - d)
    if not (0.0 < q < 1.0):
        raise ValueError(f"q={q:.4f} fuera de (0,1); revisá parámetros/pasos")

    n = pasos + 1
    S_lat = np.full((n, n), np.nan)
    V_lat = np.full((n, n), np.nan)
    # True = en ese nodo conviene ejercer (solo nodos interiores si americana)
    exercise_lat = np.full((n, n), False, dtype=bool)

    # Spots en cada nodo (i downs from the top path at time t)
    for t in range(n):
        for i in range(t + 1):
            # i=0 → t ups; i=t → t downs
            S_lat[i, t] = S * (u ** (t - i)) * (d ** i)

    # Payoff al vencimiento
    for i in range(n):
        if tipo == "C":
            V_lat[i, pasos] = max(S_lat[i, pasos] - K, 0.0)
        else:
            V_lat[i, pasos] = max(K - S_lat[i, pasos], 0.0)

    # Retropropagación (misma convención que opcion_americana_bin:
    # V = e^{-rΔt} * max(hold, intrinsic))
    for j in range(1, n):
        t = pasos - j
        for i in range(t + 1):
            hold = q * V_lat[i, t + 1] + (1.0 - q) * V_lat[i + 1, t + 1]
            if americana:
                spot = S_lat[i, t]
                if tipo == "C":
                    exercise = max(spot - K, 0.0)
                else:
                    exercise = max(K - spot, 0.0)
                if exercise > hold:
                    exercise_lat[i, t] = True
                    V_lat[i, t] = desc * exercise
                else:
                    V_lat[i, t] = desc * hold
            else:
                V_lat[i, t] = desc * hold

    meta = {
        "u": u,
        "d": d,
        "q": q,
        "dt": dt,
        "descuento": desc,
        "tipo": tipo,
        "americana": americana,
        "S0": S,
        "K": K,
        "pasos": pasos,
        "exercise_lat": exercise_lat,
        "n_ejercer": int(exercise_lat.sum()),
    }
    return S_lat, V_lat, meta


def _node_xy(t: int, i: int, pasos: int) -> Tuple[float, float]:
    """Coordenadas: x=tiempo, y=nivel (ups arriba)."""
    # En t hay (t+1) nodos; i=0 arriba → y = (t/2 - i)
    y = (t / 2.0) - i
    # Escalamos un poco en Y para N grandes
    return float(t), float(y)


def plot_binomial_tree(
    S_lat: np.ndarray,
    V_lat: Optional[np.ndarray] = None,
    *,
    meta: Optional[dict] = None,
    show: Literal["both", "S", "V"] = "both",
    ax=None,
    title: Optional[str] = None,
    node_size: float = 0.35,
    fontsize: int = 8,
    connect: bool = True,
    highlight_root: bool = True,
):
    """
    Dibuja el árbol recombinante.

    Parámetros
    ----------
    S_lat, V_lat : matrices del árbol (ver ``build_crr_lattices``).
    show : qué etiquetar en cada nodo — ``both`` (S y V), solo ``S`` o solo ``V``.
    """
    pasos = S_lat.shape[1] - 1
    if ax is None:
        # Ancho crece con N; alto también
        w = max(7.0, 1.6 * (pasos + 1))
        h = max(4.0, 0.9 * (pasos + 1))
        fig, ax = plt.subplots(figsize=(w, h), dpi=120)
    else:
        fig = ax.figure

    # Aristas primero (debajo de los nodos)
    if connect:
        for t in range(pasos):
            for i in range(t + 1):
                x0, y0 = _node_xy(t, i, pasos)
                for di, color, style in ((0, "#2ca02c", "-"), (1, "#d62728", "-")):
                    x1, y1 = _node_xy(t + 1, i + di, pasos)
                    ax.plot([x0, x1], [y0, y1], color=color, lw=1.2, alpha=0.55, zorder=1)
                    # pequeña etiqueta u/d en el primer paso
                    if t == 0 and pasos <= 6:
                        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
                        ax.text(
                            xm, ym + 0.08,
                            "u" if di == 0 else "d",
                            color=color, fontsize=7, ha="center", va="bottom", alpha=0.8,
                        )

    exercise_lat = None
    if meta is not None:
        exercise_lat = meta.get("exercise_lat")

    # Nodos
    for t in range(pasos + 1):
        for i in range(t + 1):
            x, y = _node_xy(t, i, pasos)
            s_val = S_lat[i, t]
            v_val = None if V_lat is None else V_lat[i, t]
            ejercemos = bool(
                exercise_lat is not None
                and exercise_lat.shape == S_lat.shape
                and exercise_lat[i, t]
            )

            is_root = highlight_root and t == 0 and i == 0
            if ejercemos:
                # Región de ejercicio temprano (diferencia clave vs europea)
                face = "#f8d7da"
                edge = "#c0392b"
                lw = 2.0
            elif is_root:
                face = "#fff3cd"
                edge = "#e67e22"
                lw = 2.0
            else:
                face = "white"
                edge = "#333333"
                lw = 1.2

            box_h = node_size * (1.15 if ejercemos and show == "both" else 0.9)
            box = FancyBboxPatch(
                (x - node_size * 0.55, y - box_h * 0.5),
                node_size * 1.1,
                box_h,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=face,
                edgecolor=edge,
                linewidth=lw,
                zorder=2,
            )
            ax.add_patch(box)

            lines = []
            if show in ("both", "S") and np.isfinite(s_val):
                lines.append(f"S={s_val:.2f}")
            if show in ("both", "V") and v_val is not None and np.isfinite(v_val):
                lines.append(f"V={v_val:.2f}")
            if ejercemos:
                lines.append("EJERCER")
            label = "\n".join(lines) if lines else ""
            ax.text(
                x, y, label,
                ha="center", va="center",
                fontsize=fontsize - 1 if ejercemos else fontsize,
                fontweight="bold" if ejercemos else "normal",
                color="#922b21" if ejercemos else "black",
                zorder=3,
            )

    ax.set_xlim(-0.6, pasos + 0.6)
    # márgenes verticales
    ys = [_node_xy(t, i, pasos)[1] for t in range(pasos + 1) for i in range(t + 1)]
    pad = 0.6
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_xlabel("Tiempo (pasos)", fontsize=10)
    ax.set_ylabel("Nivel del nodo (más ups ↑)", fontsize=10)
    ax.set_xticks(range(pasos + 1))
    ax.set_yticks([])
    ax.grid(True, axis="x", alpha=0.25)

    if title is None and meta:
        kind = "americana" if meta.get("americana") else "europea"
        title = (
            f"Árbol CRR {kind} · {meta.get('tipo')} · N={meta.get('pasos')}  "
            f"(u={meta['u']:.4f}, d={meta['d']:.4f}, q={meta['q']:.4f})"
        )
    if title:
        ax.set_title(title, fontsize=11)
    if meta:
        ax.text(
            0.01, 0.01,
            f"S0={meta.get('S0')}  K={meta.get('K')}  →  V0={V_lat[0, 0]:.4f}"
            if V_lat is not None else f"S0={meta.get('S0')}",
            transform=ax.transAxes, fontsize=8, color="#444",
        )
    # leyenda colores
    ax.plot([], [], color="#2ca02c", lw=2, label="rama up (u)")
    ax.plot([], [], color="#d62728", lw=2, label="rama down (d)")
    if exercise_lat is not None and np.any(exercise_lat):
        ax.scatter(
            [], [], s=80, c="#f8d7da", edgecolors="#c0392b", linewidths=1.5,
            label="ejercer temprano (max = intrinsic)",
        )
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)

    plt.tight_layout()
    return fig, ax


def plot_crr_tree(
    tipo: Literal["C", "P"],
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    div: float,
    pasos: int,
    *,
    americana: bool = False,
    show: Literal["both", "S", "V"] = "both",
    ax=None,
    title: Optional[str] = None,
):
    """Atajo: construye lattices CRR y plotea el árbol."""
    S_lat, V_lat, meta = build_crr_lattices(
        tipo, S, K, T, r, sigma, div, pasos, americana=americana,
    )
    return plot_binomial_tree(
        S_lat, V_lat, meta=meta, show=show, ax=ax, title=title,
    )
