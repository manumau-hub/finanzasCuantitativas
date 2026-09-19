# DATA SOURCES — Organismos publicadores

> La API series-tiempo-ar **agrega series de multiples organismos publicos
> de Argentina**. NO es exclusivamente del INDEC, aunque es la fuente
> principal para series estadisticas.

---

## Indice

1. [Como identificar la fuente de una serie](#1-como-identificar-la-fuente-de-una-serie)
2. [INDEC (Instituto Nacional de Estadistica y Censos)](#2-indec)
3. [BCRA (Banco Central)](#3-bcra)
4. [Ministerio de Economia](#4-ministerio-de-economia)
5. [Secretaria de Trabajo (MTEySS)](#5-secretaria-de-trabajo-mteyss)
6. [Subsecretaria de Programacion Macroeconomica](#6-subsecretaria-de-programacion-macroeconomica)
7. [DGEYC (Direccion General de Estadistica y Censos CABA)](#7-dgeyc-direccion-general-de-estadistica-y-censos-caba)
8. [Otros organismos](#8-otros-organismos)
9. [Filtrar series por publicador](#9-filtrar-series-por-publicador)

---

## 1. Como identificar la fuente de una serie

El campo **`meta[1].dataset.source`** del response indica el organismo
publicador real:

```json
"meta": [
  {...global...},
  {
    "dataset": {
      "title": "Indice de Precios al Consumidor Nacional (IPC). Base diciembre 2016.",
      "source": "Instituto Nacional de Estadistica y Censos (INDEC)",
      ...
    },
    ...
  }
]
```

En el response normalizado del script, esto aparece como `series[].source`:

```python
data = fetch_series("145.3_INGNACUAL_DICI_M_38")
print(data['series'][0]['source'])
# → "Instituto Nacional de Estadística y Censos (INDEC)"
```

---

## 2. INDEC

**Instituto Nacional de Estadistica y Censos**

- **URL oficial:** https://www.indec.gob.ar
- **Source string en API:** `Instituto Nacional de Estadística y Censos (INDEC)`
- **Cobertura aprox:** la mayoria de las ~4250 series.

### Datasets principales

| Dataset | Descripcion | Frecuencia |
|---------|-------------|------------|
| IPC Nacional. Base diciembre 2016. | Indice de Precios al Consumidor Nacional con todas sus categorias y regiones | Mensual / Trimestral |
| IPC GBA. Base diciembre 2016. | IPC del Gran Buenos Aires con desglose por items individuales | Mensual |
| IPC GBA Base abril 2008 | **DISCONTINUADO** — historico pre-2016 | Mensual / Anual |
| EMAE. Base 2004. | Estimador Mensual de Actividad Economica con apertura sectorial | Mensual / Trimestral / Anual |
| IPI Manufacturero | Indice de Produccion Industrial | Mensual |
| ISAC. Base 2004. | Indicador Sintetico de Actividad de la Construccion | Mensual |
| EPH continua | Encuesta Permanente de Hogares — empleo, desempleo, ingresos | Trimestral |
| EPH puntual | EPH metodologia anterior — historico | Semestral |
| Canasta basica y linea de pobreza | Valores monetarios de las canastas | Mensual |
| Exportaciones por provincia y rubro | Comercio exterior detallado | Mensual / Anual |
| Cuentas Nacionales | PIB y agregados macroeconomicos | Trimestral / Anual |

### Cuando consultar INDEC directo

- Para metodologias detalladas.
- Para tablas de datos no publicadas en la API (algunas EPH detalladas, censos completos).
- Para datos en formato PDF tradicional.

URL de datos abiertos del INDEC: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-31-58

---

## 3. BCRA

**Banco Central de la Republica Argentina**

- **URL oficial:** https://www.bcra.gob.ar
- **Source string en API:** `Banco Central de la República Argentina (BCRA)`
- **Cobertura aprox:** subset de series del BCRA (~50-100), principalmente
  las mas usadas. Para cobertura COMPLETA usar el skill `bcra-macro`.

### Datasets principales accesibles aqui

| Dataset | Series tipicas |
|---------|----------------|
| Series historicas de estadisticas monetarias | M2, M3, base monetaria, reservas |
| Reservas internacionales y pasivos del BCRA | Saldos diarios y promedios |
| Tipo de cambio $-USD y futuro dolar | BNA vendedor, futuros |
| Balance cambiario | Operaciones por sector |
| Activos y pasivos del BCRA | Composicion del balance |
| Relevamiento de Expectativas de Mercado (REM) | Encuesta a analistas privados sobre expectativas macro |

### Cuando usar `bcra-macro` skill en su lugar

El skill `bcra-macro` accede DIRECTAMENTE a la API del BCRA
(`api.bcra.gob.ar`) con cobertura **completa de 638 series**. Si solo
necesitas datos del BCRA y no del INDEC, usar `bcra-macro`.

---

## 4. Ministerio de Economia

**Ministerio de Economia de la Nacion**

- **URL oficial:** https://www.argentina.gob.ar/economia
- **Source string:** varios — segun subsecretaria/secretaria que publique.

### Datasets principales

| Dataset | Publicador |
|---------|------------|
| Producto Interno Bruto (PIB) Cuentas Nacionales | Secretaria de Programacion Economica |
| Deuda publica | Secretaria de Finanzas |
| Recursos tributarios | Direccion General Impositiva (AFIP) — agregada por MinEcon |
| Indicadores fiscales | Direccion Nacional de Politica Fiscal |
| Producto Interno Bruto en dolares per capita | Subsecretaria de Programacion Macroeconomica |

---

## 5. Secretaria de Trabajo (MTEySS)

**Secretaria de Trabajo, Empleo y Seguridad Social**

- **URL oficial:** https://www.argentina.gob.ar/trabajo
- **Source string:** `Secretaría de Trabajo, Empleo y Seguridad Social`

### Datasets principales

| Dataset | Series tipicas |
|---------|----------------|
| RIPTE | Remuneracion Imponible Promedio Trabajadores Estables — mensual desde 1994 |
| Salario minimo, vital y movil | SMVM en pesos corrientes — diario/mensual/horario |
| Haber minimo jubilatorio | Pesos corrientes desde 1971 |

### Frecuencia tipica

Mensual.

---

## 6. Subsecretaria de Programacion Macroeconomica

**Subsecretaria de Programacion Macroeconomica del Ministerio de Economia**

- **Source string:** `Subsecretaría de Programación Macroeconómica`

### Datasets principales

| Dataset | Comentario |
|---------|------------|
| IPC GBA (catalogo programacion macro) | Datos de IPC re-publicados con metadatos macroeconomicos |
| IPC Resto | Categoria del IPC GBA base 2008 (discontinuado) |
| Producto Interno Bruto en dolares per capita y poblacion | PIB convertido a USD |

---

## 7. DGEYC (Direccion General de Estadistica y Censos CABA)

**Direccion General de Estadistica y Censos del Gobierno de la Ciudad de Buenos Aires**

- **URL oficial:** https://www.estadisticaciudad.gob.ar
- **Source string:** `Dirección General de Estadística y Censos del GCBA`

### Datasets principales

| Dataset | Comentario |
|---------|------------|
| IPC de la Ciudad de Buenos Aires | Indice paralelo al IPC INDEC, calculado por GCBA con su propia metodologia |

### Cuando usar IPC CABA vs IPC GBA

- **IPC CABA:** solo Ciudad Autonoma de Buenos Aires (CABA), excluye conurbano.
- **IPC GBA:** Gran Buenos Aires = CABA + 24 partidos del conurbano bonaerense.

---

## 8. Otros organismos

La API tambien incluye datos de:

- **Direccion Nacional de Datos e Informacion Publica (DGNIP)** — el equipo
  que mantiene la API.
- **AFIP** (Agencia Federal de Ingresos Publicos) — recaudacion via Min Economia.
- **ANSES** (Administracion Nacional de la Seguridad Social) — algunos
  indicadores de beneficios.
- **Banco Nacion Argentina (BNA)** — cotizaciones de divisas.
- **Secretarias provinciales de estadistica** (algunos datos).

---

## 9. Filtrar series por publicador

### Via `/search` con filtros de agregacion

```bash
GET /search?q=...&aggregations[publisher.name]=INDEC
```

Filtra resultados a solo series publicadas por INDEC.

### Manual cliente-side

```python
results = search_series("ipc nacional", limit=50)
indec_only = [
    r for r in results['data']
    if 'INDEC' in r.get('dataset', {}).get('source', '')
]
```

### Catalogos por publicador

Para descubrir TODOS los datasets de un publicador:

```bash
GET /search?q=*&aggregations[publisher.name]=INDEC&limit=100
```

Devuelve los primeros 100 datasets del INDEC con sus IDs.

---

## Comparacion entre fuentes

| Source | # series aprox | Fortaleza | Cuando usar |
|--------|----------------|-----------|-------------|
| INDEC | ~3500 | Estadisticas oficiales (precios, actividad, empleo, pobreza) | Para casi todo lo macro/social |
| BCRA | ~100 | Monetario, financiero, FX, reservas | **Mejor usar skill `bcra-macro` (638 series completas)** |
| Min Economia | ~200 | PIB, deuda, fiscal | Para cuentas nacionales y deuda |
| Sec Trabajo | ~10 | Salarios | Para RIPTE, SMVM, jubilaciones |
| Sub Prog Macro | ~50 | Catalogo macroeconomico re-empaquetado | Para indicadores con metadata especifica |
| DGEYC CABA | ~20 | IPC CABA | Para indicadores especificos de Capital |
