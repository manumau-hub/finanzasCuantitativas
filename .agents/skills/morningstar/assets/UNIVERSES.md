# Morningstar Universe Codes

Lista exhaustiva de los **53 universe codes** con datos confirmados al 2026-06-04.
Todos se acceden via el mismo endpoint con el mismo token universal `klr5zyak8x`.

**Total: 102,093 listings** en 39 paises.

---

## Como usar

```bash
# Ver todos
python scripts/fetch_morningstar.py info

# Descargar uno
python scripts/fetch_morningstar.py screener --universe XNAS -o nasdaq.csv

# Multiples
python scripts/fetch_morningstar.py screener --universe XNAS XLON XTKS -o 3markets.csv

# Por pais
python scripts/fetch_morningstar.py screener --country AR -o argentina.csv

# Todos
python scripts/fetch_morningstar.py screener --all -o global.csv
```

---

## Americas (9 universes, 13,985 listings)

| Code | Exchange | Country | Currency | Count |
|------|----------|---------|----------|-------|
| `XNYS` | NYSE (New York Stock Exchange) | United States | USD | 2,343 |
| `XNAS` | Nasdaq | United States | USD | 3,741 |
| `ARCX` | NYSE Arca | United States | USD | 3 |
| `XASE` | NYSE American | United States | USD | 267 |
| `XTSE` | TSX (Toronto) | Canada | CAD | 1,123 |
| `XTSX` | TSXV (TSX Venture) | Canada | CAD | 1,728 |
| `XMEX` | BMV (Bolsa Mexicana) | Mexico | MXN | 2,233 |
| `BVMF` | B3 (Brasil) | Brasil | BRL | 2,070 |
| `XBUE` | BCBA (Buenos Aires) | Argentina | ARS | 469 |

> **Argentina (XBUE):** devuelve los **CEDEARs** (certificados de deposito de acciones extranjeras que cotizan en BCBA) con precios en ARS. Cada CEDEAR tiene un `PerformanceId` distinto del ADR original. Ej: Apple Inc CEDEAR → `0P0000TFNY`, vs Apple Inc NASDAQ → `0P000000GY`.

---

## Europe (27 universes, 65,206 listings)

### Reino Unido
| Code | Exchange | Country | Currency | Count |
|------|----------|---------|----------|-------|
| `XLON` | LSE (London Stock Exchange) | United Kingdom | GBP | 1,333 |

### Zona Euro
| Code | Exchange | Country | Currency | Count |
|------|----------|---------|----------|-------|
| `XPAR` | Euronext Paris | France | EUR | 728 |
| `XAMS` | Euronext Amsterdam | Netherlands | EUR | 123 |
| `XBRU` | Euronext Brussels | Belgium | EUR | 140 |
| `XLIS` | Euronext Lisbon | Portugal | EUR | 49 |
| `XDUB` | Euronext Dublin | Ireland | EUR | 44 |
| `XETR` | Xetra (Deutsche Borse) | Germany | EUR | 1,048 |
| `XFRA` | Frankfurt (Tradegate) | Germany | EUR | 14,082 |
| `XSTU` | Stuttgart | Germany | EUR | 9,971 |
| `XMUN` | Munich | Germany | EUR | 8,425 |
| `XHAM` | Hamburg | Germany | EUR | 3,596 |
| `XDUS` | Dusseldorf | Germany | EUR | 8,297 |
| `XBER` | Berlin | Germany | EUR | 256 |
| `XHAN` | Hanover | Germany | EUR | 1,436 |
| `XMIL` | Borsa Italiana (Milan) | Italy | EUR | 1,411 |
| `XMAD` | BME Madrid | Spain | EUR | 291 |
| `XMCE` | Mercado Continuo (Madrid) | Spain | EUR | 291 |
| `XHEL` | Helsinki (Nasdaq Nordic) | Finland | EUR | 194 |
| `XATH` | Athens | Greece | EUR | 149 |

> **Alemania (XFRA, XSTU, XETR, XMUN, XHAM, XDUS, XBER, XHAN):** hay **8 exchanges alemanes** con miles de listings. La diferencia entre ellos es principalmente el horario y los participantes. XFRA/XSTU/XMUN son los mas grandes.

