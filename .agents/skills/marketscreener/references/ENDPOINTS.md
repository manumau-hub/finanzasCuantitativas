# MarketScreener — Referencia Completa de Páginas y Datos Gratuitos

Documentación detallada de **todas las páginas gratuitas** de MarketScreener, estructura de URLs, datos disponibles y ejemplos de parsing.

**URL base:** `https://www.marketscreener.com`
**Formato:** HTML (scraping)
**Auth:** Ninguna (gratis sin registro)

---

## 1. Identificación de Empresas (IDs numéricos)

Cada empresa tiene un **ID numérico único** que se usa en todas las URLs. Para encontrar el ID, se usa la búsqueda.

### Búsqueda: `GET /search/?q={ticker}` ✅ Free

**URL:** `https://www.marketscreener.com/search/?q={ticker}`

**Ejemplo:** `https://www.marketscreener.com/search/?q=AAPL`

**Datos obtenidos:**
- Lista de resultados con nombre, ticker, exchange y link a la página de cada empresa
- El link contiene el ID numérico: `/quote/stock/APPLE-INC-4849/` → ID = 4849

**Cómo parsear:**
```python
from bs4 import BeautifulSoup
import requests

r = requests.get("https://www.marketscreener.com/search/?q=AAPL",
                 headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

# Los resultados están en tablas <table class="table">
# Cada fila <tr> tiene: nombre, ticker, exchange, tipo
```

**IDs conocidos de ADRs argentinos:**

| Ticker | Nombre | ID |
|--------|--------|:---:|
| GGAL | Grupo Financiero Galicia | 13491328 |
| TGS | Transportadora de Gas del Sur | 13491332 |
| BMA | Banco Macro | 13491217 |
| YPF | YPF S.A. | 13491303 |
| PAM | Pampa Energía | 13491216 |
| CEYL | Central Puerto | No disponible |

---

## 2. Página Principal (Quote/Summary): `/{id}/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/`

**Ejemplos:**
- `https://www.marketscreener.com/quote/stock/APPLE-INC-4849/`
- `https://www.marketscreener.com/quote/stock/GRUPO-FINANCIERO-GALICIA--13491328/`

**Datos obtenidos:**
- Precio actual (end-of-day o real-time estimate)
- Cambio diario ($ y %)
- Cambio 5-day y YTD
- Exchange, ISIN, Sector/Industria
- Últimas noticias y transcripts
- Links a todas las demás secciones

---

## 3. Earnings Transcripts: `/{id}/news-call-transcripts/` ⚠️ Listado free — Contenido Premium

**El LISTADO de transcripts es gratuito.** La página lista todos los earnings calls disponibles
con títulos, fechas y quarters. Sin embargo, el **contenido completo del transcript está
detrás de un paywall** (requiere suscripción).

**URL listado:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/news-call-transcripts/`

**Ejemplo transcript Q1 2026 GGAL:**
`https://www.marketscreener.com/news/transcript-grupo-financiero-galicia-s-a-q1-2026-earnings-call-may-14-2026-ce7f5bddd188fe23`

**URLs de transcripts siguen este patrón:**
```
/news/transcript-{nombre}-q{numero}-{año}-earnings-call-{fecha}-{hash}
```

**Datos obtenidos (solo del listado, no del contenido completo):**
| Campo | Descripción |
|-------|-------------|
| `title` | Título del earnings call (ej: "Grupo Financiero Galicia S.A., Q1 2026 Earnings Call, May 14, 2026") |
| `date` | Fecha del earnings call |
| `quarter` | Quarter y año (ej: "Q1 2026") |
| `url` | URL del transcript (contenido completo requiere suscripción) |

> ⚠️ **Importante:** El contenido completo del transcript (participantes, prepared remarks,
> Q&A) está **detrás de un paywall**. Solo el listado con títulos, fechas y URLs
> es gratuito.

**Cómo parsear:**
```python
# El transcript está en <div class="transcript"> (o similar)
# Cada sección tiene <p><strong>Operator</strong></p>, <p><strong>Question</strong></p>, etc.
# Los participantes aparecen como "Aaron Rakers (Wells Fargo)" o similar
```

---

## 4. Perfil de Empresa: `/{id}/company/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/company/`

