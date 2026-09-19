# Spec: Market Data Toolkit (librería genérica, desde cero)

Documento **autocontenido** para implementar un toolkit de market data usable por cualquier aplicación (CLI, API, notebooks, web apps). No asume acceso a ningún repositorio previo.

**Alcance de esta entrega:** dos módulos.

| Módulo | Código | Descripción |
|--------|--------|-------------|
| **US Equities & Options** | `core` | Spot, quote, cadena de opciones, r, div, IV ATM |
| **BYMA (Argentina)** | `byma` | Paneles, históricos OHLCV, índices, opciones AR, bonos |

Implementar **ambos**. Si el consumidor no usa BYMA, igual debe estar disponible como subpaquete importable.

Reglas globales:

- Librería pura (sin Streamlit / Flask / UI).
- Contrato estable (firmas + schemas de este doc).
- Exponer `source` cuando haya fallback.
- Tasas y volatilidades en **decimal** (0.04 = 4%), salvo donde se indique lo contrario.

---

# Stack Python (obligatorio + opciones)

## Instalación recomendada

```text
pip install requests pandas numpy yahooquery yfinance scipy
```

| Paquete | Versión guía | Uso |
|---------|--------------|-----|
| `requests` | ≥ 2.28 | HTTP a stockprices.dev, Yahoo Chart, BYMA |
| `pandas` | ≥ 2.0 | Options chain / paneles / históricos |
| `numpy` | ≥ 1.24 | Solver IV (bisección / arrays) |
| `yahooquery` | ≥ 2.3 | Spot, quote, option chain (primario US) |
| `yfinance` | ≥ 0.2.28 | Fallback US + dividendYield |
| `scipy` | ≥ 1.10 | Opcional: `brentq` para IV; si no, bisección propia con numpy |

**No** requerir: streamlit, plotly, easyocr, pillow, jupyter, beautifulsoup (salvo que se agregue un scraper legacy aparte; BYMA va por API JSON).

## Imports canónicos (usar estos)

```python
from __future__ import annotations

import re
from datetime import datetime
from typing import Callable, Optional, Tuple
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests

# Providers US (lazy import dentro de cada provider está OK para arranque rápido)
from yahooquery import Ticker as YQTicker
import yfinance as yf
```

Solver IV (elegir **una** implementación; preferida A):

```python
# Opción A (preferida): bisección propia, solo numpy
# Opción B: from scipy.optimize import brentq
```

