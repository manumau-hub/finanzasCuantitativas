---
name: morningstar
description: "Morningstar Screener via API JSON publica: descarga masiva de 53 universes (102K+ listings, 39 paises, NYSE/Nasdaq/BCBA/etc) con 33 campos (precio, market cap, ratios, retornos 1d/1w/1m/3m/6m/12m/36m/60m/120m, deuda, dividend yield, sector, industria). Sin API key, sin auth."
license: MIT
---

# Morningstar — Screener via API JSON

Skill para descargar la base de datos de acciones globales de [Morningstar](https://www.morningstar.com) usando un endpoint JSON interno descubierto por ingenieria inversa. Sin API key, sin autenticacion, sin rate limit agresivo.

---

## ⚠️ Aviso Legal

- Este endpoint **no es oficial** — fue descubierto interceptando el trafico XHR de la UI web del screener de Morningstar.
- Los datos provienen del sitio publico de Morningstar. Respetar los **terminos de servicio** del sitio.
- **Solo el endpoint `/security/screener` es accesible** sin auth. Otros endpoints de Morningstar (api-global, global, lt, etc.) requieren resolver AWS WAF challenge (no soportado por este skill).
- Para uso intensivo, respetar pausas de 0.5-1 segundo entre requests.

---

## Scripts

| Script | Descripcion |
|--------|-------------|
| **[fetch_morningstar.py](./scripts/fetch_morningstar.py)** | Script principal: info, fields, search, screener, download |

---

## Instalacion de dependencias

```bash
pip install requests
```

> Solo `requests` puro, sin dependencias extras.

---

## Uso rapido

```bash
# === INFO ===
python scripts/fetch_morningstar.py info       # Stats del skill
python scripts/fetch_morningstar.py fields     # 33 campos disponibles

# === BUSCAR TICKERS (por nombre, multi-universe) ===
python scripts/fetch_morningstar.py search Apple --universe XNAS
python scripts/fetch_morningstar.py search Apple --universe XNAS XFRA XBUE
python scripts/fetch_morningstar.py search YPF --universe XBUE
python scripts/fetch_morningstar.py search "MercadoLibre" --universe XNAS BVMF

# === DESCARGA MASIVA (screener) ===
python scripts/fetch_morningstar.py screener --universe XNAS
python scripts/fetch_morningstar.py screener --universe XBUE
python scripts/fetch_morningstar.py screener --universe XNAS XLON XTKS

# === DESCARGA POR PAIS ===
python scripts/fetch_morningstar.py screener --country AR
python scripts/fetch_morningstar.py screener --country US
python scripts/fetch_morningstar.py screener --country DE

# === DESCARGA COMPLETA (53 universes, 100K+ listings) ===
python scripts/fetch_morningstar.py screener --all

# === GUARDAR A ARCHIVO ===
python scripts/fetch_morningstar.py screener --universe XBUE -o argentina.json
python scripts/fetch_morningstar.py screener --universe XNAS -o nasdaq.csv
python scripts/fetch_morningstar.py screener --country AR -o ar.csv
python scripts/fetch_morningstar.py search "YPF" --universe XBUE -o ypf_results.json

# === DOWNLOAD (alias de screener) ===
python scripts/fetch_morningstar.py download --universe XBUE -o ar.csv

# === MODO SILENCIOSO (solo JSON, sin logs) ===
python scripts/fetch_morningstar.py search Apple --universe XNAS -q
python scripts/fetch_morningstar.py screener --universe XBUE -q -o ar.json

# === CAMPOS ESPECIFICOS (--fields) ===
python scripts/fetch_morningstar.py screener --universe XNAS --fields Ticker Name ClosePrice MarketCap PERatio
```

---

## Modos disponibles

| Modo | Descripcion | Ejemplo |
|------|-------------|---------|
| `info` | Stats del skill, dominios, token, #universes, #campos | `python fetch_morningstar.py info` |
| `fields` | Lista los 33 securityDataPoints disponibles con descripcion | `python fetch_morningstar.py fields` |
| `search` | Buscar tickers por nombre en uno o varios universes | `python fetch_morningstar.py search Apple --universe XNAS` |
| `screener` | Descarga masiva de uno o varios universes (toda la DB) | `python fetch_morningstar.py screener --universe XNAS` |
| `download` | Alias de `screener` | `python fetch_morningstar.py download --universe XNAS` |

### Flags

| Flag | Descripcion | Ejemplo |
|------|-------------|---------|
| `--universe XNAS` | Uno o varios universe codes (sin prefijo `E0EXG$`) | `--universe XNAS XBUE` |
| `--country AR` | Codigos de pais ISO (39 paises soportados) | `--country AR US DE` |
| `--all` | Todos los 53 universes (~100K listings, demora ~1-2 min) | `--all` |
| `--fields Ticker Name` | Sub-set de campos (default: los 33) | `--fields Ticker Name ClosePrice` |
| `--output archivo.json` | Guardar a JSON | `-o data.json` |
| `--output archivo.csv` | Guardar a CSV (flat) | `-o data.csv` |
| `-q` / `--quiet` | Solo JSON, sin logs | `-q` |

---

## Cobertura

**53 universes, 102,093 listings, 39 paises** — ver [assets/UNIVERSES.md](./assets/UNIVERSES.md).

### Top 10 universes

| Universe | Exchange | Pais | Listings |
|----------|----------|------|----------|
| `XFRA` | Frankfurt (Tradegate) | Germany | 14,082 |
| `XSTU` | Stuttgart | Germany | 9,971 |
| `XMUN` | Munich | Germany | 8,425 |
| `XDUS` | Dusseldorf | Germany | 8,297 |
| `XBOM` | Bombay (BSE) | India | 5,192 |
| `XTKS` | Tokyo | Japan | 3,989 |
| `XNAS` | Nasdaq | United States | 3,741 |
| `XNSE` | NSE India | India | 3,018 |
| `XSHE` | Shenzhen | China | 2,934 |
| `XKRX` | Korea Exchange | South Korea | 2,877 |

### Argentina

`XBUE` (BCBA) → **469 CEDEARs** (certificados de deposito de acciones extranjeras) con precios en ARS.

```bash
python fetch_morningstar.py screener --universe XBUE -o ar.csv
```

> Cada CEDEAR tiene un `PerformanceId` distinto del ADR original. Ej: Apple Inc CEDEAR (`0P0000TFNY`) ≠ Apple Inc NASDAQ (`0P000000GY`).

### Brasil

`BVMF` (B3) → **2,070 BDRs/acciones** en BRL.

### Mexico

`XMEX` (BMV) → **2,233 acciones** en MXN.

---

## Campos (33 en total)

**5 metadata:** `Ticker`, `Name`, `PerformanceId`, `Universe`, `MarketCountryName`

**5 categoricos:** `SectorName`, `IndustryName`, `EquityStyleBox` (1-9), `QuantitativeStarRating` (1-5)

**23 numericos:**
- **Precio/tamano (2):** `ClosePrice`, `MarketCap`
- **Valuacion (3):** `PERatio`, `PEGRatio`, `DividendYield`
- **Calidad (7):** `DebtEquityRatio`, `NetMargin`, `EBTMarginYear1`, `ROATTM`, `ROETTM`, `ROEYear1`, `ROICYear1`
- **Crecimiento (2):** `EPSGrowth3YYear1`, `RevenueGrowth3Y`
- **Retornos (9):** `ReturnD1`, `ReturnW1`, `ReturnM0`, `ReturnM1`, `ReturnM3`, `ReturnM6`, `ReturnM12`, `ReturnM36`, `ReturnM60`, `ReturnM120`

Ver [assets/DATA_POINTS.md](./assets/DATA_POINTS.md) para detalles.

---

## Ejemplos de output

### `search Apple --universe XNAS` (1 resultado)

```json
{
  "_meta": {
    "query": "Apple",
    "universe_count": 1,
    "total_results": 1
  },
  "results": [
    {
      "Ticker": "AAPL",
      "PerformanceId": "0P000000GY",
      "Name": "Apple Inc",
      "ClosePrice": 311.23,
      "MarketCap": 4571145807880,
      "MarketCountryName": "United States",
      "SectorName": "Technology",
      "IndustryName": "Consumer Electronics",
      "_universe_code": "XNAS",
      "_universe_name": "Nasdaq"
    }
  ]
}
```

### `screener --universe XBUE -o ar.csv` (469 filas)

```csv
_universe_code,Ticker,Name,PerformanceId,Universe,ClosePrice,MarketCap,SectorName,IndustryName,EquityStyleBox,...
XBUE,MMM,3M Co Cedear,0P0000D5UB,E0EXG$XBUE,23100,Industrials,Conglomerates,4,...
XBUE,A3,A3 Mercados SA Ordinary Shares,0P0000WJD7,E0EXG$XBUE,2215,Financial Services,Financial Data & Stock Exchanges,,...
XBUE,YPFD,YPF SA Class D,0P0000BS4D,E0EXG$XBUE,83850,Energy,Oil & Gas Integrated,9,...
```

### `search YPF --universe XBUE` (4 resultados)

```json
{
  "_meta": {"query": "YPF", "universe_count": 1, "total_results": 4},
  "results": [
    {"Ticker": "YPFD",   "PerformanceId": "0P0000BS4D", "Name": "YPF SA Class D",        "ClosePrice": 83850, "SectorName": "Energy", "IndustryName": "Oil & Gas Integrated", "_universe_code": "XBUE"},
    {"Ticker": "YPFD1",  "PerformanceId": "0P0001NX4I", "Name": "YPF SA Class D Cedear", ...},
    {"Ticker": "YPF",    "PerformanceId": "...",          "Name": "YPF SA",                ...},
    ...
  ]
}
```

---

## Consideraciones tecnicas

### Token universal

El mismo token `klr5zyak8x` funciona en **5 sub-dominios** de `tools.morningstar.*`:

| Dominio | Idioma default |
|---------|----------------|
| `tools.morningstar.co.uk` | English (UK) |
| `tools.morningstar.de` | German |
| `tools.morningstar.fr` | French |
| `tools.morningstar.it` | Italian |
| `tools.morningstar.es` | Spanish |

Todos devuelven la misma data. El script prueba los 5 hasta que uno responda 200.

> **NO funciona en:** `tools.morningstar.com` (US), `.com.au`, `.br`, `.jp`, etc. (geofencing, IP blocking o no existe el endpoint).

### Encoding

El API devuelve nombres de sectores/industrias en el idioma del `languageId` (es-AR, de-DE, etc.). **PROBLEMA:** los caracteres acentuados vienen mal-encodados (`Energ�a` en vez de `Energía`).

**Solucion del script:** usar `languageId=en-GB` para todos los universes. Los nombres de empresas (Apple, YPF, etc.) se mantienen, solo los nombres de sectores/industrias se devuelven en inglés (que es el estándar para screener cuantitativo).

### Rate limit

No hay rate limit agresivo observado. Sin embargo:
- Hacer 50+ requests en pocos segundos puede triggerear throttling del CDN
- El script espera 0.5-1 segundo entre universes (configurable en `get()`)
- Sin reintentos agresivos

### PerformanceId

Cada **listing** (instrumento en un exchange especifico) tiene un `PerformanceId` unico. El mismo "Apple Inc" tiene:
- `0P000000GY` en NASDAQ (XNAS)
- `0P0000EEDJ` en XFRA (Frankfurt)
- `0P0000VE8R` en BVMF (Brasil BDR)
- `0P0000TFNY` en XBUE (CEDEAR Argentina)

> El PerformanceId NO se transfiere entre exchanges. Es la unica clave estable para identificar un listing especifico.


## Estructura del skill

```
skills/morningstar/
├── SKILL.md                          # Este archivo (guia rapida)
├── assets/
│   ├── UNIVERSES.md                  # Lista completa de 53 universes
│   └── DATA_POINTS.md                # Lista de 33 campos disponibles
├── references/
│   └── REFERENCE.md                  # Documentacion tecnica detallada
└── scripts/
    └── fetch_morningstar.py          # Script principal
```

---

> **Documentacion detallada:** Consultar [references/REFERENCE.md](./references/REFERENCE.md) para la doc tecnica exhaustiva de endpoints, JSON schemas, ejemplos y troubleshooting.
