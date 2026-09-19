# Google Finance — Referencia Completa

> **Google Finance** (`google.com/finance`) es la app de market data de Google.
> NO tiene API publica oficial, pero su SPA web expone un endpoint **RPC
> (Remote Procedure Call) `batchexecute`** que retorna JSON estructurado
> para CUALQUIER simbolo del catalogo global.
>
> SIN API key. SIN autenticacion. Pero con caveats importantes que estan
> documentados en [`LIMITATIONS_TROUBLESHOOTING.md`](./LIMITATIONS_TROUBLESHOOTING.md).

---

## Indice

1. [Resumen de endpoints](#1-resumen-de-endpoints)
2. [Bypass del consent screen](#2-bypass-del-consent-screen)
3. [Endpoint principal: batchexecute](#3-endpoint-principal-batchexecute)
4. [Formato del request](#4-formato-del-request)
5. [Formato del response (wrb.fr)](#5-formato-del-response-wrbfr)
6. [Manejo de errores](#6-manejo-de-errores)
7. [Documentos relacionados](#7-documentos-relacionados)

---

## 1. Resumen de endpoints

| # | URL | Metodo | Uso |
|---|-----|--------|-----|
| 1 | `/finance/beta/_/FinHubUi/data/batchexecute?rpcids={RPC_ID}` | POST | **El endpoint principal** — invoca cualquier RPC interno |
| 2 | `/finance/beta/quote/{TICKER}:{EXCHANGE}` | GET | HTML SPA (sin consent screen) — contiene los chunks `AF_initDataCallback` con la data SSR |
| 3 | `/finance/quote/{TICKER}:{EXCHANGE}` | GET | HTML SPA (redirige a `consent.google.com` sin cookies) |

**Total: 1 endpoint REST (`batchexecute`) + 2 URLs HTML** (las 2 ultimas son alternativas).

---

## 2. Bypass del consent screen

### Problema

Las URLs "stable" (`/finance/quote/...`) redirigen automaticamente a
`consent.google.com` para pedir aceptacion de cookies de tracking, lo que
hace que el cliente reciba HTML del consent (titulo "Antes de continuar")
en lugar del HTML real del simbolo.

### Solucion 1 — Usar URLs `/beta/` directo

```python
# Esto NO redirige a consent screen:
url = "https://www.google.com/finance/beta/quote/GGAL:NASDAQ"
url = "https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute"
```

**Recomendado para todo nuevo desarrollo.** Es lo que usa el script
`fetch_gfinance.py`.

### Solucion 2 — Pasar cookies de consent

```python
COOKIES = {
    "CONSENT": "PENDING+999",
    "SOCS": "CAESHAgBEhJnd3NfMjAyNTAxMjMtMF9SQzMaAmVuIAEaBgiAvLW8Bg",
}
requests.get(url, cookies=COOKIES)
```

Con estas cookies, **incluso la URL stable redirige a `/beta/`** y devuelve
el HTML real. Si Google rota las cookies y deja de funcionar, capturar
unas frescas con un browser real (DevTools → Network → ver cookies de
una request exitosa). Guardar como `assets/consent_cookies.json`.

---

## 3. Endpoint principal: batchexecute

**URL:** `POST https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute`

Este es el endpoint XHR que Google Finance usa para hidratar datos
client-side. Implementa el protocolo **Wiz batchexecute** de Google
(tambien usado en Search, Maps, Translate, etc).

### Headers requeridos

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "X-Same-Domain": "1",                                  # CRITICO
    "Origin": "https://www.google.com",
    "Referer": "https://www.google.com/finance/quote/...", # ayuda a no ser bloqueado
}
```

> ⚠️ **`X-Same-Domain: 1` es crítico**. Sin este header puede que la API
> rechace el request por considerar que viene de otro origen.

### Query params

| Param | Tipo | Descripcion |
|-------|------|-------------|
| `rpcids` | str | ID del RPC a ejecutar (ej: `gCvqoe`). Se pueden encadenar multiples con coma. |
| `source-path` | str | Path original del usuario (ej: `/finance/quote/GGAL:NASDAQ`). Sirve para deduping y telemetria. |
| `f.sid` | str | Session ID (`-1` para anonymous). |
| `bl` | str | Build version del backend (ej: `boq_finhub-uiserver_20260531.09_p2`). |
| `hl` | str | Idioma (`en`, `es`). |
| `_reqid` | str | Request ID monotonico (cualquier numero entero). |
| `rt` | str | Response type (`c` para compact). |

---

## 4. Formato del request

El body es `application/x-www-form-urlencoded` con un solo campo: `f.req`.

### Estructura del `f.req`

```json
[[["RPC_ID", "JSON_args_serialized_as_string", null, "generic"]]]
```

Es decir: triple-array donde cada item es una tupla `(rpc_id, json_args, null, "generic")`.

### Ejemplo (quote de GGAL:NASDAQ via gCvqoe)

```python
import json, requests

rpc_id = "gCvqoe"
# Args del RPC — diferente por cada RPC (ver references/RPC_IDS.md)
rpc_args = [[[None, ["GGAL", "NASDAQ"]]], 1]
rpc_args_json = json.dumps(rpc_args, separators=(",", ":"))

f_req = json.dumps([[[rpc_id, rpc_args_json, None, "generic"]]], separators=(",", ":"))

r = requests.post(
    "https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute",
    params={
        "rpcids": rpc_id,
        "source-path": "/finance/quote/GGAL:NASDAQ",
        "f.sid": "-1",
        "bl": "boq_finhub-uiserver_20260531.09_p2",
        "hl": "en",
        "_reqid": "1",
        "rt": "c",
    },
    data={"f.req": f_req},
    headers={
        "X-Same-Domain": "1",
        "Origin": "https://www.google.com",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.google.com/finance/quote/GGAL:NASDAQ",
    },
    cookies={
        "CONSENT": "PENDING+999",
        "SOCS": "CAESHAgBEhJnd3NfMjAyNTAxMjMtMF9SQzMaAmVuIAEaBgiAvLW8Bg",
    },
)
```

### RPC IDs disponibles

| RPC ID | Descripcion |
|--------|-------------|
| `gCvqoe` | Quote basico |
| `dlNq8b` | Quote enriquecido |
| `JL8oKc` | Descripcion empresa profundo |
| `SICF5d` | Peers / related stocks |
| `YTM9q` | Analyst recommendations + opinions |
| `XxQsbd` | Earnings history |
| `gXxkFd` | Ratings tecnicos |
| `Pr8h2e` | Financials masivos (income/balance/cashflow) |
| `c2u4wc` | OHLC (4 variantes segun args: intraday 1-min/5-min, daily 1m/6m) |
| `kA4MVd` | News (2 variantes segun args: globales o symbol-specific) |
| `hgueg` | Indices globales |
| `vNewwe` | Sectors heatmap |

> Catalogo estructurado + args templates en
> [`../assets/rpc_ids.json`](../assets/rpc_ids.json).
> Detalles completos en [`RPC_IDS.md`](./RPC_IDS.md).

---

## 5. Formato del response (wrb.fr)

Google usa un formato custom llamado **wrb.fr** (Wiz response batch.framework).

### Estructura

```
)]}'

<size>
[["wrb.fr","<rpcId>","<JSON_serialized_payload>",null,null,null,"generic"], ...]
<size>
[["di",N],["af.httprm",N,"<hash>",N]]
```

| Componente | Significado |
|------------|-------------|
| `)]}'` | XSSI guard prefix (4 chars) — strip antes de parsear |
| `<size>` | Numero entero = bytes de la siguiente linea |
| `["wrb.fr", rpc_id, payload, ...]` | El response real |
| `payload` | **JSON serializado dentro de string** — necesita doble `json.loads` |

