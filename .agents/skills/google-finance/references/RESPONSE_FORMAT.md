# Response Format — Parser del protocolo wrb.fr

> El endpoint `batchexecute` de Google retorna data en un formato custom
> llamado **wrb.fr** (Wiz Response Batch.framework). Este documento explica
> el formato con todos los edge cases y como parsearlo correctamente.

---

## Indice

1. [Estructura del response](#1-estructura-del-response)
2. [Por que tiene XSSI guard](#2-por-que-tiene-xssi-guard)
3. [Doble JSON parse](#3-doble-json-parse)
4. [Multi-RPC batching](#4-multi-rpc-batching)
5. [Edge cases](#5-edge-cases)
6. [Implementacion de referencia](#6-implementacion-de-referencia)
7. [Errores comunes](#7-errores-comunes)

---

## 1. Estructura del response

Un response tipico se ve asi (cuerpo en text/plain):

```
)]}'

500
[["wrb.fr","gCvqoe","[[[[\"/m/0clbgbw\",[\"GGAL\",\"NASDAQ\"],\"Grupo Financiero Galicia SA\",0,\"USD\",[48.62,0.29,0.60,2,2,2],null,48.33,...]]]]",null,null,null,"generic"],["di",158],["af.httprm",157,"-3931642880561185143",15]]
25
[["e",4,null,null,536]]
```

### Componentes

| Componente | Descripcion |
|------------|-------------|
| `)]}'\n\n` | **XSSI guard prefix** — 4 chars (`)]}'`) + 2 newlines. NO es JSON valido por si solo. Strip antes de parsear. |
| `500\n` | **Numero entero seguido de newline** — indica bytes de la SIGUIENTE linea. Util para streaming, ignorable para parsing batch. |
| `[["wrb.fr", ...], ["di", N], ["af.httprm", ...]]` | **Lineas JSON** con entries de respuesta. Solo nos interesan las `wrb.fr`. |
| `25\n[["e",4,null,null,536]]` | **Trailer** con metricas (puede aparecer mas de uno). |

### Significado de cada entry

| Entry tag | Que significa | Si nos importa |
|-----------|---------------|----------------|
| `"wrb.fr"` | **W**iz **R**esponse **B**atch **fr**ame — el payload del RPC | ✅ ESTO ES LO QUE QUEREMOS |
| `"di"` | Duration info — tiempo de procesamiento server-side | ❌ |
| `"af.httprm"` | HTTP metric trailer — para profiling de Google | ❌ |
| `"e"` | End marker con stats | ❌ |
| `"er"` | Error marker (en responses con error) | ⚠️ Si aparece = el RPC fallo |

---

## 2. Por que tiene XSSI guard

El prefix `)]}'\n\n` es una **proteccion contra ataques XSSI** (Cross-Site
Script Inclusion). Antes era posible que un sitio malicioso incluyera
una API que retorna JSON via `<script src="...">` y leyera la respuesta
manipulando el prototype. Para prevenirlo, Google (y otros como Facebook)
agregan un prefix que hace el response INVALIDO como JavaScript pero
parseable como JSON despues de strippearlo.

**Implementacion practica:**

```python
text = response.text
if text.startswith(")]}'"):
    text = text[4:]  # strip 4 chars (no necesitas saltar los \n, json.loads tolera whitespace)
```

---

## 3. Doble JSON parse

El payload del RPC viene como **JSON serializado dentro de un string**.
Es decir, esta JSON-stringified dos veces.

### Ejemplo

```json
["wrb.fr","gCvqoe","[[[[\"/m/0clbgbw\",[\"GGAL\",\"NASDAQ\"],...]]]]",null,null,null,"generic"]
                   ^ Notar las "" alrededor — es un string dentro del array
```

El elemento `item[2]` es un string `"[[[[\"/m/0clbgbw\",...]]]]"`. Para
obtener el array real hay que hacer DOS json.loads:

```python
# Primer parse: la linea entera
line = '[["wrb.fr","gCvqoe","[[[[\\"/m/0clbgbw\\",...]]]]",null,...]]'
arr = json.loads(line)
# arr[0] = ["wrb.fr", "gCvqoe", "[[[[\"/m/0clbgbw\",...]]]]", null, null, null, "generic"]

# Segundo parse: el payload del item
payload_str = arr[0][2]  # Es un string!
payload = json.loads(payload_str)
# payload = [[[["/m/0clbgbw", ["GGAL","NASDAQ"], ...]]]]
```

### Por que doble parse?

Para que cada RPC pueda tener su shape arbitrario sin afectar el formato
del batch container. Tambien permite que el servidor cache responses
individuales sin re-parsear el JSON ya generado.

---

## 4. Multi-RPC batching

El endpoint soporta **invocar multiples RPCs en una sola request**.

### Request multi-RPC

```python
f_req = json.dumps([[
    ["gCvqoe", '[[[null,["GGAL","NASDAQ"]]],1]', None, "generic"],
    ["JL8oKc", '[[[null,["GGAL","NASDAQ"]]]]', None, "generic"],
    ["YTM9q",  '[[null,["GGAL","NASDAQ"]]]', None, "generic"],
]])
params["rpcids"] = "gCvqoe,JL8oKc,YTM9q"  # coma-separated
```

### Response multi-RPC

```
)]}'

500
[
  ["wrb.fr","gCvqoe","[...]","null,null,null,"generic"],
  ["wrb.fr","JL8oKc","[...]",null,null,null,"generic"],
  ["wrb.fr","YTM9q","[...]",null,null,null,"generic"],
  ["di", N],
  ["af.httprm", ...]
]
```

Todos los wrb.fr aparecen en el mismo array. El parser debe iterar y
matchear por `rpc_id` (item[1]).

### Ventajas del batching

- **1 round-trip en vez de 3** → mas rapido
- **Atomicidad relativa** — si uno falla, los otros siguen
- **Menos overhead de auth/cookies** por request

---

## 5. Edge cases

### A) Response sin XSSI prefix

Algunos errores 400/403/404 retornan **HTML estandar** sin el prefix:

```html
<!DOCTYPE html>
<html lang=en>
  <title>Error 404 (Not Found)!!1</title>
  ...
```

**Manejo:**

```python
if not text.startswith(")]}'"):
    # Es probable HTML de error de Google
    raise ValueError(f"Response sin XSSI prefix — probable error: {text[:300]}")
```

### B) Response con `"er"` (error marker)

Cuando un RPC valido falla server-side, Google retorna un marker `"er"`:

```json
[["er", null, null, null, null, 400, null, null, null, 3], ["di", 10], ...]
```

**Manejo:**

```python
for item in arr:
    if isinstance(item, list) and item and item[0] == "er":
        error_code = item[5]  # 400, 500, etc.
        raise ValueError(f"Server-side error code {error_code}")
```

### C) Payload string vacio o null

A veces el RPC retorna OK pero con payload vacio:

```json
["wrb.fr","RiQiSd","",null,null,null,"generic"]
```

**Manejo:**

```python
payload_str = item[2]
if not payload_str:
    payload = None  # o []
else:
    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        payload = payload_str  # raw string
```

### D) Lineas que son solo numeros

Las lineas `500\n`, `25\n` etc. son metadata de tamaño y NO contienen
JSON. Hay que skippearlas:

```python
for line in body.split("\n"):
    line = line.strip()
    if not line or line.isdigit():  # skip empty or numeric
        continue
    arr = json.loads(line)
    ...
```

### E) Caracteres Unicode escapados

El payload puede contener `&` (`&`), `<` (`<`), etc. Esto NO es
problema porque `json.loads` los maneja automaticamente. Pero si haces
regex sobre el string crudo, tener en cuenta que `&` aparece como `&`.

### F) Response chunked / streamed

El endpoint puede usar `Transfer-Encoding: chunked`. **`requests`** lo
maneja automaticamente — no hay que hacer nada especial.

### G) Multiples bloques `wrb.fr` con el mismo rpcId

Cuando llamas un solo RPC, deberia haber un solo `wrb.fr` con ese ID.
Pero en el HTML SSR, el mismo RPC ID puede aparecer multiples veces
(ej: `gCvqoe` aparece como `ds:2` Y `ds:13`). Si haces multi-RPC batching
con el mismo RPC duplicado, vienen ambos responses — distinguir por
**orden** o por hash del args.

---

## 6. Implementacion de referencia

Parser robusto que maneja todos los edge cases:

```python
import json
import requests


def parse_wrbfr(text: str) -> list[tuple[str, any]]:
    """Parse del response wrb.fr de Google.

    Returns:
        Lista de (rpc_id, payload) para cada wrb.fr en el batch.
        Items con payload vacio se retornan con payload=None.
        Si hay error marker "er", se ignora silenciosamente (manejarlo upstream).
    """
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
            if not isinstance(item, list) or len(item) < 3:
                continue
            if item[0] != "wrb.fr":
                continue
            rpc_id = item[1]
            payload_str = item[2]
            if not payload_str:
                results.append((rpc_id, None))
                continue
            try:
                payload = json.loads(payload_str)  # ← DOBLE PARSE
            except json.JSONDecodeError:
                payload = payload_str
            results.append((rpc_id, payload))
    return results


def call_rpc(rpc_id: str, args: list, headers: dict, cookies: dict) -> any:
    """Invoca un RPC y retorna su payload."""
    rpc_args_json = json.dumps(args, separators=(",", ":"))
    f_req = json.dumps([[[rpc_id, rpc_args_json, None, "generic"]]],
                       separators=(",", ":"))
    r = requests.post(
        "https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute",
        params={
            "rpcids": rpc_id,
            "source-path": "/finance",
            "f.sid": "-1",
            "bl": "boq_finhub-uiserver_20260531.09_p2",
            "hl": "en",
            "_reqid": "1",
            "rt": "c",
        },
        data={"f.req": f_req},
        headers=headers,
        cookies=cookies,
        timeout=30,
    )
    r.raise_for_status()
    parsed = parse_wrbfr(r.text)
    if not parsed:
        return None
    # Match por rpc_id, o devolver el primero
    for rid, data in parsed:
        if rid == rpc_id:
            return data
    return parsed[0][1]
```

---

## 7. Errores comunes

### Error: "Expecting value: line 1 column 1 (char 0)"

**Causa:** No strippeaste el XSSI prefix `)]}'`.

**Fix:**
```python
text = response.text
if text.startswith(")]}'"):
    text = text[4:]
data = json.loads(text)  # ← ERROR si no strippeas
```

### Error: el payload es un string, no un dict/list

**Causa:** No hiciste el doble JSON parse.

**Fix:**
```python
arr = json.loads(line)
payload = json.loads(arr[0][2])  # ← agregar este segundo parse
```

### Error: matched response esta vacio

**Causa:** El `rpc_id` no matchea el que retorno el server. Casos:

1. Pasaste un RPC ID con typo (case-sensitive: `gCvqoe` ≠ `gcvqoe`).
2. El server retorno un error con `"er"` en lugar de `"wrb.fr"`.
3. El RPC requiere args especificos que pasaste vacios.

**Fix:**
```python
parsed = parse_wrbfr(r.text)
print(parsed)  # debug: ver que rpc_ids retornaron
```

### Error: HTTP 400 "f.req invalid"

**Causa:** El payload del `f.req` esta mal serializado. Issues comunes:

1. `rpc_args` NO esta serializado a string (debe ser string JSON, no array):
   ```python
   # ❌ MAL
   f_req = json.dumps([[[rpc_id, [some, args], None, "generic"]]])
   # ✅ BIEN
   rpc_args_json = json.dumps([some, args])
   f_req = json.dumps([[[rpc_id, rpc_args_json, None, "generic"]]])
   ```

2. Estructura triple-array faltante (deben ser **3 `[`** al inicio):
   ```python
   # ✅ Correcto: [[[ rpc, args, null, "generic" ]]]
   ```

### Error: response 200 pero "wrb.fr" no aparece

**Causa:** Probablemente recibiste HTML de error (consent screen u
otro). Verificar headers y cookies.

```python
if not parsed:
    print(f"Body first 500 chars: {r.text[:500]}")
    # Si ves <html>, faltan cookies/headers.
    # Si ves )]}\' pero ningun wrb.fr, el RPC fallo silenciosamente.
```
