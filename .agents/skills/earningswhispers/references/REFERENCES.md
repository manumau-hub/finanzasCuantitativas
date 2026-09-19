# EarningsWhispers — Referencia Tecnica

Documentacion detallada de la API, estructura del sitio y cobertura global.

**URL base:** `https://www.earningswhispers.com`
**API endpoint:** `GET /api/conferencecalls?t={TICKER}`
**Formato:** JSON (ASP.NET Core MVC)
**Auth:** Ninguna (API publica)
**Cobertura:** Global — 33,500+ stocks trackeados en la plataforma. Cobertura de transcripts para large/mid caps globales: US, Europa, Asia, LatAm, Canada.

---

## 1. Arquitectura del Sitio

EarningsWhispers es un sitio ASP.NET Core (IIS) con jQuery + Bootstrap + D3.js en el frontend.

```
Navegador -> IIS -> ASP.NET MVC -> SQL Server DB -> JSON Response
```

A diferencia de Seeking Alpha, **no tiene anti-bot ni sistema de proteccion** porque los datos se cargan via JavaScript despues de que el usuario llega a la pagina. El endpoint `/api/conferencecalls` es publico y devuelve JSON directamente.

### Flujo de la pagina de transcript

1. Usuario visita `https://www.earningswhispers.com/transcript/{TICKER}` (ej: AAPL)
2. El servidor renderiza HTML basico con placeholders
3. El JS `news.js` ejecuta: `gettranscript("AAPL", null)`
4. `gettranscript()` llama a `GET /api/conferencecalls?t=AAPL`
5. La API devuelve JSON con todos los datos del transcript
6. `news.js` renderiza el contenido en el DOM

### Ventaja para scraping

La API se puede llamar **directamente** sin necesidad de visitar la pagina ni ejecutar JS. El endpoint no requiere:
- Cookies de sesion
- Headers especiales
- API keys
- Autenticacion

---

## 2. API Endpoint

### Request

```
GET https://www.earningswhispers.com/api/conferencecalls?t=GGAL
```

**Parametros:**

| Parametro | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `t` | string | Si | Ticker (GGAL, YPF, TGS, PAM...) |
| `d` | string | No | Fecha en formato YYYY-MM-DD (parece no funcionar) |
| `ccid` | int | No | ID especifico de conference call |

**Headers necesarios:**

```http
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json, text/javascript, */*
X-Requested-With: XMLHttpRequest
Referer: https://www.earningswhispers.com/
```

### Response (200 OK)

```json
[
  {
    "ccid": 132,
    "ticker": "GGAL",
    "company": "Grupo Financiero Galicia S.A.",
    "ccDate": "2026-05-14T11:00:00",
    "ccYear": 2026,
    "ccQtr": 1,
    "speakers": "[{\"speaker\": \"spk00\", \"text\": \"...\"}, ...]",
    "aiSummary": null,
    "summary": null,
    "speakerMap": "{\"spk00\": {\"name\": \"Operator\", \"title\": \"...\"}, ...}",
    "status": ""
  }
]
```

---

## 3. Estructura de los Datos

### Campos del Response

| Campo | Tipo | Descripcion |
|---|---|---|
| `ccid` | int | ID unico de la conference call |
| `ticker` | string | Simbolo bursatil |
| `company` | string | Nombre de la empresa |
| `ccDate` | string | Fecha del call (ISO 8601: `YYYY-MM-DDTHH:MM:SS`) |
| `ccYear` | int | Año fiscal |
| `ccQtr` | int | Quarter fiscal (1-4) |
| `speakers` | string (JSON) | Array de objetos `{speaker, text}` con el transcript completo |
| `speakerMap` | string (JSON) | Objeto que mapea speaker IDs a `{name, title}` |
| `summary` | string? | Resumen ejecutivo (puede ser null) |
| `aiSummary` | string? | Resumen generado por AI (puede ser null) |
| `status` | string | Estado del transcript (usualmente vacio) |

### Formato de speakers

El campo `speakers` es un **string JSON**. Ejemplo parseado:

```json
[
  {"speaker": "spk00", "text": "Good morning, ladies and gentlemen..."},
  {"speaker": "spk05", "text": "Thank you. Thank you, everybody..."},
  {"speaker": "spk12", "text": "Our net income for the quarter..."}
]
```

### Formato de speakerMap

El campo `speakerMap` es un **string JSON**. Ejemplo parseado:

```json
{
  "spk00": {"name": "Operator", "title": "Conference Operator"},
  "spk05": {"name": "Pablo Ferdida", "title": "Head of Investor Relations"},
  "spk12": {"name": "Gonzalo Fernandez-Cobaro", "title": "CFO of Grupo Galicia"},
  "spk07": {"name": "Daniel Vaz", "title": "Analyst, Safra"},
  "spk10": {"name": "Chito Labarta", "title": "Analyst, Goldman Sachs"}
}
```

---

## 4. Tamaños Tipicos de Response

