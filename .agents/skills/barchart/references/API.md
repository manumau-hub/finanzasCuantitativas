# Barchart — Internal API Investigation

Documentación de la API interna de Barchart.com descubierta durante el desarrollo del skill. Sirve como punto de partida para futuros intentos de extracción de datos que requieran acceso a la API.

---

## Autenticación

La API interna de Barchart usa el framework Laravel y requiere:

1. **Cookies de sesión**: Se obtienen visitando cualquier página de Barchart (`/stocks/quotes/{TICKER}`)
2. **XSRF-TOKEN**: Laravel genera un token CSRF que se envía como cookie y debe reenviarse como header `X-XSRF-TOKEN`
3. **Headers requeridos**:
   - `X-XSRF-TOKEN`: El valor decodificado (URL-decode) de la cookie `XSRF-TOKEN`
   - `Accept: application/json, text/plain, */*`
   - `Referer`: La página desde la que se hace la llamada

### Ejemplo de sesión con Python:

```python
import requests, urllib.parse

BASE = 'https://www.barchart.com'
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 ...'})

# 1. Obtener cookies
s.get(f'{BASE}/stocks/quotes/{TICKER}/related-etfs')

# 2. Extraer XSRF token
xsrf = None
for c in s.cookies:
    if 'XSRF' in c.name:
        xsrf = urllib.parse.unquote(c.value)
        break

# 3. Llamar API
headers = {
    'X-XSRF-TOKEN': xsrf,
    'Accept': 'application/json',
    'Referer': f'{BASE}/stocks/quotes/{TICKER}/related-etfs',
}
r = s.get(f'{BASE}/proxies/core-api/v1/quotes/get?symbols={TICKER}&lists=...', headers=headers)
```

---

## Endpoint descubierto: `/proxies/core-api/v1/quotes/get`

### URL base
```
https://www.barchart.com/proxies/core-api/v1
```

También existe `/api/v1` en el código AngularJS (`API_URL = "/api/v1"`) pero devuelve 401 directamente. El proxy `/proxies/core-api/v1` es el que funciona con cookies.

### Parámetros del endpoint

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `symbols` | Ticker(s) separados por coma | `GGAL` |
| `lists` | Lista/filtro de datos a consultar | `etfs.related.toStock` |
| `fields` | Campos a retornar (separados por coma) | `symbol,symbolName,percentHolding` |
| `orderBy` | Campo por el que ordenar | `percentHolding` |
| `orderDir` | Dirección de orden | `asc`, `desc` |
| `limit` | Límite de resultados | `20` |
| `page` | Número de página | `1` |
| `raw` | Si es `1`, incluye datos raw en la respuesta | `1` |
| `meta` | Metadatos de los campos | `field.shortName` |
| `groupBy` | Agrupación | `symbol` |

### Posibles valores de `lists`

| List | Resultado |
|------|-----------|
| `etfs.related.toStock` | Devuelve el stock mismo (no ETFs relacionados) |
| `etfs.relatedToStock` | Ídem |
| `etfs.related.stock` | Ídem |
| `stocks.related.etfs` | Ídem |
| `etfs.holdings` | No probado con éxito (requiere symbol de ETF) |

**Nota:** Todos los lists probados devuelven el mismo stock que se pasa como `symbols`, no los ETFs que lo contienen. Es posible que el list correcto tenga un nombre diferente no descubierto.

### Ejemplo de respuesta (vacía para datos de ETFs relacionados)

```json
{
  "count": 0,
  "total": 0,
  "data": []
}
```

Ejemplo de respuesta exitosa (pero solo devuelve el stock):

```json
{
  "count": 1,
  "total": 1,
  "data": [
    {
      "symbol": "GGAL",
      "symbolName": "Grupo Fin Galicia ADR",
      "percentHolding": "N/A",
      "lastPrice": "48.33"
    }
  ],
  "errors": null
}
```

---

## Endpoint `/views` (incompleto)

El código AngularJS revela un endpoint `/views` que parece mapear nombres de vista a configuraciones de API:

