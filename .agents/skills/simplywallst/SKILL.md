---
name: simplywallst
description: "Data financiera de 120K+ stocks globales: snowflake scores, valuation, financial health, dividend analysis, insider transactions. Sin API key."
license: MIT
---

# SimplyWallSt — Stock Research & Snowflake Scores

Extrae datos financieros de [SimplyWallSt](https://simplywall.st/) usando su **API REST interna** (`simplywall.st/api/...`). Sin Cloudflare, sin API key, sin registro.

120,000+ stocks globales con **snowflake scores** (value, income, health, past, future, management), análisis de valuación, dividendos históricos y proyectados, score de salud financiera, insider transactions, y más.

---

## ⚠️ Aviso Legal

- SimplyWallSt **no tiene API pública oficial**. Esta skill usa endpoints internos del frontend web.
- Respetá los **términos de servicio** del sitio.
- Implementá **rate limiting** (mín 300ms entre requests).

---

## Instalación

```bash
pip install requests
```

---

## Scripts

| Script | Descripción |
|--------|-------------|
| **[fetch_sws.py](./scripts/fetch_sws.py)** | Cliente completo: listar tickers, company detail, snowflake scores, análisis |

---

## Uso rápido

```bash
# PRIMERO: Descargar snapshot de tickers (1 vez sola, ~5 min)
python scripts/fetch_sws.py --download-snapshot

# Luego: las búsquedas por ticker usan el snapshot → instantáneas
python scripts/fetch_sws.py --ticker GGAL

# Buscar por nombre
python scripts/fetch_sws.py --search "Galicia"

# Full data con todos los includes (info, score, analysis, extended, raw_data, insider)
python scripts/fetch_sws.py --ticker GGAL --full

# Listar empresas (grid)
python scripts/fetch_sws.py --grid --size 10

# Listar solo tickers disponibles (Argentina)
python scripts/fetch_sws.py --list-tickers --country AR --output tickers_ar.csv

# Snowflake scores de múltiples tickers
python scripts/fetch_sws.py --ticker GGAL,BMA,SUPV --score

# Output a archivo
python scripts/fetch_sws.py --ticker GGAL --full --output ggal_data.json
```

---

## Endpoints descubiertos

| Endpoint | Método | Data | Status |
|----------|--------|------|--------|
| `/api/grid/filter?include=info,score,grid` | POST | Listado de empresas con scores y métricas | ✅ Funciona |
| `/api/company{canonical_url}` | GET | Detail completo de una empresa | ✅ Funciona |

### Includes disponibles para Company Detail

| Include | Data |
|---------|------|
| `info` | Perfil corporativo, industria, país, empleados, CEO |
| `score` | Snowflake scores (value, income, health, past, future, management) |
| `analysis` | Precio, market cap, P/E, P/B, ROE, ROA, EPS, dividendos, growth |
| `analysis.extended` | Dividendos históricos, payout ratio, buyback, future EPS |
| `analysis.extended.raw_data` | Financial statements históricos |
| `analysis.extended.raw_data.insider_transactions` | Insider trading |

---

## Cobertura

| Característica | Detalle |
|----------------|---------|
| Stocks globales | 120,000+ en 90+ mercados |
| Mercados Argentina | ✅ BASE (BCBA) tickers: GGAL, BMA, SUPV, YPFD, etc. |
| Mercados US | ✅ NasdaqGS, NYSE, AMEX |
| Actualización | Diaria (precio de cierre) |
| Snowflake scores | Value, Income, Health, Past, Future, Management |
| Dividendos | Histórico 19+ años, proyecciones futuras |
| Insider transactions | ✅ (cuando están disponibles) |
| Analistas | Consensus count y price targets |

---

## Flags del script

| Flag | Descripción |
|------|-------------|
| `--ticker TICKER` | Ticker(s) separados por coma: GGAL o GGAL,BMA |
| `--search QUERY` | Buscar por nombre |
| `--full` | Todos los includes disponibles |
| `--score` | Solo snowflake scores |
| `--info` | Solo info corporativa |
| `--analysis` | Solo métricas de análisis |
| `--extended` | Incluir data extendida |
| `--raw-data` | Incluir raw data financiera |
| `--grid` | Listar companies via grid/filter |
| `--list-tickers` | Listar tickers disponibles |
| `--country AR` | Filtrar por país (solo --grid) |
| `--size N` | Tamaño de página (default: 24) |
| `--limit N` | Límite de resultados |
| `--download-snapshot` | Descargar snapshot completo de tickers a `assets/` |
| `--snapshot PATH` | Usar snapshot específico (default: auto-buscar en `assets/`) |
| `--output archivo.json` | Guardar output |
| `--csv` | Output en CSV |
| `--delay N` | Delay entre requests (default: 0.3s) |

---

## Ejemplos por tipo de data

### Snowflake Scores
```bash
python scripts/fetch_sws.py --ticker GGAL --score
# → value=0, income=0, health=4, past=1, future=5, management=0
# → "High growth potential with adequate balance sheet."
```

### Info Corporativa
```bash
python scripts/fetch_sws.py --ticker GGAL --info
# → name, industry (Banks), country (AR), employees (10032), year_founded (1905)
```

### Análisis + Dividendos
```bash
python scripts/fetch_sws.py --ticker GGAL --analysis --extended
# → P/E, P/B, ROE, ROA, EPS, Debt/Equity, market cap
# → dividend history, payout ratios, future yield
```

### Todos los datos
```bash
python scripts/fetch_sws.py --ticker GGAL --full
```

---

## Trabajar con el grid/filter

El grid/filter devuelve **companies listas para consumir** con info + scores + grid metrics en un solo request. Ideal para screener:

```bash
# Todas las empresas (default: market cap desc)
python scripts/fetch_sws.py --grid --limit 50

# Top 10 Argentina
python scripts/fetch_sws.py --grid --size 10
```

> **Nota:** El grid/filter no permite filtros por país o ticker directamente. Usar `--list-tickers` + `--country` para filtrar client-side.

---

## Snapshot de tickers (recomendado)

El snapshot es un archivo CSV local con **todos los listings disponibles** que permite **resolver tickers al instante** sin iterar el grid.

### Descargar el snapshot (1 vez, ~10 min)

```bash
# Descarga completa (~10 min, genera assets/YY-MM-DD-ticker-snapshot.csv)
python scripts/fetch_sws.py --download-snapshot
```

### Cómo funciona el snapshot completo

El API tiene un límite de **10,000 registros** por query. Para obtener todos, el script usa **particionado por exchange**:

1. **Fase 1**: Obtiene top 10K con la query default → extrae los exchanges disponibles
2. **Fase 2**: Para cada exchange, fetchea **todas** las empresas (cada exchange tiene < 10K registros)
3. **Dedup**: Combina todo y elimina duplicados por `unique_symbol` (exchange + ticker)

### Resultados del snapshot `26-06-04`

| Métrica | Valor |
|---------|-------|
| Total listings únicos (`unique_symbol`) | **78,454** |
| Países cubiertos | **83** |
| Exchanges | **106** |
| Duplicados en el proceso de dedup | **0** |
| Requests totales | ~944 |
| Duración | ~11 min |
| Tamaño del CSV | ~6 MB |

> **¿Por qué 78K y no 54K?** El API reporta `total_records=54,530` para la query default (que filtra por scores mínimos). Pero al particionar por exchange con reglas más simples (`exchange_symbol=X` + `primary_flag=true`), se obtienen **muchos más** — ETFs, fondos, companies sin scores, y ADRs. Las 54K son solo las que cumplen los filtros default.

### Verificación de calidad de datos

| Control | Resultado |
|---------|-----------|
| `unique_symbol` duplicados | **0** — dedup 100% efectivo |
| Mismo ticker + mismo exchange repetido | **3 casos** — todos son falsos positivos (leading zeros: `115` ≠ `0115`) |
| Tickers cross-listed (múltiples exchanges) | **8,751** — legítimo, una empresa listada en varios mercados |
| Países con más listings | US (16,274), CN (7,016), IN (6,074), CA (5,221), JP (4,764) |

### Sin snapshot

Sin snapshot, `--ticker GGAL` tarda ~30s iterando el grid. Con snapshot, es instantáneo.

### Formato del snapshot

| Campo | Descripción |
|-------|-------------|
| `ticker_symbol` | Símbolo (GGAL, BMA, MSFT, etc.) |
| `name` | Nombre de la empresa |
| `exchange_symbol` | Exchange (BASE, NasdaqGS, NYSE) |
| `canonical_url` | Ruta API para company detail |
| `unique_symbol` | Exchange + Ticker (clave única) |
| `country` | Código ISO país |
| `industry` | Industria |
| `employees` | N° empleados |
| `year_founded` | Año fundación |
| `score_value/income/health/past/future/management/total` | Snowflake scores |
| `share_price` | Precio actual |
| `market_cap` | Market cap (moneda local) |
| `pe_ratio`, `pb_ratio` | Múltiplos |

### Snapshot específico

```bash
python scripts/fetch_sws.py --snapshot assets/26-06-04-ticker-snapshot.csv --ticker GGAL
```

---

## Mapa Exchange → País

| Exchange | País | Listings | Descripción |
|----------|------|---------:|-------------|
| `OTCPK` | US | 6,138 | OTC Markets Pink (EEUU) |
| `TSE` | JP | 4,693 | Tokyo Stock Exchange (Japón) |
| `BSE` | IN | 3,833 | BSE India (antes Bombay SE) |
| `SZSE` | CN | 3,723 | Shenzhen Stock Exchange (China) |
| `SHSE` | CN | 3,293 | Shanghai Stock Exchange (China) |
| `SEHK` | HK | 3,019 | Hong Kong Exchange |
| `NYSE` | US | 2,574 | New York Stock Exchange |
| `ASX` | AU | 2,527 | Australian Securities Exchange |
| `TSX` | CA | 2,381 | Toronto Stock Exchange (Canadá) |
| `NasdaqGM` | US | 2,304 | NASDAQ Global Market |
| `NSEI` | IN | 2,241 | National Stock Exchange of India |
| `KOSE` | KR | 2,075 | Korea Exchange (KOSPI) |
| `TSXV` | CA | 1,999 | TSX Venture Exchange (Canadá) |
| `KOSDAQ` | KR | 1,997 | KOSDAQ (Corea) |
| `LSE` | GB | 1,963 | London Stock Exchange |
| `NasdaqCM` | US | 1,854 | NASDAQ Capital Market |
| `BATS` | US | 1,575 | BATS Exchange (EEUU) |
| `NasdaqGS` | US | 1,532 | NASDAQ Global Select |
| `BME` | ES | 1,514 | Bolsas y Mercados Españoles |
| `TPEX` | TW | 1,430 | Taipei Exchange (Taiwán) |
| `AIM` | GB | 1,310 | AIM (London Stock Exchange) |
| `TWSE` | TW | 1,292 | Taiwan Stock Exchange |
| `KLSE` | MY | 1,172 | Bursa Malaysia |
| `ENXTPA` | FR | 1,147 | Euronext Paris |
| `XTRA` | DE | 1,135 | Xetra (Deutsche Börse) |
| `BOVESPA` | BR | 1,120 | B3 (Brasil) |
| `TASE` | IL | 1,029 | Tel Aviv Stock Exchange |
| `SET` | TH | 993 | Stock Exchange of Thailand |
| `IDX` | ID | 985 | Indonesia Stock Exchange |
| `OM` | SE | 852 | OMX Nordic (Estocolmo) |
| `WSE` | PL | 849 | Warsaw Stock Exchange |
| `OB` | NO | 811 | Oslo Børs (Noruega) |
| `CNSX` | CA | 777 | Canadian Securities Exchange |
| `JSE` | ZA | 754 | Johannesburg Stock Exchange |
| `DB` | DE | 648 | Deutsche Börse (Frankfurt) |
| `SNSE` | CL | 647 | Santiago Stock Exchange (Chile) |
| `CPSE` | DK | 636 | Copenhagen Stock Exchange |
| `BIT` | IT | 625 | Borsa Italiana |
| `SWX` | CH | 588 | SIX Swiss Exchange |
| `IBSE` | IE | 577 | Irish Stock Exchange |
| `HOSE` | VN | 572 | Ho Chi Minh Stock Exchange |
| `HNX` | VN | 417 | Hanoi Stock Exchange |
| `SGX` | SG | 398 | Singapore Exchange |
| `DSE` | BD | 443 | Dhaka Stock Exchange |
| `DFM` | AE | 70 | Dubai Financial Market |
| `ADX` | AE | 85 | Abu Dhabi Securities Exchange |
| `BASE` | AR | 84 | Bolsa de Buenos Aires (Argentina) |
| `BMV` | MX | 147 | Bolsa Mexicana de Valores |
| `BVL` | PE | 102 | Bolsa de Valores de Lima (Perú) |
| `BVC` | CO | 56 | Bolsa de Valores de Colombia |
| ... | ... | ... | 106 exchanges en total |

> El mapping completo de los 106 exchanges está en [references/REFERENCE.md](./references/REFERENCE.md#exchange--country-mapping).

---

## Estructura del skill

```
skills/simplywallst/
├── SKILL.md                              # Este archivo
├── references/
│   └── REFERENCE.md                      # Documentación completa de endpoints y data
├── scripts/
│   └── fetch_sws.py                      # Script principal
└── assets/
    └── YY-MM-DD-ticker-snapshot.csv      # Snapshot de tickers (generado)
```

---

> **📖 Documentación detallada:** Consultá [references/REFERENCE.md](./references/REFERENCE.md) para la documentación exhaustiva con ejemplos de respuesta, campos, y consideraciones técnicas.
