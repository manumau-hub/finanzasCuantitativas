---
name: marketscreener
description: "Scraper de MarketScreener (S&P Capital IQ): earnings transcripts, cotizaciones, perfiles empresa, financials, valuation, consenso analistas, noticias, insider trading, ratings. Sin API key."
license: MIT
metadata:
  category: finanzas, scraper, stocks, transcripts, earnings, eeuu, global, ADRs
  language: es
  source: https://www.marketscreener.com
---

# MarketScreener — Datos Financieros y Earnings Transcripts Globales

Scraper de **MarketScreener** (plataforma de S&P Capital IQ) que accede a **datos gratuitos sin registro**: earnings transcripts, cotizaciones, perfiles, financials históricos, valuación, consenso de analistas, noticias, insider trading y ratings.

**URL base:** `https://www.marketscreener.com`
**País soportado:** Global (20,000+ stocks, ADRs argentinos incluidos)
**Requiere registro:** ❌ No, **todo es scraping directo**

---

## ⚠️ Lo que MarketScreener ofrece GRATIS (sin registro)

| Funcionalidad | Disponible Gratis | Requiere Pago |
|:---|:---:|:---:|
| **Earnings Transcripts** (contenido completo) | — | 🔒 Premium |
| **Earnings Transcripts** (listado con fechas, quarters, URLs) | ✅ | — |
| **Cotizaciones** (hasta 15 min retraso) | ✅ | — |
| **Perfil de empresa** (descripción, sector, empleados, web) | ✅ | — |
| **Datos financieros** (Income Statement, Balance Sheet, Cash Flow) | ✅ (años recientes) | 🔒 Más años |
| **Valuación** (PE, PB, EV/EBITDA, market cap, dividend yield) | ✅ | — |
| **Consenso de analistas** (target price, recomendaciones, revisiones) | ✅ | — |
| **Ratings** (Surperformance Score: Trader, Investor, Global) | ✅ | — |
| **Noticias** (histórico completo) | ✅ | — |
| **Calendario** (earnings, dividends, splits, AGM) | ✅ | — |
| **Insider Trading** (transacciones de ejecutivos) | ✅ | 🔒 Más detalle |
| **Accionistas** (top shareholders) | ✅ | 🔒 Lista completa |
| **Gobierno corporativo** (board, management) | ✅ | — |
| **Gráficos** (históricos, velas, indicadores técnicos) | ✅ | — |
| **Búsqueda de símbolos** | ✅ | — |
| **Screener avanzado** | — | 🔒 Premium |
| **Datos financieros históricos >3 años** | — | 🔒 Premium |

---

## Cobertura

| Tipo | Cobertura |
|------|-----------|
| **Stocks US** | ✅ Todas (AAPL, MSFT, etc.) |
| **ADRs argentinos** | ✅ GGAL, TGS, BMA, YPF, PAM, etc. |
| **Stocks globales** | ✅ Europa, Asia, Latinoamérica |
| **ETFs** | ✅ |
| **Índices** | ✅ |
| **Bonos** | ❌ No disponible |
| **Forex / Crypto** | ❌ No disponible |

---

## Autenticación

**No requiere API key ni registro.** Todo el contenido es scraping directo de páginas públicas HTML.

---

## Uso Rápido

```python
from marketscreener_client import MarketScreenerClient

client = MarketScreenerClient()

# Último earnings transcript de GGAL
transcript = client.get_transcript("GGAL")
print(transcript["title"])
print(transcript["prepared_remarks"][:500])

# Cotización de AAPL
quote = client.get_quote("AAPL")
print(f"${quote['price']} ({quote['change_pct']}%)")

# Perfil de empresa
profile = client.get_profile("GGAL")
print(profile["name"], profile["industry"])

# Financials
fin = client.get_financials("AAPL", statement="income")
print(fin["2025"]["revenue"])

# Consenso de analistas
consensus = client.get_consensus("AAPL")
print(f"Target: ${consensus['target_mean']}, Recomendación: {consensus['rating']}")
```

---

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| **[marketscreener_client.py](./scripts/marketscreener_client.py)** | Cliente completo con todas las funcionalidades (transcripts, quotes, profile, financials, valuation, consensus, news, ratings, insider, calendar, search) |
| **[marketscreener_cli.py](./scripts/marketscreener_cli.py)** | CLI rápida para consultas diarias |

---

## Buenas Prácticas

1. **Rate limiting**: usar 1 request por segundo como mínimo para evitar bloqueos
2. **User-Agent**: siempre usar un User-Agent de navegador real
3. **Cachear**: los datos de transcripts no cambian después de publicados, cachear localmente
4. **HTML Parsing**: usar BeautifulSoup para parsear HTML, no regex
5. **IDs numéricos**: cada empresa tiene un ID numérico único en MarketScreener (ej: AAPL=4849, GGAL=13491328)
6. **Errores 404**: si no se encuentra una página, puede que la empresa no esté cubierta
