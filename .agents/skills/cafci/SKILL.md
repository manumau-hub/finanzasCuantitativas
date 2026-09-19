---
name: cafci
description: "Datos de fondos comunes de inversion argentinos via CAFCI (Camara Argentina de Fondos Comunes de Inversion). Combina catalogo JSON (1152 fondos, 4615 clases, fees, IDs, metadata), snapshot diario XLSX (VCP, patrimonio, market share, variaciones), ficha individual markdown (rendimientos TNA por periodo) y composicion de cartera (top activos). Sin API key."
license: MIT
---

# CAFCI — Fondos Comunes de Inversion Argentinos

Skill para consultar informacion publica de **fondos comunes de inversion en
Argentina** via las 4 fuentes oficiales de [CAFCI](https://www.cafci.org.ar)
(Camara Argentina de Fondos Comunes de Inversion).

Cubre **1152 fondos** y **4615 clases** activas al 2026-06: Money Market,
Renta Fija, Renta Variable, Renta Mixta, PyMes, Retorno Total,
Infraestructura, Fondos Cerrados, ASG, RG900.

---

## ⚠️ Aviso Legal

- API publica sin documentacion oficial. **Los endpoints pueden cambiar sin aviso** (como paso con la API REST anterior, discontinuada en 2026-04).
- Respetar terminos de uso del CAFCI.
- Los datos son **delayed** (cierre del dia habil, ~18hs ART).
- Para uso comercial intensivo, contactar al CAFCI para feeds oficiales.
- **Rendimientos pasados no garantizan rendimientos futuros.**

---

## 📌 Importante: API REST anterior DISCONTINUADA

La API REST `api.pub.cafci.org.ar/tipo-renta`, `/fondo/{id}`,
`/estadisticas/...` fue **discontinuada en 2026-04** (HTTP 403 "Route not
allowed"). El unico path que sigue activo en ese host es `/pb_get`.

Esta skill usa las **4 fuentes alternativas** que la reemplazaron:

1. `/consulta-de-fondos.json` (catalogo completo)
2. `/pb_get` (XLSX diario)
3. `defuddle.md/.../fondos/{F}?clase={C}` (ficha markdown)
4. `.../fondos/{F}?clase={C}` (HTML para composicion de cartera)

---

## Scripts

| Script | Descripcion |
|--------|-------------|
| **[fetch_cafci.py](./scripts/fetch_cafci.py)** | Script principal: todos los endpoints + funciones de consulta |

**Requiere:** `pip install openpyxl` (para parsear el XLSX diario).

---

## Uso rapido

```bash
# ── DATASETS ENTEROS (con cache local diario) ──────────────────────────

# Catalogo completo: 1152 fondos, 4615 clases con IDs, honorarios, metadata
py scripts/fetch_cafci.py catalogo
py scripts/fetch_cafci.py catalogo -o catalogo.json    # guarda 2.7MB
py scripts/fetch_cafci.py catalogo --no-cache          # fuerza refetch

# Snapshot diario: VCP, patrimonio, variaciones (dia/mes/YTD/12m)
py scripts/fetch_cafci.py diario
py scripts/fetch_cafci.py diario -o diario.json
py scripts/fetch_cafci.py diario --no-cache

# ── CONSULTAS SOBRE EL CACHE ───────────────────────────────────────────

# Buscar fondo por nombre (parcial, case-insensitive)
py scripts/fetch_cafci.py buscar "ahorro"
py scripts/fetch_cafci.py buscar "delta"
py scripts/fetch_cafci.py buscar "renta fija"

# Resolver IDs (mas compacto: solo fondo_id, clase_id, nombres)
py scripts/fetch_cafci.py resolve "ieb estrategico"
py scripts/fetch_cafci.py resolve "1810"

# Top N por patrimonio en una categoria del diario
py scripts/fetch_cafci.py top "Mercado de Dinero Peso Argentina"
py scripts/fetch_cafci.py top "Mercado de Dinero Peso Argentina" --limit 20
py scripts/fetch_cafci.py top "Renta Variable Peso Argentina"
py scripts/fetch_cafci.py top "Renta Fija Peso Argentina" --limit 5

# ── FICHAS INDIVIDUALES ────────────────────────────────────────────────

# Ficha markdown (rendimientos TNA: 7d/1m/90d/180d/YTD/12m + datos del fondo)
py scripts/fetch_cafci.py ficha 304 308              # 1810 Ahorro
py scripts/fetch_cafci.py ficha 1717 5772            # otro fondo
py scripts/fetch_cafci.py ficha 304 308 -o ficha.md  # guarda markdown

# Composicion de cartera (top activos + porcentaje)
py scripts/fetch_cafci.py cartera 304 308
py scripts/fetch_cafci.py cartera 1717 5772

# Ficha COMPLETA todo-en-uno (combina catalogo + diario + ficha + cartera)
py scripts/fetch_cafci.py fondo 304 308
py scripts/fetch_cafci.py fondo 304 308 -o 1810_ahorro_completo.json

# ── COMBINADO ──────────────────────────────────────────────────────────

# Catalogo + diario juntos (sin fichas individuales)
py scripts/fetch_cafci.py all -o cafci_snapshot.json

# ── OUTPUT ─────────────────────────────────────────────────────────────

# Modo silencioso (solo JSON/markdown, sin logs)
py scripts/fetch_cafci.py top "Mercado de Dinero Peso Argentina" -q
```

---

## Endpoints disponibles

| Modo | Data | URL |
|------|------|-----|
| `catalogo` | Catalogo: 1152 fondos, 4615 clases, IDs, honorarios, metadata | `GET /consulta-de-fondos.json` |
| `diario` | Snapshot diario: VCP, patrimonio, market share, variaciones | `GET /pb_get` (XLSX) |
| `ficha FONDO CLASE` | Ficha markdown: rendimientos TNA por periodo | `GET defuddle.md/.../fondos/{F}?clase={C}` |
| `cartera FONDO CLASE` | Composicion de cartera (top activos + %) | `GET .../fondos/{F}?clase={C}` (HTML) |
| `buscar QUERY` | Buscar fondos por nombre parcial | (local, sobre catalogo) |
| `resolve QUERY` | Resolver fondoId/claseId desde nombre | (local, sobre catalogo) |
| `top CATEGORIA` | Top N por patrimonio en una categoria | (local, sobre diario) |
| `fondo FONDO CLASE` | Ficha completa todo-en-uno (combina los 4 endpoints) | (local + 4 requests) |
| `all` | Snapshot catalogo + diario | (local + 2 requests) |

**Total: 4 endpoints HTTP + 5 funciones de consulta sobre cache.**

---

## Cache local

Los datasets pesados (catalogo + diario) se cachean **una vez por dia** en
el directorio temporal del sistema:

```
$TMP/cafci-catalog-YYYY-MM-DD.json    (~2.7 MB)
$TMP/cafci-daily-YYYY-MM-DD.json      (~1-2 MB)
```

- Windows: `C:\Users\<user>\AppData\Local\Temp\`
- Linux/Mac: `/tmp/`

Si vas a hacer multiples consultas en el dia (typical workflow), reusan
el cache automaticamente. Forzar refetch con `--no-cache`.

---

## Tipos de renta soportados

| Tipo | Cantidad fondos |
|------|-----------------|
| Renta Fija | 542 |
| Renta Mixta | 271 |
| Mercado de Dinero | 96 |
| Renta Variable | 76 |
| PyMes | 65 |
| Retorno Total | 42 |
| Infraestructura | 23 |
| Fondos Cerrados | 22 |
| ASG | 10 |
| RG900 | 5 |

---

## Categorias del DIARIO (para `top`)

Las categorias del diario combinan `tipo_renta + moneda + region` como
string. Ejemplos comunes:

| Categoria | Cobertura |
|-----------|-----------|
| `Renta Variable Peso Argentina` | Acciones argentinas |
| `Mercado de Dinero Peso Argentina` | Money Market $ |
| `Renta Fija Peso Argentina` | Bonos $ |
| `Renta Fija Dolar Estadounidense Argentina` | Bonos USD argentinos |
| `Renta Mixta Peso Argentina` | Fondos mixtos $ |
| `Retorno Total Peso Argentina` | Total return $ |

> Para ver lista completa: `py scripts/fetch_cafci.py diario -q | jq '.categorias'`

---

## Consideraciones tecnicas

### Datos devueltos por `catalogo`

Top-level:

| Campo | Descripcion |
|-------|-------------|
| `generated_at` | Timestamp ISO del catalogo. |
| `total_fondos`, `total_clases` | Contadores. |
| `filtros` | Catalogos de enums: `tipo_renta`, `region`, `moneda`, `benchmark`, `duration`, `horizonte`, `sociedad_gerente`, `tipo_dinero`, `tipo_renta_mixta`. |
| `fondos[]` | Array de fondos. |

Cada `fondos[]` tiene id, nombre, codigo_cnv, estado, objetivo, tipo_dinero,
valuacion, dias_liquidacion, inicio, sociedad_gerente, sociedad_depositaria,
moneda, tipo_renta, region, duration, benchmark, horizonte y **clases[]**.

Cada `clases[]` tiene id, nombre, moneda, inversion_minima, **honorarios**
(ingreso, rescate, transferencia, administracion_gerente, administracion_depositaria,
gasto_ordinario_gestion), suscripcion, liquidez, rg384, log_abierto,
ticker_bloomberg, ticker_isin.

> ⚠️ `honorarios.*` son **strings** (no floats). Castear con `float()` antes de comparar.

### Datos devueltos por `diario`

```json
{
  "fecha_reporte": "2026-06-04",
  "categorias": ["Renta Variable Peso Argentina", ...],
  "fondos": [
    {
      "nombre": "Allaria Equity Selection - Clase A",
      "categoria": "Renta Variable Peso Argentina",
      "moneda": "ARS",
      "region": "Arg",
      "horizonte": "Cor",
      "fecha": "2026-06-04",
      "vcp_actual": 1642.85,
      "vcp_anterior": 1628.345,
      "variacion_dia_pct": 0.891,
      "vcp_reexp_pesos": 1642.85,
      "variacion_mes_pct": -1.181,
      "variacion_ytd_pct": 11.939,
      "variacion_12m_pct": 61.542,
      "cantidad_cuotapartes": 1276470413.29,
      "patrimonio": 2097049572.01,
      "market_share": 0.107,
      "depositaria": "Banco Comafi S.A.",
      "codigo_cnv": "1603"
    }
  ]
}
```

### Datos devueltos por `cartera`

```json
{
  "fondo_id": 304,
  "clase_id": 308,
  "fecha_cartera": "15/05/2026",
  "composicion": [
    {"nombre": "Cta Cte $ Rem Bco Credico", "porcentaje": 17.4},
    {"nombre": "Pzo Fi $ Bco Nacion", "porcentaje": 14.8},
    ...
    {"nombre": "Resto de Activos", "porcentaje": 29.2}
  ]
}
```

> CAFCI publica solo los **top ~14 activos** + `"Resto de Activos"` agrupado.
> La fecha de cartera tiene delay de ~2-3 semanas vs el diario.

### Datos devueltos por `fondo` (todo-en-uno)

```json
{
  "meta": { ...del catalogo... },
  "diario": { ...del XLSX... },
  "ficha_md": "...markdown defuddle...",
  "cartera": { ...composicion... }
}
```

### Workflows recomendados

**A) Top N por patrimonio con fees:**
1. `top "<categoria>" --limit N` → lista de fondos
2. Para cada `nombre`, `resolve` para conseguir `fondo_id, clase_id`
3. Buscar honorarios en `catalogo` por `clases[].nombre` exacto

**B) Ficha completa de un fondo:**
1. `resolve "<query>"` → conseguir IDs
2. `fondo FONDO_ID CLASE_ID` → todo-en-uno

**C) Cuando el usuario no especifica clase:**
- Usar `buscar` o `resolve` y mostrar las clases disponibles
- Si hay una sola, continuar automaticamente con esa

### Flags

| Flag | Descripcion |
|------|-------------|
| `--limit N` | Cantidad de resultados (`top`). Default: 10 |
| `--no-cache` | Forzar refetch de catalogo/diario (ignorar cache local) |
| `-o archivo` | Guardar output a archivo JSON o markdown |
| `-q` / `--quiet` | Modo silencioso (solo JSON/markdown, sin logs) |

### Rate limiting

No hay rate limiting documentado. Recomendado:
- Minimo **0.3 segundos** entre requests a CAFCI.
- Para `defuddle.md` (proxy externo), esperar mas si hay timeouts.
- Para batches grandes, usar pool de concurrencia max 5.

### Manejo de errores

| Status | Causas tipicas |
|--------|----------------|
| 200 | OK |
| 403 `Route not allowed` | Path discontinuado de la API REST anterior |
| 403 (en `/pb_get`) | Faltan headers de browser (Origin, Referer) — el script ya los envia |
| 404 | URL mal formada o IDs inexistentes |
| Timeout en `defuddle.md` | Proxy externo lento — reintentar |

### Encoding

UTF-8 valido. Las consolas Windows muestran `?` para acentos pero los
archivos UTF-8 se guardan correctamente (el script usa `ensure_ascii=False`).

---

## Estructura del skill

```
skills/cafci/
├── SKILL.md                          # Este archivo (guia rapida)
├── references/
│   └── REFERENCE.md                  # Documentacion completa de los 4 endpoints + cache
└── scripts/
    └── fetch_cafci.py                # Script principal
```

---

> **Documentacion detallada:** Consultar [references/REFERENCE.md](./references/REFERENCE.md)
> para schemas JSON completos, tablas de campos exhaustivas, codigos de
> tipo_renta/region/horizonte/moneda, cache local, manejo de errores y
> consideraciones tecnicas.

> **Inspirado en:** [ferminrp/agent-skills/cafci-fondos-comunes-argentina](https://github.com/ferminrp/agent-skills/tree/main/skills/cafci-fondos-comunes-argentina)
> — esta implementacion porta el mismo diseño de 4 fuentes a la arquitectura
> SKILL.md / references/REFERENCE.md / scripts/fetch_*.py del repo.
