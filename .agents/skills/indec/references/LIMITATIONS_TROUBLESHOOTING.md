# LIMITATIONS & TROUBLESHOOTING

> A diferencia de skills basados en APIs no-oficiales (TradingView,
> Google Finance, BYMA), esta API ES OFICIAL del Estado Argentino y tiene
> politicas de no-break ABI. **Es la API mas estable y confiable de
> todo este repo.**
>
> Esta seccion documenta sus limitaciones y los problemas mas comunes.

---

## Indice

1. [Por que esta API es MAS confiable que otras](#1-por-que-esta-api-es-mas-confiable-que-otras)
2. [Limitaciones conocidas](#2-limitaciones-conocidas)
3. [Errores comunes y soluciones](#3-errores-comunes-y-soluciones)
4. [Caveats de los IDs](#4-caveats-de-los-ids)
5. [Caveats de los datos](#5-caveats-de-los-datos)
6. [Que hacer si la API falla](#6-que-hacer-si-la-api-falla)

---

## 1. Por que esta API es MAS confiable que otras

A diferencia de TradingView/Google Finance/BYMA (todas APIs internas no
documentadas), esta API:

| Caracteristica | series-tiempo-ar | TradingView | Google Finance | BYMA |
|----------------|:----------------:|:-----------:|:--------------:|:----:|
| API oficial publica | ✅ | ❌ (interna) | ❌ (interna) | ❌ (interna) |
| Documentacion oficial completa | ✅ | ❌ | ❌ | ❌ |
| Codigo abierto en GitHub | ✅ | ❌ | ❌ | ❌ |
| Politicas de no-break ABI | ✅ | ❌ | ❌ | ❌ |
| Stable desde | 2017+ | ~2017 | ~2010 | ? |
| Cambio de RPC IDs frecuente | Nunca | Eventual | Eventual | Eventual |
| Issue tracker publico | ✅ GitHub | ❌ | ❌ | ❌ |

**Conclusion:** podes construir productos sobre esta API con confianza.
Es muchisimo mas estable que las otras del repo.

---

## 2. Limitaciones conocidas

### A) Maximo 1,000 datapoints por serie por request

**Impacto:** para series largas (>1000 datapoints como dolar diario desde
1990 = 12,000+ datapoints), tenes que paginar con `start` (offset).

**Workaround:** loop con offsets sucesivos.

```python
all_data = []
offset = 0
LIMIT = 1000
while True:
    r = fetch_series(ID, limit=LIMIT, start=offset)
    chunk = r['series'][0]['data']
    if not chunk:
        break
    all_data.extend(chunk)
    if len(chunk) < LIMIT:
        break
    offset += LIMIT
```

### B) `last` incompatible con `sort/start/limit`

Si usas `--last N` no podes combinar con `--sort`, `--start`, `--limit`.

```bash
# ✅ OK
?ids=...&last=12

# ❌ HTTP 400
?ids=...&last=12&sort=desc
?ids=...&last=12&limit=20
```

**El script `fetch_indec.py` ya maneja esto** automaticamente: si pasas
`--last`, ignora los otros tres params.

### C) Multi-serie con frecuencias mezcladas

Si pasas IDs con frecuencias distintas (ej: una mensual + una diaria):

- La API agrega usando la frecuencia mas baja (mensual).
- La serie de mayor frecuencia se colapsa con `avg`.
- Esto puede no ser lo que queres (ej: querias suma, no promedio).

**Workaround:** pasar `collapse + collapse_aggregation` explicitos.

### D) Series DISCONTINUADAS

Muchas series antiguas (IPC GBA Base 2008, censos viejos) estan marcadas
como `SERIE DISCONTINUADA` en `dataset.title`. Las podes consultar pero
no se actualizan.

**Filtrar:**

```python
results = search_series("ipc")
active = [
    r for r in results['data']
    if 'DISCONTI' not in r['dataset']['title'].upper()
]
```

### E) Frecuencia oficial vs frecuencia del response

El campo `meta[1].field.frequency` puede aparecer como `null` en algunas
series. Mejor confiar en `meta[0].frequency` (global).

### F) No hay webhooks ni streaming

Solo polling. Si necesitas data en tiempo real, no es esta API (los
indicadores macro se publican mensual/trimestralmente igual, asi que
streaming no aporta).

### G) Lag de publicacion

Los datos del INDEC tienen lag:

| Indicador | Lag tipico |
|-----------|-----------|
| IPC mensual | ~15 dias (publica mes M a mediados de mes M+1) |
| EMAE mensual | ~25 dias |
| PIB trimestral | ~3 meses |
| EPH trimestral | ~3 meses |
| Pobreza semestral | ~3 meses |

Esto NO es limitacion de la API sino del proceso de publicacion del INDEC.

### H) No hay series intra-mensuales para precios

El IPC se publica mensual. No hay version semanal o diaria desde INDEC
oficial. Para precios diarios hay otros indices privados (no en esta API).

---

## 3. Errores comunes y soluciones

### Error: HTTP 400 "El parametro last no puede ser utilizado..."

**Causa:** combinaste `--last` con `--sort`, `--start` o `--limit`.

**Fix:** elegir uno de los 2 patrones:
- Patron "ultimos N": solo `--last N`.
- Patron "paginacion": solo `--limit N --start OFFSET`.

### Error: HTTP 404 "Serie con ID 'XXX' no encontrada"

**Causa:** typo en el ID o ID inexistente.

**Fix:**
1. Verificar con `validate`:
   ```bash
   py scripts/fetch_indec.py validate "XXX_YYY"
   ```
2. Buscar con keywords:
   ```bash
   py scripts/fetch_indec.py search "XXX_palabra_clave"
   ```

### Error: HTTP 400 "El parametro collapse 'day' es invalido..."

**Causa:** intentaste collapsear a una frecuencia mayor que la serie
(ej: serie mensual con `--collapse day`).

**Fix:** usar collapse igual o menor que la frecuencia de la serie:
- Serie diaria → puede ser collapsed a week/month/quarter/year.
- Serie mensual → solo a quarter/semester/year.
- Serie trimestral → solo a semester/year.

### Error: Response vacio (`data: []`)

**Causas posibles:**
1. `start_date` despues del ultimo datapoint disponible.
2. `end_date` antes del primer datapoint.
3. Serie sin actualizar recientemente.

**Fix:** consultar el rango disponible:

```bash
py scripts/fetch_indec.py series "XXX_YYY" --metadata only
# Mira meta[0].start_date y meta[0].end_date
```

### Error: datapoints `null` al inicio cuando uso representation_mode

**Causa:** `percent_change_a_year_ago` necesita 12 meses previos para
calcular. Los primeros 12 datapoints de la serie tienen `null` porque
no hay valor de "hace 1 año".

**Fix:** filtrar `null`:

```python
data = fetch_series(ID, representation_mode="percent_change_a_year_ago")
valid = [d for d in data['series'][0]['data'] if d['value'] is not None]
```

### Error: HTTPSConnectionPool / timeout

**Causa:** lag de red o server temporal.

**Fix:** reintentar con backoff:

```python
import time
for attempt in range(3):
    try:
        return fetch_series(ID)
    except requests.HTTPError:
        time.sleep(2 ** attempt)
```

### Error: encoding raro en metadata (acentos como ?)

**Causa:** consola Windows (cp1252) no soporta UTF-8.

**Fix:** ya manejado por el script (`sys.stdout.reconfigure(encoding="utf-8")`).
Si seguis viendo `?`:
1. Guardar a archivo con `-o file.json`.
2. O cambiar a consola con soporte UTF-8 (Windows Terminal, PowerShell 7+).

---

## 4. Caveats de los IDs

### Los IDs son criptos

```
145.3_INGNACUAL_DICI_M_38
```

NO intentar adivinar. Usar siempre:
1. `search` para descubrir.
2. `validate` para confirmar.
3. `assets/known_series_ids.json` para los principales pre-mapeados.

### Mismo indicador, multiples IDs

A veces hay multiples series para el "mismo" indicador:
- Frecuencias distintas (mensual, trimestral, anual).
- Bases distintas (2004, 2008, 2016).
- Distintos publicadores (INDEC vs Subsec Prog Macro).

Ejemplo del IPC:
- IPC nivel general Variacion mensual: `145.3_INGNACUAL_DICI_M_38`
- IPC Nucleo: `148.3_INUCLEONAL_DICI_M_19`
- IPC Bienes: `147.3_IBIENESNAL_DICI_T_19`

Saber **cual usar** depende del caso de uso. Ver [SERIES_CATALOG.md](./SERIES_CATALOG.md).

### IDs cambian raramente, pero PUEDEN cambiar

Aunque la API es estable, ocasionalmente:
- Una serie es discontinuada y reemplazada por otra (con nuevo ID).
- Una base es cambiada (de 2008 a 2016).

Verificar periodicamente que los IDs cacheados sigan validos:

```bash
py scripts/fetch_indec.py validate "XXX_YYY_ZZZ"
```

---

## 5. Caveats de los datos

### Variaciones vs Indices

Muchas series del IPC existen en 2 formas:
- **Indice raw** (base dic 2016 = 100): para calcular tus propias variaciones.
- **Variacion mensual %** (ya calculada): para usar directo.

⚠️ NO aplicar `representation_mode=percent_change` a una serie que YA es
una variacion. Aplicar solo a indices raw.

### Series con bases distintas

El IPC Nacional Base 2016 reemplazo al IPC GBA Base 2008. Los valores
NO son comparables directamente entre bases.

### Series desestacionalizadas

EMAE tiene 3 variantes:
- **Serie original**: dato crudo con estacionalidad.
- **Serie desestacionalizada**: ajustada por patrones estacionales.
- **Serie tendencia-ciclo**: suavizada.

Usar la **desestacionalizada** para analisis macro (comparar mes a mes
sin ruido estacional).

### Pesos corrientes vs constantes

Muchos indicadores estan en **pesos corrientes** (no ajustados por
inflacion). Para series largas en Argentina, esto significa que los
valores crecen exponencialmente.

Para deflactar: dividir por el indice IPC del mismo mes (multiplicar
por 100 / IPC).

### Valores en raw currency

Los financials de empresas no-US (como deuda publica) suelen estar en
ARS. Para USD, convertir con tipo de cambio del periodo.

---

## 6. Que hacer si la API falla

### Paso 1: verificar status

```bash
curl -I https://apis.datos.gob.ar/series/api/series?ids=145.3_INGNACUAL_DICI_M_38&last=1
```

Debe retornar 200.

### Paso 2: probar endpoint base

```bash
curl https://apis.datos.gob.ar/series/api/search?q=ipc&limit=1
```

### Paso 3: verificar que el ID no cambio

```bash
py scripts/fetch_indec.py validate "XXX_YYY"
```

Si retorna error 404 pero antes funcionaba, el ID fue discontinuado.
Buscar reemplazo con `search`.

### Paso 4: chequear status de la API

Repositorio GitHub: https://github.com/datosgobar/series-tiempo-ar-api/issues

Si hay un issue activo de "API down", esperar fix.

### Paso 5: providers alternativos

Si la API esta caida temporalmente:

| Para | Plan B |
|------|--------|
| IPC | scraping directo de indec.gob.ar (CSV oficiales) |
| BCRA datos | skill `bcra-macro` (API directa BCRA) |
| Tipo de cambio | skill `data912` (real-time AR) |
| PIB / cuentas nacionales | scraping de minecon.gob.ar |

### Paso 6: cache local

Para reducir dependencia de uptime:

```python
import json
import os
from pathlib import Path

CACHE_DIR = Path("/tmp/indec_cache")
CACHE_DIR.mkdir(exist_ok=True)

def fetch_cached(series_id, ttl_hours=24, **kwargs):
    cache_file = CACHE_DIR / f"{series_id}.json"
    if cache_file.exists():
        age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
        if age_hours < ttl_hours:
            return json.loads(cache_file.read_text())
    data = fetch_series(series_id, **kwargs)
    cache_file.write_text(json.dumps(data))
    return data
```

---

## Checklist pre-production

Para usar este skill en escenarios criticos:

- [ ] Tengo cache de responses con TTL razonable (24hs para mensual, 1mes para anual).
- [ ] Tengo retry con backoff exponencial para errores transitorios.
- [ ] Tengo validacion periodica de IDs cacheados (al menos 1x/mes).
- [ ] Tengo fallback a otro provider del repo si la API falla.
- [ ] Estoy filtrando series DISCONTINUADAS.
- [ ] Estoy usando `metadata=simple` (no `full`) para reducir bandwidth.
- [ ] Estoy usando atajos (`ipc`, `emae`, etc.) en lugar de hardcodear IDs.

Si marcaste todos, **podes usar este skill con MUY alta confianza**. Es
la API mas confiable del repo.
