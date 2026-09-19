# Macrotrends — Cobertura de Mercados

Macrotrends cubre aproximadamente **~6,500 tickers** que cotizan en **mercados de Estados Unidos** (NYSE, NASDAQ, AMEX). Incluye:

- **Acciones US** — Empresas estadounidenses (~5,300 tickers)
- **ADRs Internacionales** — Empresas no-US que cotizan en EEUU (~276+ ADRs)
- **ETFs y Fondos** — ~91 ETFs
- **Class A/B shares** — Acciones con clases múltiples (~22)

**No cubre** acciones que cotizan exclusivamente en bolsas extranjeras sin ADR en EEUU.

---

## Cómo consultar tickers

### Por defecto (search automático)

El script resuelve el slug automáticamente usando el search endpoint interno de Macrotrends:

```bash
python fetch_financials.py --ticker GGAL --all
```

### Usando slug manual

Si el search no encuentra el ticker, se puede pasar el slug manual:

```bash
# Buscar el slug en el search endpoint
python -c "
import requests, json
r = requests.get('https://www.macrotrends.net/assets/php/ticker_search_list.php',
    headers={'User-Agent': 'Mozilla/5.0'})
data = r.json()
for item in data:
    if 'AAPL' in item['n']:
        print(item)
"
```

### Listar todos los tickers disponibles

```bash
python -c "
import requests, json
r = requests.get('https://www.macrotrends.net/assets/php/ticker_search_list.php',
    headers={'User-Agent': 'Mozilla/5.0'})
data = r.json()
# Listar tickers ordenados
for item in sorted(data, key=lambda x: x['s']):
    ticker = item['s'].split('/')[0]
    print(f'{ticker:10s} {item[\"n\"]}')
" > all_macrotrends_tickers.txt
```

---

## ADRs Internacionales Destacados

Empresas internacionales con ADR en EEUU que **sí** están en Macrotrends:

| País/Región | Tickers |
|-------------|---------|
| Argentina | **GGAL**, BBAR, EDN, PAM, TEO, LOMA, SUPV, IRSA, CRESY, CEPU |
| Brasil | **PBR**, VALE, ITUB, BBD, ABEV, GGB, SUZ, TIMB, SBS, UGP, CSAN, NTCOY, BAK |
| México | **AMX**, KOF, FMX, CX, OMAB, PAC, ASR, TV, SIM, VTMX, AGRO, VLRS |
| Chile | **BCH**, BSAC, ENIC, CCU, SQM, AKO.A, AKO.B |
| Colombia | **EC**, AVAL, CIB |
| UK | **BP**, HSBC, LYG, SHEL, UL, BCS |
| España | **SAN**, BBVA, TEF, IBDRY, GRFS, CAIXY, TELFY, EXTOY |
| Francia | **TTE**, VLEEY, LOGI, SDXAY, GNFTY, SGBAF, CLLS, EDAP, IPHA, STLA |
| Alemania | **SIEGY**, SMERY, SMNEY |
| Suiza | **NVS**, NSRGY, RHHBY |
| Japón | **TM**, SONY |
| China | **BABA**, TCEHY, TSM, TME |
| India | (ver tickers individuales en search endpoint) |
| Países Bajos | **ASML**, UL, MT |

> **Nota:** Muchas empresas internacionales también cotizan como ADR en EEUU. Si existe un ADR, Macrotrends lo tiene. Para ver la lista completa de ADRs disponibles, ejecutá el comando de búsqueda de más arriba.

---

## Empresas que NO están en Macrotrends

Macrotrends en general **NO** tiene datos de acciones que cotizan **exclusivamente** en bolsas locales fuera de EEUU sin un ADR en NYSE/NASDAQ/AMEX.

Ejemplos de tickers que **no funcionan**:
- `RY.TO` — Royal Bank of Canada (solo TSX)
- `SAP.DE` — SAP (solo XETRA)
- `ITUB4.SA` — Itaú (Brasil, solo B3 — pero ITUB sí funciona como ADR)
- `GGAL.BA` — Galicia (BYMA — pero GGAL funciona como ADR en NASDAQ)
- `005930.KS` — Samsung (solo KRX)

### Alternativas para tickers internacionales

Si el ticker que buscás no está en Macrotrends, podés:

1. **Buscar su ADR en EEUU** — Muchas empresas grandes tienen ADR en NYSE/NASDAQ
2. **Usar Yahoo Finance skill** — Cubre mercados globales
3. **Usar Twelve Data** (free tier: 800 req/día con técnicos y OHLCV global)
