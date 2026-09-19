---
name: earningswhispers
description: "Earnings transcripts completos via API publica de EarningsWhispers. Sin anti-bot, sin auth. 33,500+ stocks globales trackeados. Test ok en mas de 60 tickers, AAPL, MSFT, GGAL, SHEL, TM, VALE etc"
license: MIT
metadata:
  category: finanzas, transcripts, earnings, api, global
  language: es
  source: https://www.earningswhispers.com/
---

# EarningsWhispers — Earnings Transcripts API (Cobertura Global)

Skill para extraer **earnings transcripts completos** de [EarningsWhispers](https://www.earningswhispers.com/) via su **API publica**.

**A diferencia de Seeking Alpha**, este sitio tiene una API publica abierta sin autenticacion, sin anti-bot, y sin rate limiting agresivo. Los transcripts incluyen texto completo de las earnings calls con participantes, prepared remarks y Q&A.

---

## API Endpoint

```
GET https://www.earningswhispers.com/api/conferencecalls?t={TICKER}
```

| Parametro | Tipo | Descripcion |
|---|---|---|
| `t` | **string (requerido)** | Ticker del simbolo bursatil (AAPL, MSFT, GGAL, SHEL...) |
| `ccid` | int | ID interno de conference call (opcional, no habilita historicos) |

**Response:** Array JSON. Si el ticker existe, el array contiene 1 objeto con el ultimo transcript. Si no existe, devuelve array vacio.

```
Respuesta tipica (~50 KB para GGAL, ~90 KB para AAPL):
[{
  "ccid": 132,
  "ticker": "GGAL",
  "company": "Grupo Financiero Galicia S.A.",
  "ccDate": "2026-05-14T11:00:00",
  "ccYear": 2026,
  "ccQtr": 1,
  "speakers": "JSON string con array de speakers",
  "speakerMap": "JSON string con mapping de nombres y cargos",
  "summary": null,
  "aiSummary": null,
  "status": ""
}]
```

---

## Cobertura Real

EarningsWhispers trackea **~33,500+ stocks globales** en su plataforma. De esos, una **proporcion significativa** tiene earnings transcripts completos disponibles via la API.

### Que empresas tienen transcripts?

Cualquier empresa publica que realice **earnings conference calls** puede tener transcript. En la practica:

- **Large caps**: Cobertura casi total (AAPL, MSFT, JPM, SHEL, TM...)
- **Mid caps**: Alta cobertura (la mayoria tiene transcripts)
- **Small caps**: Cobertura parcial (depende de si hacen calls publicos)
- **ADRs**: Cobertura alta para ADRs argentinos, brasilenos, mexicanos...
- **ETFs, fondos, bonds**: Sin cobertura (no hacen earnings calls)

### Como saber si un ticker tiene transcript?

Solo hay que probar la API:

```bash
# Si devuelve datos, tiene transcript
curl "https://www.earningswhispers.com/api/conferencecalls?t=AAPL"

# Si devuelve [] (array vacio), no tiene transcript
curl "https://www.earningswhispers.com/api/conferencecalls?t=XXXX"
```

### Ejemplos por region al 05-30-2026

**US — Cobertura masiva** (cualquier empresa publica US con earnings calls):

| Ticker | Empresa | Transcript |
|---|---|---|
| AAPL | Apple Inc. | ✅ Q2 2026 |
| MSFT | Microsoft Corp. | ✅ Q3 2026 |
| GOOG | Alphabet Inc. | ✅ Q1 2026 |
| AMZN | Amazon.com, Inc. | ✅ Q1 2026 |
| META | Meta Platforms, Inc. | ✅ Q1 2026 |
| NVDA | NVIDIA Corp. | ✅ Q1 2027 |
| TSLA | Tesla, Inc. | ✅ Q1 2026 |
| JPM | JPMorgan Chase & Co. | ✅ |
| V | Visa Inc. | ✅ |
| WMT | Walmart Inc. | ✅ |
| DIS | Walt Disney Co. | ✅ |
| NKE | Nike Inc. | ✅ |
| XOM | Exxon Mobil Corp. | ✅ |
| UNH | UnitedHealth Group | ✅ |
| PFE | Pfizer, Inc. | ✅ |
| DAL | Delta Air Lines | ✅ |
| COIN | Coinbase Global | ✅ |

**Europa:**

| Ticker | Empresa | Transcript |
|---|---|---|
| SHEL | Shell plc | ✅ |
| BP | BP p.l.c. | ✅ |
| TTE | TotalEnergies SE | ✅ |
| HSBC | HSBC Holdings | ✅ |
| BBVA | BBVA | ✅ |

**Asia:**

| Ticker | Empresa | Transcript |
|---|---|---|
| TM | Toyota Motor Corp. | ✅ |
| HMC | Honda Motor Co. | ✅ |
| BABA | Alibaba Group | ✅ |
| JD | JD.com, Inc. | ✅ |
| TCEHY | Tencent Holdings | ✅ |
| INFY | Infosys Technologies | ✅ |

**LatAm:**

| Ticker | Empresa | Transcript |
|---|---|---|
| ITUB | Itau Unibanco | ✅ |
| BBD | Banco Bradesco | ✅ |
| VALE | Vale S.A. | ✅ |
| AMX | America Movil | ✅ |
| FMX | Fomento Economico Mexicano | ✅ |
| SBS | Cia de Saneamento | ✅ |
| WMMVY | Walmart Mexico | ✅ |

**Argentina:**

| Ticker | Empresa | Transcript |
|---|---|---|
| GGAL | Grupo Financiero Galicia | ✅ Q1 2026 |
| YPF | YPF S.A. | ✅ Q1 2026 |
| TGS | Transportadora de Gas | ✅ Q1 2026 |
| PAM | Pampa Energia | ✅ Q4 2025 |
| BMA | Banco Macro | ✅ |

---

## Sobre los tickers que no funcionan

Algunos tickers pueden no tener transcript por estas razones:

| Motivo | Ejemplos |
|---|---|
| **No hacen earnings calls** | ETFs (SPY, QQQ, ARKK), bonds |
| **Ticker incorrecto** | GOOGL -> GOOG, WALMEX -> WMMVY |
| **No cubiertos en la base** | Algunos small caps |
| **Empresa quebrada/fusionada** | SBNY, FRC |

---

## Notas sobre Tickers

- **GOOGL** no funciona, usar **GOOG** (Alphabet)
- **WALMEX** no funciona, usar **WMMVY** (Walmart Mexico)
- **SNE** (antiguo Sony) ya no existe, SONY tampoco esta cubierto
- Tickers que no existen en la base devuelven `[]` (array vacio)

---

## Instalacion

```bash
python -c "from curl_cffi import requests; print('OK')"
```

Dependencia: `curl_cffi` (ya disponible en el entorno).

---

## Scripts

| Script | Descripcion |
|---|---|
| **[ew_client.py](./scripts/ew_client.py)** | Cliente completo con CLI integrado |
| **[ew_cli.py](./scripts/ew_cli.py)** | CLI wrapper |

---

## Uso Rapido

### CLI

```bash
# Cualquier ticker global
python ew_cli.py get AAPL
python ew_cli.py get SHEL --json
python ew_cli.py batch MSFT,GOOG,AMZN --json
python ew_cli.py info GGAL

# Lista de tickers de ejemplo
python ew_cli.py list
```

### Desde Python

```python
from ew_client import EarningsWhispersClient

client = EarningsWhispersClient()

# Transcript de cualquier empresa global
tr = client.get_transcript("AAPL")
print(tr.company)                    # "Apple, Inc."
print(tr.prepared_remarks[:500])

# Como dict (para JSON)
data = tr.to_dict()

# Batch
results = client.get_transcripts_batch(["MSFT", "GOOG", "AMZN"])
```

---

## Campos Clave del Transcript

```python
tr = client.get_transcript("NVDA")
tr.company          # "NVIDIA Corp."
tr.date             # "2026-05-20T16:30:00"
tr.quarter_label    # "Q1"
tr.year             # 2027 (fiscal year)
tr.prepared_remarks # Texto de la presentacion
tr.qa_section       # Preguntas y respuestas
tr.summary          # Resumen ejecutivo (puede ser None)
tr.ai_summary       # Resumen AI (puede ser None)
```

---

## Cache

- Cache local en `.cache/transcript_{TICKER}.json`
- Expiracion: **24 horas**
- Forzar refresh: `--no-cache` o `force_refresh=True`
- El cache **NUNCA** almacena cookies ni credenciales

---

## Limitaciones

1. **Solo ultimo transcript**: La API devuelve solo el mas reciente. No hay historico completo.
2. **Sin search endpoint**: No hay forma de descubrir tickers disponibles programaticamente.
3. **Sin autenticacion Google/Facebook**: La pagina web requiere login; la API no.
4. **Cobertura no exhaustiva**: ~33,500 stocks trackeados, pero no todos tienen transcripts (depende de si hacen earnings calls publicos).
5. **Sin datos historicos**: El parametro `ccid` no habilita acceso a transcripts anteriores.

---

## Referencias

- [REFERENCES.md](./references/REFERENCES.md) — Documentacion tecnica detallada
- [EarningsWhispers](https://www.earningswhispers.com/) — Sitio web
- [news.js](https://www.earningswhispers.com/js/news.js) — JS con el endpoint original