BYMA:

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# requests.get/post(..., verify=False)  # ver sección BYMA / SSL
```

## Extras de empaquetado (recomendado)

```text
# pyproject.toml / setup.cfg extras
[project.optional-dependencies]
dev = ["pytest>=7", "pytest-mock>=3"]
```

API de superficie del paquete:

```python
# market_data/__init__.py — reexportar core (+ byma namespace)
from market_data.core import (
    get_spot,
    get_spot_with_source,
    get_quote,
    get_expirations,
    get_options_chain,
    get_options_chain_yfinance,
    get_dividend_yield,
    get_risk_free_rate,
    get_risk_free_rate_with_source,
    get_implied_vol_atm_with_source,
    calc_implied_vol_atm_with_source,
)
from market_data import byma  # byma.get_panel, byma.get_historical, ...
```

---

# MÓDULO `core` — US Equities & Options

## 1. Objetivo

1. Spot / quote de acciones y ETFs US.  
2. Cadena de opciones (calls + puts) por vencimiento.  
3. Parámetros de pricing: `r`, `div`, σ ATM.  
4. Fallback multi-proveedor.

**Fuera de alcance:** pricing de estrategias, superficies 3D, UI, brokers, OCR.

## 2. Principios

| Principio | Requisito |
|-----------|-----------|
| Sin UI | Solo funciones/clases |
| Solver IV inyectable | `iv_solver` opcional; default incluido en el paquete |
| Fuente trazable | `(value, source)` preferido |
| Decimales | Normalizar % → decimal |
| Timeouts | HTTP 10 s (15 s para tasas) |
| User-Agent | UA de navegador en requests |
| Pandas | Chain como `DataFrame` con columnas canónicas |

## 3. API pública

### 3.1 Spot

```text
get_spot(ticker: str) -> float
get_spot_with_source(ticker: str) -> tuple[float, str]
```

**Fallback (orden fijo):**

1. stockprices.dev  
2. Yahoo Chart API HTTP (`v8/finance/chart`)  
3. yahooquery  
4. yfinance  

Si todos fallan → `ValueError` con errores por proveedor.

### 3.2 Quote

```text
get_quote(ticker: str) -> dict
```

| Clave | Tipo | Notas |
|-------|------|--------|
| `last` | float \| None | Precio |
| `change` | float \| None | Variación absoluta 1d |
| `changePercent` | float \| None | **Porcentaje** (1.25 = +1.25%) |
| `name` | str \| None | Nombre corto |
| `source` | str \| None | Proveedor |
| `bid` / `ask` / `volume` | opcional | |

Fallback: stockprices.dev → yahooquery. Sin datos: dict con `None`s (no excepción).

### 3.3 Expirations

```text
get_expirations(ticker: str) -> list[str]   # YYYY-MM-DD ordenadas
```

Fallback: yahooquery → yfinance. Sin datos: `[]`.

### 3.4 Options chain

```text
get_options_chain(ticker: str, expiration: str | None = None) -> pd.DataFrame
get_options_chain_yfinance(ticker: str, max_expirations: int | None = None) -> pd.DataFrame
```

| Columna | Obligatorio |
|---------|-------------|
| `strike` | sí |
| `type` (`"call"` \| `"put"`) | sí |
| `expiration` (`YYYY-MM-DD`) | sí |
| `bid`, `ask`, `lastPrice` | recomendado |
| `impliedVolatility` | recomendado |
| `volume`, `openInterest` | opcional |
| `Spot`, `Ticker` | sí |

Aliases a normalizar: `strikePrice`→`strike`, `optionType`→`type` (`calls`/`puts`→`call`/`put`), `expirationDate`→`expiration`.

- `expiration=None` → todas las expiries (o documentar tope).  
- `get_options_chain_yfinance`: solo yfinance (útil si yahooquery falla en serialización).

### 3.5 Dividend yield

```text
get_dividend_yield(ticker: str) -> float   # decimal; 0.0 si no hay datos
```

Fuente: `yf.Ticker(ticker).info` → `dividendYield` / `yield`. Si valor > 1 → `/100`.

### 3.6 Risk-free rate

```text
get_risk_free_rate() -> float
get_risk_free_rate_with_source() -> tuple[float, str]
```

- Símbolos: `^IRX` primero, luego `^TNX`.  
- Método: Yahoo Chart → yfinance.  
- % → decimal si valor > 1.  
- Fallback final: `(0.05, "fallback")`.

### 3.7 Vol implícita ATM

```text
get_implied_vol_atm_with_source(chain_df, spot, expiry) -> tuple[float, str] | None
calc_implied_vol_atm_with_source(
    chain_df, spot, expiry, r, div,
    price_source: str = "mid",          # "mid" | "last"
    iv_solver: Callable | None = None,
) -> tuple[float, str] | None
```

**get_implied_\***: columna `impliedVolatility`; strike más cercano a spot; call luego put; IV>1 → `/100`. Fuente ejemplo: `"IV Yahoo ATM"`.

**calc_implied_\***:

- `mid` = (bid+ask)/2 (ambos > 0); `last` = lastPrice  
- `T = max(días_hasta_expiry, 1) / 365`  
- Solver: `(tipo, S, K, T, r, precio, div) -> float` con `tipo in {"C","P"}`  
- Aceptar solo `0 < iv < 5`  
- Default solver: BS + bisección (numpy); **opción B**: `scipy.optimize.brentq`

## 4. Endpoints HTTP — `core`

```http
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

### 4.1 stockprices.dev

```http
GET https://stockprices.dev/api/stocks/{TICKER}
GET https://stockprices.dev/api/etfs/{TICKER}
```

Campos: `Price`, `ChangeAmount`, `ChangePercentage`, `Name`.

### 4.2 Yahoo Chart (sin crumb)

```http
GET https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?range=5d&interval=1d
```

- Spot: último `close` no-null.  
- Risk-free: `%5EIRX` / `%5ETNX`.  
- Host alt: `query2.finance.yahoo.com`.

### 4.3 yahooquery / yfinance

