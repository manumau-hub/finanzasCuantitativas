---
name: finnhub
description: "API de datos financieros completa: stocks US/global, forex, crypto, fundamentales, noticias, earnings, recomendaciones, WebSocket. 60 calls/min gratis."
license: MIT
metadata:
  category: finanzas, api, stocks, forex, crypto, noticias, eeUU, global
  language: es
  source: https://finnhub.io/docs/api
---

# Finnhub API — Datos Financieros en Tiempo Real

API REST con **32 endpoints gratuitos** que cubre: cotizaciones en vivo, velas OHLCV, perfiles de empresa, fundamentales, noticias, forex, crypto, datos económicos, calendario de earnings y WebSocket.

**Base URL:** `https://finnhub.io/api/v1`
**Documentación oficial:** [finnhub.io/docs/api](https://finnhub.io/docs/api)
**Pricing:** [finnhub.io/pricing](https://finnhub.io/pricing)

---

## ⚠️ IMPORTANTE: Endpoints Free vs Premium

Este skill documenta **todos** los endpoints, pero marca claramente cuáles son:

- ✅ **FREE** — Funcionan con el plan gratuito (60 calls/min, sin tarjeta)
- 🔒 **PREMIUM** — Requieren plan pago (Starter $11.99/mes+, Professional $49.99/mes o Enterprise)

> **NOTA CRÍTICA:** El plan gratuito de Finnhub es **mucho más limitado** de lo que su documentación sugiere. Según pruebas con una API key gratuita real (2026), solo los siguientes endpoints funcionan:
> - `/quote` (cotización), `/stock/profile2` (perfil empresa), `/stock/peers` (pares), `/stock/earnings` (earnings)
> - `/stock/recommendation` (recomendaciones), `/stock/metric` (métricas), `/news` (noticias mercado)
> - `/company-news` (noticias empresa), `/search` (búsqueda), `/stock/market-status` (estado mercado)
>
> Endpoints como `stock/candle` (velas OHLCV), `stock/financials`, `stock/price-target`, `stock/dividend`, `forex/rates`, `crypto/candle` **requieren plan pago**.
>
> Ver la tabla completa en [references/ENDPOINTS.md](./references/ENDPOINTS.md).

---



## Autenticación

### Obtener API Key (GRATIS, sin tarjeta de crédito)

1. Ir a: [https://finnhub.io/register](https://finnhub.io/register)
2. Crear cuenta (email + contraseña)
3. Copiar la API Key del dashboard: [https://finnhub.io/dashboard](https://finnhub.io/dashboard)
4. **Plan gratuito**: 60 calls/minuto, 30 calls/segundo máximo

### Usar la API Key

```python
import os
API_KEY = os.getenv("FINNHUB_API_KEY")  # Recomendado (variable de entorno)
# O directamente en tests:
# API_KEY = "tu_api_key_aqui"
```

```bash
# Header (recomendado)
X-Finnhub-Token: tu_api_key

# O query param
?token=tu_api_key
```

**⚠️ NUNCA hardcodear la API key en código compartido.**

---

## Rate Limits

| Límite | Plan Free | Starter ($11.99/mes) | Professional ($49.99/mes) | Enterprise ($3500/mes) |
|--------|-----------|---------------------|-------------------------|----------------------|
| **Calls/minuto** | 60 | 300+ | 300+ | 900 (market), 300 (fund) |
| **Calls/segundo** | 30 (global) | 30 (global) | 30 (global) | 30 (global) |
| **WebSocket símbolos** | 50 | Ilimitado | Ilimitado | Ilimitado |
| **Historia OHLCV** | Limitada | 30+ años | 30+ años | 30+ años |
| **Noticias** | 1 año | 20 años | 20 años | 20 años |
| **Cobertura fundamental** | US | Global | Global | Global |

> **Tip:** si recibís HTTP 429, esperá 1-2 segundos antes de reintentar.

---

## Uso Rápido

### 1. Cotización en tiempo real

```python
import requests

API_KEY = "tu_api_key"
BASE = "https://finnhub.io/api/v1"

r = requests.get(f"{BASE}/quote", params={"symbol": "AAPL", "token": API_KEY})
quote = r.json()
print(f"AAPL: ${quote['c']:.2f} ({quote['dp']:+.2f}%)")
```

### 2. Perfil de empresa

```python
r = requests.get(f"{BASE}/stock/profile2", params={"symbol": "AAPL", "token": API_KEY})
profile = r.json()
print(f"{profile['name']} | {profile['finnhubIndustry']} | Market Cap: ${profile['marketCapitalization']/1000:.2f}B")
```

### 3. Noticias de una empresa

```python
r = requests.get(f"{BASE}/company-news", params={
    "symbol": "AAPL", "from": "2025-01-01", "to": "2025-01-15", "token": API_KEY
})
for article in r.json()[:3]:
    print(f"  {article['headline'][:80]}...")
```

### 4. Velas OHLCV diarias

```python
import time
end = int(time.time())
start = end - (90 * 86400)  # 90 días
r = requests.get(f"{BASE}/stock/candle", params={
    "symbol": "AAPL", "resolution": "D",
    "from": start, "to": end, "token": API_KEY
})
candles = r.json()
print(f"Status: {candles['s']}, velas: {len(candles['c'])}")
```

### 5. Búsqueda de símbolos

```python
r = requests.get(f"{BASE}/search", params={"q": "microsoft", "token": API_KEY})
for result in r.json()["result"]:
    print(f"{result['symbol']}: {result['description']} ({result['type']})")
```

---

## Scripts Disponibles

| Script | Descripción | Endpoints que usa |
|--------|-------------|-------------------|
| **[finnhub_client.py](./scripts/finnhub_client.py)** | Cliente Python completo con todos los endpoints gratuitos | quote, candle, profile2, peers, metric, financials, earnings, recommendation, price-target, company-news, news, forex, crypto, search, economic, market-status, dividends, splits, calendar |
| **[finnhub_cli.py](./scripts/finnhub_cli.py)** | Interfaz de línea de comandos para consultas rápidas | quote, profile2, search, news, peers, earnings, market-status |
| **[download_multiple.py](./scripts/download_multiple.py)** | Descarga batches de datos por categorías | quote, candle, metric, financials, earnings, recommendation, company-news |

---

## Cobertura de la API (según pruebas con key gratuita real)

| Categoría | Endpoints | Free | Premium |
|-----------|-----------|:----:|:-------:|
| **Cotizaciones** | quote | ✅ | — |
| **Perfil empresa** | profile2, peers | ✅ | — |
| **Earnings** | earnings (4 quarters free) | ✅ | — |
| **Recomendaciones** | recommendation (~8 meses) | ✅ | — |
| **Métricas (133)** | metric (sin historia, solo último valor) | ✅ | — |
| **Noticias** | company-news, news | ✅ | — |
| **Búsqueda** | search | ✅ | — |
| **Estado mercado** | market-status | ✅ | — |
| **Velas OHLCV** | candle | — | 🔒 Premium |
| **Estados financieros** | financials, financials-reported, price-target | — | 🔒 Premium |
| **Dividendos/Splits** | dividend, split | — | 🔒 Premium |
| **Forex** | rates, candle, exchange, symbol | — | 🔒 Premium |
| **Crypto** | candle, exchange, symbol | — | 🔒 Premium |
| **Económico** | economic/code, economic, country | — | 🔒 Premium |
| **Símbolos** | stock/symbol, market-holiday, ipo-calendar | — | 🔒 Premium |
| **WebSocket** | Trades (50 símbolos) | — | 🔒 Premium |
| **Insider, Ownership** | insider-transactions, ownership, etc. | — | 🔒 Premium |
| **Estimates** | eps-estimate, revenue-estimate, etc. | — | 🔒 Premium |
| **ETFs, Índices, Bonos** | etf/profile, etf/holdings, index/constituents, bond/price, etc. | — | 🔒 Premium |
| **Alternativos** | social-sentiment, covid-19, esg-score, etc. | — | 🔒 Premium |

> ⚠️ Esta tabla está basada en **pruebas reales con una API key gratuita en junio 2026**. Finnhub cambia su política de acceso periódicamente. Verificar siempre en la [documentación oficial](https://finnhub.io/docs/api).

---

## Buenas Prácticas

1. **Usar variable de entorno** `FINNHUB_API_KEY` en vez de hardcodear
2. **Cachear resultados**: los datos fundamentales cambian poco (especialmente company profile, financials)
3. **Rate limiting**: 60 calls/min gratis = 1 call por segundo como mínimo
4. **Evitar endpoints premium** con key gratuita — recibirás error `"You don't have access to this resource."`
5. **WebSocket**: solo 1 conexión por API key, 50 símbolos en free
6. **Reutilizar sesión HTTP** para mejor performance (`requests.Session()`)
7. **No usar para trading de alta frecuencia**: API pública, sin garantía de latencia ultra-baja

---

## Recursos

- [Documentación oficial Finnhub](https://finnhub.io/docs/api)
- [Pricing oficial](https://finnhub.io/pricing)
- [Python SDK oficial](https://github.com/Finnhub-Stock-API/finnhub-python)
- [Referencia de endpoints free vs premium](./references/ENDPOINTS.md)
- [Dashboard (API key)](https://finnhub.io/dashboard)
- [Estado del servicio](https://status.finnhub.io/)