### Parser de referencia

Ver implementacion completa en
[`fetch_gfinance.py:parse_wrbfr()`](../scripts/fetch_gfinance.py) y
explicacion detallada en [`RESPONSE_FORMAT.md`](./RESPONSE_FORMAT.md).

```python
def parse_wrbfr(text):
    if not text.startswith(")]}'"):
        return []
    body = text[4:].strip()
    results = []
    for line in body.split("\n"):
        line = line.strip()
        if not line or line.isdigit():
            continue
        try:
            arr = json.loads(line)
        except json.JSONDecodeError:
            continue
        for item in arr:
            if (isinstance(item, list) and len(item) >= 3
                and item[0] == "wrb.fr" and item[2]):
                parsed = json.loads(item[2])  # doble parse!
                results.append((item[1], parsed))
    return results
```

### Estructura del payload por RPC

Cada RPC retorna su propio shape (array anidado SIN keys). Los layouts
posicionales (que indice corresponde a que campo) estan documentados en
[`../assets/chunk_layouts.json`](../assets/chunk_layouts.json).

---

## 6. Manejo de errores

| Status | Causa tipica | Que hacer |
|--------|--------------|-----------|
| 200 OK | Response correcto. Verificar que `parse_wrbfr()` no devuelva `[]` (significa error en payload). | — |
| 400 | `f.req` malformed o RPC inexistente. | Validar el JSON anidado del payload. |
| 403 | Faltan cookies o Origin/Referer. | Pasar cookies de consent y headers completos. |
| 404 | Path incorrecto (typo en `/finance/beta/_/FinHubUi/data/batchexecute`). | Verificar el path exacto en `LIMITATIONS_TROUBLESHOOTING.md`. |
| 500 | Backend de Google fallo. | Reintentar con backoff. |

### Response 200 pero `data: []`

Probable que el RPC necesite args distintos. Ver `RPC_IDS.md` para los args templates correctos.

### Response 200 con `wrb.fr` pero payload `null`

Probable que el simbolo no exista en la base de Google Finance, o el
formato del ticker sea invalido (`NASDAQ:GGAL` vs `GGAL:NASDAQ`).

> Documentacion exhaustiva de troubleshooting en
> [`LIMITATIONS_TROUBLESHOOTING.md`](./LIMITATIONS_TROUBLESHOOTING.md).

---

## 7. Documentos relacionados

| Documento | Contenido |
|-----------|-----------|
| [`RPC_IDS.md`](./RPC_IDS.md) | Tabla detallada de cada RPC con args templates, output shapes, ejemplos |
| [`RESPONSE_FORMAT.md`](./RESPONSE_FORMAT.md) | Parser deep dive del protocolo wrb.fr, edge cases, multi-RPC batching |
| [`LIMITATIONS_TROUBLESHOOTING.md`](./LIMITATIONS_TROUBLESHOOTING.md) | **⚠️ LECTURA OBLIGATORIA antes de usar.** Limitaciones conocidas, warnings, recomendaciones, plan B si la API cambia |
| [`COOKBOOK.md`](./COOKBOOK.md) | Recetas listas para copy-paste de los casos mas comunes |
| [`../assets/rpc_ids.json`](../assets/rpc_ids.json) | Catalogo JSON de RPCs |
| [`../assets/chunk_layouts.json`](../assets/chunk_layouts.json) | Layouts posicionales de los arrays |
| [`../assets/consent_cookies.json`](../assets/consent_cookies.json) | Cookies de bypass del consent screen |