Primario / fallback para spot, quote y options.

### 4.4 Yahoo con crumb (opción de implementación, no requerida)

| Endpoint | Auth | Uso |
|----------|------|-----|
| `/v7/finance/quote` | crumb | quotes batch |
| `/v7/finance/options/{symbol}` | crumb | options sin wrapper |
| `/v10/finance/quoteSummary/{symbol}` | crumb | fundamentals |

Crumb: cookie de sesión + `GET /v1/test/getcrumb`. La entrega mínima **no** depende de crumb.

## 5. Layout del paquete

```text
market_data/
  __init__.py
  exceptions.py          # MarketDataError, NoDataError
  schemas.py             # columnas canónicas, TypedDicts
  core/
    __init__.py
    spot.py
    quote.py
    options.py
    rates.py
    implied_vol.py
    bs_iv.py             # solver default
    providers/
      stockprices.py
      yahoo_chart.py
      yahooquery_provider.py
      yfinance_provider.py
  byma/
    __init__.py
    client.py
    panels.py
    historical.py
    bonds.py
```

Alternativa válida v1: un solo `core.py` flat + `byma.py`, siempre que se respete el contrato.

## 6. Edge cases — `core`

1. Ticker → upper.  
2. Expiry: comparar `str(expiry)[:10]`.  
3. IV NaN en ATM call → put / strikes vecinos.  
4. Sin bid/ask → no inventar mid.  
5. Backoff ante rate-limit Yahoo.  
6. Preferir `(value, source)` a estado global mutable.

## 7. Tests de aceptación — `core`

```python
assert get_spot("AAPL") > 0
q = get_quote("AAPL"); assert q["last"] is not None
exps = get_expirations("AAPL"); assert len(exps) > 0
chain = get_options_chain("AAPL", exps[0])
assert {"strike", "type", "expiration", "Spot", "Ticker"} <= set(chain.columns)
r, _ = get_risk_free_rate_with_source(); assert 0 < r < 1
assert get_dividend_yield("AAPL") >= 0
```

Unit tests con HTTP mockeado; live = integration.

## 8. Ejemplo de consumo

```python
from market_data import (
    get_spot,
    get_options_chain,
    get_dividend_yield,
    get_risk_free_rate_with_source,
    calc_implied_vol_atm_with_source,
)

S = get_spot("MSFT")
chain = get_options_chain("MSFT", None)
r, _ = get_risk_free_rate_with_source()
div = get_dividend_yield("MSFT")
expiry = sorted(chain["expiration"].unique())[0]
sigma, src = calc_implied_vol_atm_with_source(chain, S, expiry, r, div, "mid")
```

---

# MÓDULO `byma` — Argentina

## B1. Objetivo

Cliente de la **API pública** de BYMA: paneles delayed (~15 min), históricos OHLCV, índices, ficha de bonos. Sin API key.

## B2. Base URL y headers

```text
BASE = https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free
```