| Ticker | Tamaño JSON | Speakers | Chars totales | Prepared Remarks | Q&A |
|---|---|---|---|---|---|
| AAPL | ~95 KB | ~12 | ~90,000 | ~35,000 | ~55,000 |
| NVDA | ~70 KB | ~10 | ~65,000 | ~30,000 | ~35,000 |
| MSFT | ~70 KB | ~10 | ~65,000 | ~40,000 | ~25,000 |
| GGAL | ~53 KB | ~13 | ~51,000 | ~15,000 | ~36,000 |
| YPF | ~54 KB | ~13 | ~52,000 | ~23,000 | ~28,000 |
| TGS | ~22 KB | ~6 | ~21,000 | ~8,000 | ~12,000 |
| PAM | ~42 KB | ~10 | ~40,000 | ~12,000 | ~26,000 |
| BMA | ~48 KB | ~14 | ~46,000 | ~15,000 | ~31,000 |
| TM (Toyota) | ~90 KB | ~15 | ~85,000 | ~30,000 | ~55,000 |
| BBD (Bradesco) | ~150 KB | ~20+ | ~140,000 | ~50,000 | ~90,000 |

---

## 5. Discovery del Endpoint

El endpoint fue descubierto analizando el JS de `news.js`:

```javascript
async function gettranscript(t, d) {
    let url = `/api/conferencecalls?t=${encodeURIComponent(t)}`;
    if (d) {
        url += `&d=${encodeURIComponent(d)}`;
    }
    fetch(url)
        .then(r => r.json())
        .then(data => {
            const json = Array.isArray(data) ? data[0] : data;
            ccTitle(json.company, json.ccQtr, json.ccYear, json.ccDate);
            renderConferenceCall(json);
            showCCSum(json.summary, json.status);
        });
}
```

Fuente: [news.js linea ~600](https://www.earningswhispers.com/js/news.js)

---

## 6. Funciones del Frontend Relevantes

En `news.js` se encontraron las siguientes funciones de renderizado:

| Funcion | Proposito |
|---|---|
| `gettranscript(t, d)` | Llama a la API y renderiza el transcript |
| `renderConferenceCall(json)` | Renderiza speakers en el DOM |
| `showCCSum(summary, status)` | Muestra resumen ejecutivo |
| `ccTitle(company, qtr, year, date)` | Setea el titulo de la pagina |
| `getquote(ticker)` | Obtiene cotizacion en tiempo real |

---

## 7. Cobertura del Sitio

### Tamaño de la base de datos

Segun el analisis del sitemap del sitio:

| Fuente | Cantidad |
|---|---|
| URLs totales en sitemaps | ~152,707 |
| Tickers unicos con pagina dedicada (`/more/{TICKER}`) | ~33,528 |
| Paginas de transcript individuales | No expuestas en sitemap (cargadas via JS) |
| Empresas con transcripts disponibles | Proporcion significativa de los ~33,528 |

### Que determina si un ticker tiene transcript?

La API devuelve datos solo si la empresa tiene **earnings conference calls registrados** en la base de datos de EarningsWhispers. Esto aplica tipicamente a:

- Empresas publicas listadas en NYSE, NASDAQ, TSX, LSE, etc.
- ADRs de mercados emergentes
- Empresas que realizan earnings calls trimestrales publicos

### Tickers sin transcript

| Categoria | Ejemplos | Motivo |
|---|---|---|
| ETFs | SPY, QQQ, ARKK | No hacen earnings calls |
| Bonds/Tesorerias | — | No son empresas |
| Ticker incorrecto | GOOGL -> GOOG | Alphabet usa GOOG |
| Ticker incorrecto | WALMEX -> WMMVY | WM Mexico usa WMMVY |
| No cubiertos | SONY, SAN, BNS, TCS | No estan en la base de datos |

### Notas sobre tickers alternativos

| Ticker que falla | Alternativa que funciona |
|---|---|
| GOOGL | GOOG |
| WALMEX | WMMVY |
| SNE (antiguo Sony) | No disponible |
| CRESY / IRS | No disponibles (ADRs sin transcripts) |

---

## 8. Limitaciones Conocidas

1. **Unico transcript**: La API devuelve solo el transcript mas reciente por ticker
2. **Sin paginacion**: No hay forma de obtener transcripts historicos via la API publica
3. **Sin search**: No hay endpoint publico para buscar tickers por nombre
4. **Cobertura no exhaustiva**: ~80% de large caps globales tienen cobertura. ETFs, small caps y empresas sin earnings calls no estan cubiertas.
5. **Dependencia externa**: Si EarningsWhispers cambia su API, el skill se rompe
6. **Sin SSL client certificate**: No aplica, es HTTP publico
7. **GOOGL vs GOOG, WALMEX vs WMMVY**: Algunos tickers tienen multiples variantes

---

## 9. Comparativa con Otras Fuentes

| Aspecto | EarningsWhispers (este skill) | MarketScreener | Seeking Alpha |
|---|---|---|---|
| Contenido | Transcript COMPLETO | Solo titulos/fechas | Transcript COMPLETO |
| Acceso | API publica, sin auth | Scraping HTML | PerimeterX anti-bot |
| Anti-bot | Ninguno | Cloudflare (leve) | PerimeterX (fuerte) |
| Formato | JSON estructurado | HTML | HTML + JS |
| Cobertura | Global (US, EU, ASIA, LatAm) | Global | Global |
| Contenido premium | No, todo gratis | Si, contenido completo es premium | Algunos premium |
| Dificultad scraping | Facil (API directa) | Media | Dificil (requiere cookies) |
