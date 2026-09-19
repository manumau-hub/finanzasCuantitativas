# -*- coding: utf-8 -*-
"""
Parser de texto OCR para capturas IBKR.

Modos:
- vanilla: 1 opción (layout distinto)
- estrategia: 2-4 legs, sección "Tramos de estrategia"

Vanilla - layout:
- Línea: "SPY MAR 20 '26 660 Put" → ticker, expiry, strike, tipo
- Last C4.18, Ask/Bid; ignorar plot hasta "Posición: -1 (-$404.32)", "Precio medio: 4.19"

Estrategia - layout:
- Tramos de estrategia: "Comprar/Vender TICKER MON DD 'YY STRIKE Call/Put", columna Último = precio
- Abajo: Posición N, Market value hoy X, Precio medio hoy Y
"""
import re

_MONTHS = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
    "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
}


def _parse_expiry(s: str) -> str:
    """JAN 15 '27 -> 2027-01-15"""
    s = s.strip().upper()
    m = re.search(r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s*(\d{1,2})\s*'?(\d{2})", s)
    if m:
        mon, day, yy = m.groups()
        year = "20" + yy if int(yy) < 50 else "19" + yy
        mm = _MONTHS.get(mon, "01")
        return f"{year}-{mm}-{int(day):02d}"
    return ""


def _extract_tramos_section(text: str) -> str:
    """Extrae la sección 'Tramos de estrategia' hasta 'Posición' o fin."""
    m = re.search(r"Tramos\s+de\s+estrategia", text, re.I)
    if not m:
        return ""
    start = m.start()
    # Cortar en "Posición" (bloque inferior)
    m2 = re.search(r"\bPosici[oó]n\b", text[start:], re.I)
    if m2:
        return text[start : start + m2.start()].strip()
    return text[start:].strip()


def _extract_posicion_section(text: str) -> str:
    """Extrae la sección desde 'Posición' hasta el final."""
    m = re.search(r"\bPosici[oó]n\b", text, re.I)
    if m:
        return text[m.start():].strip()
    return ""


def _parse_legs_estrategia(tramos_text: str) -> list[dict]:
    """
    Parsea cada leg de "Tramos de estrategia".
    - Columna Último (C7.48, C3.31, C0.00) = valor hoy, NO precio pagado.
    - Precio pagado = solo "Precio medio" del bloque inferior (estrategia conjunta).
    - CANT: número en segmento entre legs, o CANT. N.
    """
    leg_pattern = re.compile(
        r"\b(Comprar|Vender|Buy|Sell)\s+([A-Z]{2,5})\s+"
        r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{1,2})\s*'?(\d{2})\s+(\d+)\s+(Call|Put)",
        re.I
    )
    leg_matches = list(leg_pattern.finditer(tramos_text))
    legs = []
    for m in leg_matches:
        action = m.group(1).lower()
        ticker = m.group(2).upper()
        mon, day, yy = m.group(3), m.group(4), m.group(5)
        strike = int(m.group(6))
        opt_type = m.group(7).lower()
        expiry = _parse_expiry(f"{mon} {day} '{yy}")
        legs.append({
            "action": action,
            "ticker": ticker,
            "type": opt_type,
            "expiry": expiry,
            "strike": strike,
            "quantity": 1,
            "price_paid": 0.0,  # estrategia: solo Precio medio del bloque inferior
            "ultimo": None,     # C7.48, C3.31, etc. = valor hoy
        })

    # Último por leg: C7.48, C3.31, C0.00 (CO.00 = C0.00 si OCR lee O como 0)
    # Orden por posición en texto para asignar correctamente a cada leg
    ultimo_tuples: list[tuple[int, float]] = []
    for m in re.finditer(r"(?:C|P)(\d+[.,]\d{2})", tramos_text):
        try:
            ultimo_tuples.append((m.start(), float(m.group(1).replace(",", "."))))
        except ValueError:
            pass
    for m in re.finditer(r"(?:C|P)(?:O|0)\.(\d{2})", tramos_text):
        try:
            v = float("0." + m.group(1))
            # Evitar duplicar si ya hay un 0.0 cercano
            if not any(abs(v - x[1]) < 0.001 for x in ultimo_tuples):
                ultimo_tuples.append((m.start(), v))
        except ValueError:
            pass
    ultimo_tuples.sort(key=lambda t: t[0])
    ultimo_prices = [v for _, v in ultimo_tuples]
    if len(ultimo_prices) < len(legs):
        for m in re.finditer(r"\b(\d+[.,]\d{2})\b", tramos_text):
            if len(ultimo_prices) >= len(legs):
                break
            try:
                f = float(m.group(1).replace(",", "."))
                if 0.01 <= f <= 500 and f not in ultimo_prices:
                    ultimo_prices.append(f)
            except ValueError:
                pass

    for i, leg in enumerate(legs):
        if i < len(ultimo_prices):
            leg["ultimo"] = ultimo_prices[i]

    # CANT: buscar en el segmento tras cada leg (entre leg i y leg i+1). CANT suele ir tras el contrato.
    leg_matches = list(leg_pattern.finditer(tramos_text))
    for i in range(len(legs)):
        start = leg_matches[i].end() if i < len(leg_matches) else 0
        end = leg_matches[i + 1].start() if i + 1 < len(leg_matches) else len(tramos_text)
        segment = tramos_text[start:end]
        cant_m = re.search(r"(?:CANT\.?|Cant\.?)\s*:?\s*(\d+)", segment, re.I)
        if cant_m:
            legs[i]["quantity"] = min(20, max(1, int(cant_m.group(1))))
        else:
            # Evitar números de montos (4+815.71, 4h 18 m): solo 1-20 seguido de espacio o fin
            for m in re.finditer(r"\b([1-9]|1[0-9]|20)\b(?![\d.+])", segment):
                val = int(m.group(1))
                if 1 <= val <= 20:
                    legs[i]["quantity"] = val
                    break

    return legs[:4]


