---
name: sec-data
description: "SEC EDGAR financial data: secfi library + structured JSON income statements, balance sheets, cash flow from XBRL facts."
license: MIT
---

# SEC Data — Financial Statements from SEC EDGAR

Acceso a datos financieros estructurados de la **SEC EDGAR** mediante la librería `secfi` + la API JSON de XBRL facts de la SEC.

Obtiene **income statements, balance sheets, cash flow statements** en formato JSON/CSV estructurado directamente de los filings XBRL.

Soporta **US-GAAP** (empresas US) e **IFRS** (empresas extranjeras) con mapping automático de conceptos.

---

## Dependencia

```bash
pip install secfi
```

Requiere `pandas` y `requests` (vienen con secfi).

---

## Cómo funciona

La SEC expone datos financieros estructurados via dos endpoints JSON:

| Endpoint | Descripción |
|----------|-------------|
| **Company Facts** | `https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json` — Todos los datos XBRL |
| **Company Concept** | `https://data.sec.gov/api/xbrl/companyconcept/CIK{CIK}/us-gaap/{concept}.json` — Histórico de un concepto |

El flujo típico:
1. `secfi.getCiks()` → obtiene el CIK del ticker
2. Fetch `companyfacts/CIK{cik}.json` → obtiene todos los datos financieros estructurados
3. El script mapea automáticamente conceptos US-GAAP ↔ IFRS según la taxonomía

### Taxonomías soportadas

| Taxonomía | Empresas | Formularios | Ejemplos |
|-----------|----------|-------------|----------|
| `us-gaap` | Empresas US | 10-K, 10-Q | AAPL, MSFT, NVDA |
| `ifrs-full` | Empresas extranjeras (Foreign Private Issuers) | 20-F, 6-K | GGAL, BABA, SAP, SPOT |

El script detecta automáticamente la taxonomía y resuelve los conceptos usando un mapping US-GAAP ↔ IFRS.

---

## Autenticación

```python
HEADERS = {"User-Agent": "osojuanferpity@xmail.com"}
```

La SEC **bloquea** requests sin User-Agent válido (403 Forbidden). Usar el mismo email que `secfi` usa internamente.

---

## Script principal: `fetch_financials.py`

```bash
# AAPL (US-GAAP) — todo
python scripts/fetch_financials.py --ticker AAPL --all

# GGAL (IFRS) — todo
python scripts/fetch_financials.py --ticker GGAL --all

# Solo income statement
python scripts/fetch_financials.py --ticker MSFT --income

# Solo balance + cash flow
python scripts/fetch_financials.py --ticker NVDA --balance --cashflow

# Todos los conceptos disponibles (no solo core)
python scripts/fetch_financials.py --ticker AAPL --all --all-concepts

# Output personalizado
python scripts/fetch_financials.py --ticker AAPL --all --output data/aapl

# Solo anual (default)
python scripts/fetch_financials.py --ticker AAPL --all

# Incluir trimestral también
python scripts/fetch_financials.py --ticker AAPL --all --quarterly
```

### Flags disponibles

| Flag | Descripción |
|------|-------------|
| `--ticker`, `-t` | Ticker a consultar (requerido) |
| `--all` | Fetch de income + balance + cashflow |
| `--income` | Solo income statement |
| `--balance` | Solo balance sheet |
| `--cashflow` | Solo cash flow statement |
| `--all-concepts` | Todos los conceptos disponibles en la taxonomía (default: solo core) |
| `--annual` | Solo datos anuales (default) |
| `--quarterly` | Incluir datos trimestrales |
| `--output`, `-o` | Prefijo de archivos de salida |
| `--quiet`, `-q` | Sin salida detallada |

### Output generado

```
{ticker}_financials.json          → JSON completo con todos los conceptos
{ticker}_financials.csv           → CSV tabular aplanado (concepto x entry)
{ticker}_financials_income_annual.csv  → Matriz concepto x año (income)
{ticker}_financials_balance_annual.csv → Matriz concepto x año (balance)
{ticker}_financials_cashflow_annual.csv → Matriz concepto x año (cash flow)
```

### Mapping IFRS automático

El script incluye un diccionario `IFRS_MAP` con **33+ conceptos US-GAAP mapeados** a sus equivalentes IFRS. Por ejemplo:

| US-GAAP | IFRS (ifrs-full) |
|---------|------------------|
| `Revenues` | `RevenueAndOperatingIncome` |
| `OperatingIncomeLoss` | `ProfitLossFromOperatingActivities` |
| `NetIncomeLoss` | `ProfitLoss` |
| `StockholdersEquity` | `Equity` |
| `NetCashProvidedByUsedInOperatingActivities` | `CashFlowsFromUsedInOperatingActivities` |

### Free Cash Flow (FCF)

El script calcula automáticamente el FCF:

```
FCF = Operating CF - CAPEX
```

Tanto para US-GAAP como IFRS.

---

## Testeado con

### AAPL (US-GAAP) — 55 conceptos extraídos ✅

```
>> Company facts: 4053 KB
>> Income: 13 conceptos x 17 años
>> Balance: 24 conceptos x 17 años
>> Cash flow: 18 conceptos x 17 años
>> FCF 2025: $98.7B
```

### GGAL (IFRS) — 40 conceptos extraídos ✅

```
>> Company facts: 724 KB
>> Revenue: $7.72B (2024) · Net Income: $1.76B (2024)
>> Balance: Assets $35.3B · Equity $6.58B
>> Cash flow: Operating $3.80B · FCF $3.57B
```

---

## Rate Limits

| Límite | Comportamiento |
|--------|----------------|
| ~10 req/s | Límite SEC |
| Sin API key | Público, requiere User-Agent con email |
| Datos históricos | No cambian — **cachear respuestas** |

---

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `403 Forbidden` | User-Agent inválido | Usar `osojuanferpity@xmail.com` |
| `404 Not Found` | CIK incorrecto | Verificar con `secfi.getCiks()` |
| `Ticker not found` | No está en SEC | Solo empresas que reportan a SEC |
| `KeyError: us-gaap` | Usa IFRS | El script lo resuelve automáticamente |

---

## Estructura del skill

```
skills/sec-data/
├── SKILL.md                           # Este archivo
├── references/
│   └── FINANCIALS_REFERENCE.md        # Referencia completa: todos los conceptos + mapping IFRS
└── scripts/
    └── fetch_financials.py            # Script principal con mapping IFRS automático
```