### Otros Paises Europeos
| Code | Exchange | Country | Currency | Count |
|------|----------|---------|----------|-------|
| `XSWX` | Swiss Exchange (SIX) | Switzerland | CHF | 507 |
| `XCSE` | Copenhagen (Nasdaq Nordic) | Denmark | DKK | 146 |
| `XOSL` | Oslo (Euronext) | Norway | NOK | 296 |
| `XSTO` | Stockholm (Nasdaq Nordic) | Sweden | SEK | 930 |
| `XICE` | Iceland (Nasdaq Nordic) | Iceland | ISK | 31 |
| `XTAL` | Tallinn (Nasdaq Baltic) | Estonia | EUR | 35 |
| `XWAR` | Warsaw | Poland | PLN | 797 |
| `XIST` | Borsa Istanbul | Turkey | TRY | 607 |

---

## Asia (13 universes, 33,479 listings)

| Code | Exchange | Country | Currency | Count |
|------|----------|---------|----------|-------|
| `XTKS` | TSE (Tokyo) | Japan | JPY | 3,989 |
| `XSHG` | SSE (Shanghai) | China | CNY | 2,365 |
| `XSHE` | SZSE (Shenzhen) | China | CNY | 2,934 |
| `XHKG` | HKEX (Hong Kong) | Hong Kong | HKD | 2,757 |
| `XSES` | SGX (Singapore) | Singapore | SGD | 642 |
| `XKRX` | KRX (Korea Exchange) | South Korea | KRW | 2,877 |
| `XBOM` | BSE (Bombay) | India | INR | 5,192 |
| `XNSE` | NSE India | India | INR | 3,018 |
| `XTAI` | TWSE (Taiwan) | Taiwan | TWD | 1,127 |
| `XBKK` | SET (Bangkok) | Thailand | THB | 2,719 |
| `XKLS` | Bursa Malaysia | Malaysia | MYR | 1,142 |
| `XIDX` | IDX (Jakarta) | Indonesia | IDR | 961 |
| `XPHS` | PSE (Philippines) | Philippines | PHP | 361 |

> **China (XSHG, XSHE):** las acciones A de China continental. Las acciones B y H tienen otros universes. Stocks como Tencent cotizan en XHKG.

---

## Oceania (2 universes, 1,941 listings)

| Code | Exchange | Country | Currency | Count |
|------|----------|---------|----------|-------|
| `XASX` | ASX (Australian Securities Exchange) | Australia | AUD | 1,814 |
| `XNZE` | NZX (New Zealand Exchange) | New Zealand | NZD | 127 |

---

## Middle East & Africa (2 universes, 878 listings)

| Code | Exchange | Country | Currency | Count |
|------|----------|---------|----------|-------|
| `XTAE` | TASE (Tel Aviv) | Israel | ILS | 546 |
| `XJSE` | JSE (Johannesburg) | South Africa | ZAR | 332 |

---

## Universes SIN datos (probados pero vacíos o no disponibles)

| Code | Exchange | Pais | Notas |
|------|----------|------|-------|
| `XBOS` | Boston Stock Exchange | US | No listado en Morningstar |
| `EDGX` | CBOE EDGX | US | No listado |
| `CSE2` | Canadian Securities Exchange | Canada | No listado |
| `XSGO` | Santiago | Chile | No listado |
| `XBOG` | Colombia | Colombia | No listado |
| `XLIM` | Lima | Peru | No listado |
| `MTAA` | Mercato Telematico Azionario | Italy | Duplicado de XMIL |
| `XBIL` / `XBAR` / `XVAL` | Bilbao/Barcelona/Valencia | Spain | Sub-exchanges no listados |
| `XVIE` | Vienna | Austria | No listado |
| `XRIG` | Riga | Latvia | No listado |
| `XPRA` | Prague | Czech Republic | No listado |
| `XBUD` | Budapest | Hungary | No listado |
| `XBSE` | Bucharest | Romania | No listado |
| `XMOS` | Moscow | Russia | No listado (probablemente removido) |
| `XKOS` | KOSDAQ | South Korea | Duplicado de XKRX |
| `XVSE` | Ho Chi Minh | Vietnam | No listado |
| `DSMD` | Saudi Arabia (Tadawul) | Saudi Arabia | No listado |
| `XDFM` / `XADX` | Dubai / Abu Dhabi | UAE | No listado |
| `XCAI` | Cairo | Egypt | No listado |
| `XNAI` | Nairobi | Kenya | No listado |