def _find_ticker_fallback(text: str) -> str:
    """Busca ticker conocido en el texto (fallback si el regex principal falla)."""
    known = ["SPY", "YPF", "TLT", "QQQ", "AAPL", "IWM", "DIA", "META", "GOOGL", "AMZN", "MSFT", "NVDA", "GLD"]
    text_upper = text.upper()
    for t in known:
        if re.search(r"\b" + t + r"\b", text_upper):
            return t
    m = re.search(r"\b([A-Z]{2,5})\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d", text_upper)
    return m.group(1) if m else ""


def _parse_vanilla(text: str) -> dict:
    """
    Parsea captura Vanilla (1 opción).
    Layout: "SPY MAR 20 '26 660 Put" ... ignorar hasta "Posición: -1 (-$404.32)" y "Precio medio: 4.19"
    """
    # Opción: TICKER MON DD 'YY STRIKE Call/Put (sin Comprar/Vender)
    opt_match = re.search(
        r"\b([A-Z]{2,5})\s+"
        r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{1,2})\s*'?(\d{2})\s+(\d+)\s+(Call|Put)\b",
        text, re.I
    )
    if not opt_match:
        ticker_fb = _find_ticker_fallback(text)
        return {"ticker": ticker_fb or "UNKNOWN", "legs": [], "posicion_info": {}}

    ticker = opt_match.group(1).upper()
    mon, day, yy = opt_match.group(2), opt_match.group(3), opt_match.group(4)
    strike = int(opt_match.group(5))
    opt_type = opt_match.group(6).lower()
    expiry = _parse_expiry(f"{mon} {day} '{yy}")

    # Sección Posición (ignorar plot del medio)
    posicion_text = _extract_posicion_section(text)
    posicion_info = _parse_posicion_block_vanilla(posicion_text)

    # Cantidad y signo: Posición -1 = short 1
    qty_raw = posicion_info.get("posicion")
    if qty_raw is None:
        qty_raw = 1
    qty = int(qty_raw)

    # Último: extraer LAST (C7.45) y bid+ask/2 — ambos están en el OCR
    pos_match = re.search(r"\bPosici[oó]n\b", text, re.I)
    section_end = pos_match.start() if pos_match else len(text)
    section = text[opt_match.end() : section_end]

    last_val = None
    m = re.search(r"(?:C|P)\s*(\d+[.,]\d{2})", section)
    if m:
        last_val = float(m.group(1).replace(",", "."))

    ask_val = None
    bid_val = None
    ask_m = re.search(r"(\d+[.,]\d{2})\s+Ask|Ask\s+[\dx\s]*(\d+[.,]\d{2})", section, re.I)
    if ask_m:
        g = (ask_m.group(1) or ask_m.group(2))
        if g:
            ask_val = float(g.replace(",", "."))
    bid_m = re.search(r"(\d+[.,]\d{2})\s+Bid|Bid\s+[\dx\s]*(\d+[.,]\d{2})", section, re.I)
    if bid_m:
        g = (bid_m.group(1) or bid_m.group(2))
        if g:
            bid_val = float(g.replace(",", "."))

    mid_val = (ask_val + bid_val) / 2 if (ask_val is not None and bid_val is not None) else None

    # Precio pagado: solo del bloque inferior (Precio medio). No usar Último como fallback.
    price_paid = posicion_info.get("precio_medio")
    price_paid = float(price_paid) if price_paid is not None else 0.0

    leg = {
        "action": "vender" if qty < 0 else "comprar",
        "type": opt_type,
        "expiry": expiry,
        "strike": strike,
        "quantity": qty,
        "price_paid": price_paid,
        "ultimo_last": last_val,
        "ultimo_mid": mid_val,
        "ultimo": last_val if last_val is not None else mid_val,
    }
    return {"ticker": ticker, "legs": [leg], "posicion_info": posicion_info}


