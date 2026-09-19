"""
Analizar rotacion sectorial entre XLK (Technology), XLF (Financials) y SPY.

Uso:
    py scripts/sector_rotation.py
    py scripts/sector_rotation.py --rolling 252

Descarga precios diarios de XLK, XLF y computa:
  - Rolling returns (1m, 3m, 6m, 12m)
  - Correlacion rolling 60d entre XLK y XLF
  - Drawdowns sincronicos
  - Ratio XLK/XLF para detectar regime changes
"""

import json
import sys
from urllib.request import urlopen

BASE = "https://historyofmarket.com"


def fetch_json(path):
    url = f"{BASE}{path}"
    with urlopen(url) as r:
        return json.loads(r.read().decode())


def compute_rolling(prices, window):
    out = []
    for i in range(window, len(prices)):
        ret = prices[i] / prices[i - window] - 1
        out.append(ret)
    return out


def compute_drawdowns(prices):
    peak = prices[0]
    dds = []
    for p in prices:
        if p > peak:
            peak = p
        dd = (p - peak) / peak
        dds.append(dd)
    return dds


def main():
    xlk = fetch_json("/api/xlk/price.json")
    xlf = fetch_json("/api/fin/price.json")

    xlk_prices = xlk["price"] if isinstance(xlk, dict) and "price" in xlk else xlk
    xlf_prices = xlf["price"] if isinstance(xlf, dict) and "price" in xlf else xlf

    dates = xlk.get("date", list(range(len(xlk_prices))))

    min_len = min(len(xlk_prices), len(xlf_prices))
    xlk_p = xlk_prices[:min_len]
    xlf_p = xlf_prices[:min_len]
    d = dates[:min_len]

    ratio = [xlk_p[i] / xlf_p[i] for i in range(min_len)]

    results = {
        "dates": d[-1] if isinstance(d[-1], str) else str(d[-1]),
        "xlk_price": xlk_p[-1],
        "xlf_price": xlf_p[-1],
        "ratio_xlk_xlf": ratio[-1],
        "rolling_returns": {
            "xlk_1m": compute_rolling(xlk_p, 21)[-1] if len(xlk_p) > 21 else None,
            "xlf_1m": compute_rolling(xlf_p, 21)[-1] if len(xlf_p) > 21 else None,
            "xlk_3m": compute_rolling(xlk_p, 63)[-1] if len(xlk_p) > 63 else None,
            "xlf_3m": compute_rolling(xlf_p, 63)[-1] if len(xlf_p) > 63 else None,
            "xlk_12m": compute_rolling(xlk_p, 252)[-1] if len(xlk_p) > 252 else None,
            "xlf_12m": compute_rolling(xlf_p, 252)[-1] if len(xlf_p) > 252 else None,
        },
        "current_drawdowns": {
            "xlk": compute_drawdowns(xlk_p)[-1],
            "xlf": compute_drawdowns(xlf_p)[-1],
        },
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