> **Nota:** estos codigos pueden haber sido removidos, renombrados o nunca existieron. Morningstar no documenta oficialmente estos codigos.

---

## Acceso por pais (--country flag)

| Codigo Pais | Universes |
|-------------|-----------|
| `US` | XNYS, XNAS, ARCX, XASE |
| `CA` | XTSE, XTSX |
| `MX` | XMEX |
| `BR` | BVMF |
| `AR` | XBUE |
| `GB` | XLON |
| `FR` | XPAR |
| `NL` | XAMS |
| `BE` | XBRU |
| `PT` | XLIS |
| `IE` | XDUB |
| `DE` | XETR, XFRA, XSTU, XMUN, XHAM, XDUS, XBER, XHAN |
| `IT` | XMIL |
| `ES` | XMAD, XMCE |
| `FI` | XHEL |
| `GR` | XATH |
| `CH` | XSWX |
| `DK` | XCSE |
| `NO` | XOSL |
| `SE` | XSTO |
| `IS` | XICE |
| `EE` | XTAL |
| `PL` | XWAR |
| `TR` | XIST |
| `JP` | XTKS |
| `CN` | XSHG, XSHE |
| `HK` | XHKG |
| `SG` | XSES |
| `KR` | XKRX |
| `IN` | XBOM, XNSE |
| `TW` | XTAI |
| `TH` | XBKK |
| `MY` | XKLS |
| `ID` | XIDX |
| `PH` | XPHS |
| `AU` | XASX |
| `NZ` | XNZE |
| `IL` | XTAE |
| `ZA` | XJSE |

---

## Cobertura total

- **53 universes con datos** (102,093 listings totales)
- **39 paises**
- **~30 currencies** (USD, EUR, GBP, CHF, JPY, CNY, HKD, INR, BRL, ARS, etc.)
- **~20 idiomas** (en, de, fr, it, es, pt, nl, ja, zh, ko, etc.)
- **Cobertura global** incluyendo emergentes (Argentina, Brasil, Mexico, India, China, etc.)

> **No cubierto:** CEDEARs/ADR especificos con codigo ISIN, ETFs, fondos, bonos, commodities, currencies, cryptos. Para esos, usar otras skills (`investing`, `yahoo-finance`, `cboe-data`).

---

## Notas tecnicas

### PerformanceId: clave unica por listing

Cada **listing** (instrumento en un exchange especifico) tiene un `PerformanceId` unico. El mismo "Apple Inc" tiene:
- `0P000000GY` en NASDAQ (XNAS)
- `0P0000EEDJ` en XFRA (Frankfurt)
- `0P0000VE8R` en BVMF (Brasil BDR)
- `0P0000TFNY` en XBUE (CEDEAR Argentina)

> El PerformanceId NO se transfiere entre exchanges. Cada listing tiene el suyo.

### Encoding

El API devuelve nombres de sectores/industrias en el idioma del `languageId` (es-AR, de-DE, etc.). **PROBLEMA:** los caracteres acentuados vienen mal-encodados (Energ�a en vez de Energía). El script usa **`en-GB` por default** para evitar esto y devolver nombres en inglés (estandar para screener cuantitativo).

### Rate limit

Sin rate limit agresivo observado. Sin embargo, hacer 50+ requests en pocos segundos puede ser limitado por el CDN. El script espera 0.5s entre universes.

### Sin autenticacion

Todos los sub-dominios `tools.morningstar.{co.uk,de,fr,it,es}` usan el mismo token `klr5zyak8x` y no requieren login. `tools.morningstar.com` (US) está bloqueado por IP/geofencing desde algunos lugares.

### Paginas sin el endpoint

`tools.morningstar.com` (US), `tools.morningstar.com.au`, `tools.morningstar.br` y otros devuelven error de conexion o 403 por WAF/geofencing. Solo los 5 dominios `.co.uk, .de, .fr, .it, .es` aceptan el token universal.