def _parse_posicion_block_vanilla(posicion_text: str) -> dict:
    """Posición puede ser negativa: -1. Market value: (-$404.32)."""
    out = {"posicion": None, "market_value": None, "precio_medio": None}
    m = re.search(r"Posici[oó]n\s*:?\s*(-?\d+)", posicion_text, re.I)
    if m:
        out["posicion"] = int(m.group(1))
    # Market value: (-$404.32) o ($3,022) - entre paréntesis tras Posición
    m = re.search(r"\(\s*\$?\s*(-?[\d,]+\.?\d*)\s*\)", posicion_text)
    if m:
        try:
            out["market_value"] = float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    elif not out["market_value"]:
        # Fallback: $404.32 o -404.32 tras Posición
        m = re.search(r"Posici[oó]n\s*:?\s*-?\d+\s+[\(\$]?\s*(-?[\d,]+\.?\d*)", posicion_text, re.I)
        if m:
            try:
                out["market_value"] = float(m.group(1).replace(",", ""))
            except ValueError:
                pass
    m = re.search(r"Precio\s*medio\s*:?\s*(-?\d+[.,]\d{2})", posicion_text, re.I)
    if m:
        out["precio_medio"] = float(m.group(1).replace(",", "."))
    return out


def _parse_posicion_block(posicion_text: str) -> dict:
    """
    Extrae de la sección Posición:
    - Posición: 12
    - Market value hoy: 3022 (o $3,022)
    - Precio medio hoy: 2.95
    """
    out = {"posicion": None, "market_value": None, "precio_medio": None}
    m = re.search(r"Posici[oó]n\s*:?\s*(\d+)", posicion_text, re.I)
    if m:
        out["posicion"] = int(m.group(1))
    m = re.search(r"Market\s*value\s*(?:hoy)?\s*:?\s*[\(\$]?\s*(-?[\d,]+\.?\d*)", posicion_text, re.I)
    if m:
        try:
            out["market_value"] = float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    m = re.search(r"Precio\s*medio\s*(?:hoy)?\s*:?\s*(-?\d+[.,]\d{2})", posicion_text, re.I)
    if m:
        out["precio_medio"] = float(m.group(1).replace(",", "."))
    return out


def _skip_first_line(text: str) -> str:
    """Quita la primera línea (hora, batería del teléfono)."""
    lines = text.split("\n")
    if len(lines) > 1:
        return "\n".join(lines[1:])
    # Sin saltos: no cortar — el regex encuentra la opción en cualquier parte
    return text


def parse_ibkr_ocr(text: str, mode: str = "estrategia") -> dict:
    """
    Parsea texto OCR de captura IBKR.

    mode: "vanilla" (1 opción) | "estrategia" (2-4 legs)

    Retorna:
    - ticker, legs, posicion_info (posicion, market_value, precio_medio)
    - Para vanilla: por implementar (layout distinto)
    """
    text = _skip_first_line(text)
    text = text.replace("\n", " ").replace("  ", " ")

    if mode == "vanilla":
        return _parse_vanilla(text)

    # ESTRATEGIA
    tramos = _extract_tramos_section(text)
    posicion_text = _extract_posicion_section(text)
    posicion_info = _parse_posicion_block(posicion_text)

    legs = _parse_legs_estrategia(tramos)
    if not legs:
        return {"ticker": "UNKNOWN", "legs": [], "posicion_info": posicion_info}

    ticker = legs[0].get("ticker", "UNKNOWN")
    pos = posicion_info.get("posicion")
    # Solo escalar por Posición si todos los legs tienen qty 1 (ej. spread 1:1)
    all_qty_one = all(leg.get("quantity", 1) == 1 for leg in legs)
    for leg in legs:
        action = str(leg.get("action", "comprar")).lower()
        qty = leg.get("quantity", 1)
        if pos is not None and all_qty_one and qty == 1:
            qty = abs(pos)
        sign = 1 if "comprar" in action or "buy" in action else -1
        leg["quantity"] = sign * abs(qty)
        leg.pop("ticker", None)
    # Estrategia: precio_pagado por leg no existe; solo Precio medio estrategia (bloque inferior)

    return {"ticker": ticker, "legs": legs, "posicion_info": posicion_info}