**Datos obtenidos:**
| Dato | Descripción |
|------|-------------|
| `name` | Nombre completo de la empresa |
| `ticker` | Símbolo bursátil |
| `isin` | ISIN |
| `exchange` | Bolsa donde cotiza |
| `industry` | Sector/Industria |
| `description` | Descripción del negocio (párrafo completo) |
| `employees` | Número de empleados |
| `revenue` | Ingresos (último año fiscal) |
| `net_income` | Ingreso neto (último año fiscal) |
| `website` | Sitio web corporativo |
| `country` | País de origen |
| `address` | Dirección |
| `phone` | Teléfono |

---

## 5. Financials: `/{id}/finances/` ✅ Free

**URL base:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/finances/`

**Sub-páginas:**

| Página | URL | Datos |
|--------|-----|-------|
| Income Statement | `/finances-income-statement/` | Revenue, EBITDA, Net Income, EPS (anual y trimestral) |
| Balance Sheet | `/finances-balance-sheet/` | Total Assets, Equity, Debt, Cash |
| Cash Flow | `/finances-cash-flow-statement/` | Operating CF, Free Cash Flow |
| Financial Ratios | `/finances-ratios/` | ROE, ROA, Debt/Equity, Current Ratio, etc. |

**Datos obtenidos (Income Statement):**
| Cuenta | Descripción |
|--------|-------------|
| `revenue` | Ventas netas |
| `ebitda` | EBITDA |
| `operating_income` | Resultado operativo |
| `net_income` | Resultado neto |
| `eps` | Ganancia por acción |
| `dividend_per_share` | Dividendo por acción |
| `gross_margin` | Margen bruto |
| `operating_margin` | Margen operativo |
| `net_margin` | Margen neto |

**Nota:** En plan gratuito se ven los últimos 2-3 años fiscales + últimos trimestres. Para más años requiere Premium (pago).

---

## 6. Valuación: `/{id}/valuation/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/valuation/`

**Datos obtenidos:**
| Ratio | Descripción |
|-------|-------------|
| `pe_ratio` | Price/Earnings |
| `pb_ratio` | Price/Book |
| `ps_ratio` | Price/Sales |
| `ev_ebitda` | EV/EBITDA |
| `ev_sales` | EV/Sales |
| `market_cap` | Capitalización bursátil |
| `enterprise_value` | Valor de empresa |
| `dividend_yield` | Rentabilidad por dividendo |
| `price_to_cash_flow` | Price/Cash Flow |
| `number_of_shares` | Número de acciones |
| `beta` | Beta |
| `volatility` | Volatilidad |
| `52w_high` | Máximo 52 semanas |
| `52w_low` | Mínimo 52 semanas |

---

## 7. Consenso de Analistas: `/{id}/consensus/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/consensus/`

**Datos obtenidos:**
| Dato | Descripción |
|------|-------------|
| `target_mean` | Precio objetivo promedio |
| `target_median` | Precio objetivo mediano |
| `target_high` | Precio objetivo máximo |
| `target_low` | Precio objetivo mínimo |
| `buy` | Nº recomendaciones Comprar |
| `outperform` | Nº Outperform |
| `hold` | Nº Mantener |
| `underperform` | Nº Underperform |
| `sell` | Nº Vender |
| `rating_text` | Resumen textual |
| `target_history` | Historial de precios objetivo |
| `last_update` | Última actualización |

---

## 8. Ratings Surperformance: `/{id}/ratings/` ✅ Free ⭐

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/ratings/`

**Propietario:** Surperformance (MarketScreener mismo)

**Datos obtenidos:**
| Rating | Escala | Descripción |
|--------|:------:|-------------|
| `trader_rating` | 1-10 | Evaluación de corto plazo (trader) |
| `trader_buy` | % | % recomendaciones de compra (trader) |
| `investor_rating` | 1-10 | Evaluación de largo plazo (inversor) |
| `investor_buy` | % | % recomendaciones de compra (inversor) |
| `global_rating` | 1-10 | Rating global combinado |

**Componentes del rating:**
| Componente | Trader | Investor |
|------------|:------:|:--------:|
| Fundamentals | ❌ | ✅ |
| Valuation | ✅ | ✅ |
| EPS Revisions | ✅ (4m) | ✅ (1y) |
| Visibility (Technical) | ✅ | ✅ |

---

## 9. Noticias: `/{id}/news/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/news/`

**Datos obtenidos por artículo:**
| Campo | Descripción |
|-------|-------------|
| `headline` | Titular |
| `date` | Fecha de publicación |
| `source` | Fuente (RE=Reuters, MT=MarketScreener, DJ=Dow Jones, CI=Company, PR=Press Release, ZD=Zacks) |
| `url` | Link al artículo completo |
| `body` | Contenido del artículo (si es texto completo) |