```http
Content-Type: application/json
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

**SSL:** validación de certificado suele fallar con `certifi`. Usar `verify=False` (TLS activo, sin verify de cadena). Deshabilitar warnings de urllib3 y documentarlo en el README.

**Rate limit:** ≤ 1 req/s. Endpoints públicos no oficiales — pueden cambiar.

## B3. Endpoints

### Paneles (POST JSON)

| Path | Contenido |
|------|-----------|
| `/leading-equity` | Top ~20 MERVAL × settlements |
| `/cedears` | CEDEARs |
| `/public-bonds` | Bonos + LECAP/BONCAP (paginado) |
| `/negociable-obligations` | ONs |
| `/cauciones` | Cauciones |
| `/senebi-obligaciones-negociables` | SENEBI ONs |
| `/options` | Opciones AR |

Body típico:

```json
{
  "excludeZeroPxAndQty": true,
  "T0": false,
  "T1": true,
  "T2": false,
  "page_size": 5000
}
```

- `T0` → CI (`settlementType=1`); `T1` → 24hs (`settlementType=2`).  
- `page` suele ignorarse; usar `page_size` grande.  
- Normalizar respuestas `{content, data[]}` o lista directa → `list[dict]` o `DataFrame`.

### Históricos (GET)

```http
GET {BASE}/chart/historical-series/history?symbol={SYM}&resolution=D&from={unix}&to={unix}
```

- Símbolo **con** sufijo ` 24HS` (espacio). Ej: `GGAL 24HS`, `AL30D 24HS`.  
- Resolutions: `D` | `W` | `M`.  
- Sin sufijo → HTTP 400.

### Índices (GET)

```http
GET {BASE}/chart/index-historical-series/history?symbol={COD}&...
```

| Código | Índice |
|--------|--------|
| `M` | S&P MERVAL |
| `G` | BURCAP |

### Ficha de bonos (POST)

```http
POST {BASE}/bnown/fichatecnica/especies/general
```

Body con ticker de especie (`AL30`, `AE38`, `TY30P`, …).

## B4. API pública

```text
byma.get_panel(name: str, **filters) -> pd.DataFrame
byma.get_historical(symbol_24hs: str, desde=None, hasta=None, resolution="D") -> pd.DataFrame
byma.get_index(code: str, ...) -> pd.DataFrame       # "M" | "G"
byma.get_bond_info(ticker: str) -> dict
byma.get_options_panel(**filters) -> pd.DataFrame
```

Nombres de panel: `leading-equity`, `cedears`, `public-bonds`, `on`, `cauciones`, `senebi-on`, `options`.

Mapear alias `on` → path `/negociable-obligations`, `senebi-on` → `/senebi-obligaciones-negociables`.

## B5. Campos comunes en paneles

| Campo | Descripción |
|-------|-------------|
| `symbol` | Ticker BYMA |
| `settlementType` | `"1"` CI / `"2"` 24hs |
| `securityType` | `CS`, `CD`, `GO`, `CORP`, `QS`, `OPT`, … |
| `denominationCcy` | `ARS`, `USD`, `EXT` |
| `trade`, `closingPrice`, `bidPrice`, `offerPrice` | Precios |
| `imbalance` | Variación (a menudo decimal) |
| `volume`, `volumeAmount`, `vwap` | Volúmenes |
| `maturityDate`, `underlyingSymbol`, `strikePrice` | Opciones/bonos/cauciones |
| `openInterest` | Opciones / cauciones |

## B6. Convenciones de símbolos

| Tipo | Ejemplo histórico |
|------|-------------------|
| Acción | `GGAL 24HS` |
| CEDEAR ARS / USD | `AAPL 24HS` / `AAPLD 24HS` |
| Bono ARS / MEP / CCL | `AL30 24HS` / `AL30D 24HS` / `AL30C 24HS` |

Sufijos spot: sin sufijo = ARS; `D` = USD MEP; `C` = CCL.

## B7. Dependencias — `byma`

Solo `requests`, `pandas` (+ `urllib3` vía requests). Sin yahooquery.

## B8. Tests — `byma`

```python
from market_data import byma

panel = byma.get_panel("leading-equity", T1=True)
assert len(panel) > 0
assert "symbol" in panel.columns
hist = byma.get_historical("GGAL 24HS")
assert len(hist) > 0
```

---

# Entregables

1. Paquete Python con `core` + `byma`.  
2. `README`: install, ejemplos US y BYMA, nota SSL BYMA, rate limits.  
3. `requirements.txt` / `pyproject.toml` con las deps de la sección Stack.  
4. Tests unitarios (mock) + smoke integration documentados.  
5. Advertencia: Yahoo/BYMA no oficiales; datos delayed; respetar rate limits.

---

# Opciones de diseño (cerradas — elegir y documentar en README)

| Tema | Default de esta spec | Alternativa aceptable |
|------|----------------------|------------------------|
| Shape API | Funciones flat + `byma.*` | Clase `MarketDataClient` que wrappea lo mismo |
| Solver IV | Bisección numpy en `bs_iv.py` | `scipy.optimize.brentq` |
| Yahoo options | yahooquery primario, yfinance fallback | Solo yfinance vía `get_options_chain_yfinance` |
| Retorno con fuente | `*_with_source` → `tuple` | Siempre tuple; wrappers sin source llaman al with_source |
| BYMA output | `DataFrame` | `list[dict]` + helper `to_frame()` |
| HTTP Yahoo extra | No crumb | Crumb + `/v7/finance/options` como provider adicional |