```
API_URL = "/api/v1"
GET /api/v1/views → lista de vistas guardadas
GET /api/v1/views/{viewName} → configuración de una vista
POST /api/v1/views → guardar vista
PUT /api/v1/views/{id} → actualizar vista
DELETE /api/v1/views/{id} → eliminar vista
```

- `/api/v1/views` devuelve 401 (requiere auth de más alto nivel)
- `/proxies/core-api/v1/views` devuelve 500

Probablemente el `viewName=main` en la URL de Related ETFs (`?viewName=main&orderBy=weightInEtf&orderDir=desc`) mapea a una configuración que define qué `lists` usar, pero no se pudo acceder a este recurso.

---

## Arquitectura AngularJS descubierta

### Módulo `RelatedEtfs`

Descubierto en `app-N6USK3DX.js`:

```javascript
// Config de la API
constant("RelatedEtfsApiConfig", {
  api: {
    method: "/quotes/get",
    symbols: "GGAL",
    lists: "etfs.related.toStock",
    fields: "symbol,symbolName,percentHolding,percentChange3m",
    orderBy: "percentHolding",
    orderDir: "desc",
    meta: "field.shortName",
    limit: 5
  }
});

// Controlador
controller("RelatedEtfsCtrl", function($scope, RelatedEtfsApiFactory) {
  this.getData = function() {
    RelatedEtfsApiFactory.getRelatedEtfsData()
      .then(function(data) { this.content = data; });
  };
  this.getData();
});

// Factory que hace la llamada HTTP
factory("RelatedEtfsApiFactory", function(dataProvider, httpVerbs, ..., apiConfig) {
  function getRelatedEtfsData() {
    var config = RelatedEtfsApiConfig;
    var method = config.api.method || "/quotes/get";
    delete config.api.method;
    return dataProvider.call(
      buildUrl(apiConfig.API_URL + method, config.api),
      httpVerbs.GET
    );
  }
});
```

### Factory genérico `dataProvider`

El `dataProvider.call()` construye la URL final usando `buildUrl()` y el `API_URL` (que es `/api/v1`), y los proxies de Barchart redirigen `/api/v1/*` a `/proxies/core-api/v1/*`.

---

## Datos no obtenibles vía API con requests simple

| Endpoint | Método | Resultado |
|----------|--------|-----------|
| `GET /proxies/core-api/v1/quotes/get?symbols=X&lists=etfs.related.toStock&fields=...` | GET | Solo devuelve el stock (no los ETFs) |
| `POST /proxies/core-api/v1/quotes/get` | POST | Mismo resultado que GET |
| `GET /proxies/core-api/v1/views` | GET | 500 Internal Error |
| `GET /proxies/core-api/v1/views/main` | GET | 500 Internal Error |
| `GET /api/v1/views` | GET | 401 Unauthenticated (Laravel) |
| `GET /proxies/core-api/v1/holdings?symbol=X` | GET | 500 |
| `GET /proxies/core-api/v1/etfs/holdings?symbol=X` | GET | 500 |

---

## Posible vía alternativa

Para acceder a datos que se renderizan completamente con AngularJS (como la tabla de Related ETFs), las opciones son:

1. **Headless browser** (Playwright/Selenium): Ejecutar el JS y capturar la respuesta de red del XHR a `/proxies/core-api/v1/quotes/get` — esto revelaría el endpoint exacto y los parámetros que AngularJS construye en runtime
2. **Analizar el bundle JS offline**: El archivo `app-N6USK3DX.js` (~2.9MB) contiene todo el código de Angular de Barchart. Se podría buscar offline con herramientas como `uglifyjs --beautify` para encontrar el list correcto
3. **Interceptar con Chrome DevTools Protocol**: Similar a #1 pero más controlado

---

## Referencias en el código

- JS Bundle principal: `https://assets.barchart.com/build/app-N6USK3DX.js`
- Vendor JS: `https://assets.barchart.com/build/js/barchart-utilities.min.js`
- Módulo Angular: `RelatedEtfs` → archivo `rre.js` en el bundle
- Factory: `RelatedEtfsApiFactory` → función `ere`
- Controlador: `RelatedEtfsCtrl` → función `Qie`
- API_URL encontrada: `/api/v1` (constante en el bundle)