---

## 10. Calendario: `/{id}/calendar/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/calendar/`

**Datos obtenidos:**
| Evento | Descripción |
|--------|-------------|
| `next_earnings` | Próxima fecha de earnings |
| `last_earnings` | Última fecha de earnings |
| `ex_dividend_date` | Fecha ex-dividendo |
| `dividend_payment` | Fecha pago dividendo |
| `agm_date` | Fecha Asamblea General |
| `split_date` | Fecha de split (si aplica) |
| `ipo_date` | Fecha de IPO |

---

## 11. Insider Trading: `/{id}/company-insider-trading/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/company-insider-trading/`

**Datos obtenidos (por transacción):**
| Campo | Descripción |
|-------|-------------|
| `insider_name` | Nombre del insider |
| `position` | Cargo (CEO, CFO, Director, etc.) |
| `transaction_type` | Compra o Venta |
| `transaction_date` | Fecha de la transacción |
| `quantity` | Cantidad de acciones |
| `price` | Precio de la transacción |
| `value` | Valor total de la transacción |

---

## 12. Accionistas: `/{id}/company-shareholders/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/company-shareholders/`

**Datos obtenidos:**
| Campo | Descripción |
|-------|-------------|
| `top_shareholders` | Top accionistas (nombre, %, tipo) |
| `institutional_ownership` | % institucional |
| `insider_ownership` | % de insiders |
| `float` | Acciones en circulación |
| `shares_outstanding` | Acciones emitidas |

---

## 13. Gobierno Corporativo: `/{id}/company-governance/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/company-governance/`

**Datos obtenidos:**
| Sección | Datos |
|---------|-------|
| `board_members` | Nombre, cargo, edad, compensación |
| `management` | Nombre, cargo, compensación |
| `committees` | Comités del board |

---

## 14. ETF Positions: `/{id}/positions/` ✅ Free

**URL:** `https://www.marketscreener.com/quote/stock/{NOMBRE}-{ID}/positions/`

**Datos obtenidos:**
- Lista de ETFs que tienen la acción
- Peso (%) de la acción en cada ETF

---

## Resumen de URLs por funcionalidad

| Funcionalidad | URL Pattern |
|:---|:---|
| **Búsqueda** | `/search/?q={ticker}` |
| **Quote/Summary** | `/quote/stock/{NOMBRE}-{ID}/` |
| **Perfil empresa** | `.../{ID}/company/` |
| **Financials - Income** | `.../{ID}/finances-income-statement/` |
| **Financials - Balance** | `.../{ID}/finances-balance-sheet/` |
| **Financials - Cash Flow** | `.../{ID}/finances-cash-flow-statement/` |
| **Financials - Ratios** | `.../{ID}/finances-ratios/` |
| **Valuación** | `.../{ID}/valuation/` |
| **Consenso analistas** | `.../{ID}/consensus/` |
| **Ratings** | `.../{ID}/ratings/` |
| **Noticias** | `.../{ID}/news/` |
| **Calendario** | `.../{ID}/calendar/` |
| **Insider trading** | `.../{ID}/company-insider-trading/` |
| **Accionistas** | `.../{ID}/company-shareholders/` |
| **Gobierno** | `.../{ID}/company-governance/` |
| **Transcript** | `/news/transcript-{nombre}-q{num}-{año}-...-{hash}/` |

---

## Códigos de Estado HTTP

| Código | Significado | Causa |
|--------|-------------|-------|
| 200 | ✅ OK | Todo funciona |
| 301/302 | Redirección | La URL ha cambiado (seguir Location header) |
| 403 | ❌ Bloqueado | El sitio detectó scraping (rotar User-Agent, usar proxies) |
| 404 | ❌ No encontrado | El ID de empresa no existe o la página no está disponible |
| 429 | ❌ Too Many Requests | Demasiados requests en poco tiempo (aumentar delay) |
| 503 | ❌ Servicio no disponible | El sitio está caído o bloqueando temporalmente |

---

## User-Agents Recomendados

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
```

## Rate Limiting

```python
import time

# Esperar al menos 1.5 segundos entre requests
MIN_DELAY = 1.5  # segundos
last_request = 0.0

def rate_limit():
    global last_request
    elapsed = time.time() - last_request
    if elapsed < MIN_DELAY:
        time.sleep(MIN_DELAY - elapsed)
    last_request = time.time()
```
