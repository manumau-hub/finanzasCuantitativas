# SERIES CATALOG — IDs canonicos por topico

> Catalogo organizado de los **series IDs mas importantes** del INDEC +
> BCRA + otros organismos accesibles via esta API. Estos IDs fueron
> verificados empiricamente en 2026-06.

> **Catalogo estructurado en JSON:**
> [`../assets/known_series_ids.json`](../assets/known_series_ids.json)
>
> **Bundles pre-armados:**
> [`../assets/series_groups.json`](../assets/series_groups.json)

---

## Indice

1. [IPC Nacional (Indice de Precios al Consumidor)](#1-ipc-nacional)
2. [IPC GBA y CABA (regiones)](#2-ipc-gba-y-caba)
3. [EMAE (Estimador Mensual de Actividad Economica)](#3-emae)
4. [IPI Manufacturero](#4-ipi-manufacturero)
5. [ISAC (Construccion)](#5-isac-construccion)
6. [Salarios](#6-salarios)
7. [Empleo y EPH](#7-empleo-y-eph)
8. [Pobreza e indigencia](#8-pobreza-e-indigencia)
9. [Comercio exterior](#9-comercio-exterior)
10. [Tipo de cambio (BCRA)](#10-tipo-de-cambio-bcra)
11. [Reservas internacionales (BCRA)](#11-reservas-internacionales-bcra)
12. [REM (Expectativas de mercado)](#12-rem-expectativas-de-mercado)
13. [Como descubrir otros IDs](#13-como-descubrir-otros-ids)

---

## 1. IPC Nacional

**Publicado por INDEC. Base diciembre 2016 = 100. Frecuencia mensual.**

| ID | Que es | Units |
|----|--------|-------|
| `145.3_INGNACUAL_DICI_M_38` | IPC Nacional Nivel General. **Variacion mensual %** | Variacion intermensual |
| `148.3_INUCLEONAL_DICI_M_19` | IPC Nacional Nucleo. Mensual | Indice |
| `148.3_IREGULANAL_DICI_M_22` | IPC Nacional Regulados. Mensual | Indice |
| `146.3_ITRANSPNAL_DICI_M_23` | IPC Nacional Transporte. Mensual | Indice |
| `146.3_IEDUCACNAL_DICI_M_22` | IPC Nacional Educacion. Mensual | Indice |
| `147.3_IBIENESNAL_DICI_T_19` | IPC Nacional Bienes. Mensual | Indice |
| `147.3_ISERVICNAL_DICI_T_22` | IPC Nacional Servicios. Mensual | Indice |
| `148.1_IPC_ESTACINAL_DICI_T_25` | IPC Nacional Estacionales. Trimestral | Indice |

### Frecuencia trimestral

| ID | Que es |
|----|--------|
| `147.1_IPC_BIENESNAL_DICI_T_19` | IPC Bienes Nacional. Trimestral |
| `147.1_IPC_SERVICNAL_DICI_T_22` | IPC Servicios Nacional. Trimestral |
| `146.1_IPC_EDUCACNAL_DICI_T_22` | IPC Educacion Nacional. Trimestral |
| `146.1_IPC_SALUD_NAL_DICI_T_18` | IPC Salud Nacional. Trimestral |
| `146.1_IPC_TRANSPNAL_DICI_T_23` | IPC Transporte Nacional. Trimestral |
| `146.1_IPC_COMUNINAL_DICI_T_27` | IPC Comunicaciones Nacional. Trimestral |
| `148.1_IPC_REGULANAL_DICI_T_22` | IPC Regulados Nacional. Trimestral |
| `148.1_IPC_NUCLEONAL_DICI_T_19` | IPC Nucleo Nacional. Trimestral |

### Variantes por region (Cuyo, Patagonia, etc.)

```bash
py scripts/fetch_indec.py search "IPC nacional patagonia"
py scripts/fetch_indec.py search "IPC nacional pampeana"
py scripts/fetch_indec.py search "IPC nacional NEA"
py scripts/fetch_indec.py search "IPC nacional NOA"
```

---

## 2. IPC GBA y CABA

### IPC GBA (Gran Buenos Aires) - Base diciembre 2016

| ID | Que es |
|----|--------|
| `103.1_I2N_2016_M_19` | IPC-GBA. Nivel General. Mensual |
| `105.1_I2L_2016_M_18` | IPC-GBA. Precios. Lavandina. Mensual |
| `105.1_I2N_2016_M_14` | IPC-GBA. Precios. Nalga. Pesos. Mensual |

### IPC GBA Base 2008 (DISCONTINUADO pero historico util)

| ID | Que es |
|----|--------|
| `99.3_IR_2008_0_9` | IPC resto. Mensual |
| `99.1_IR_2008_0_9` | IPC resto. Anual |
| `96.3_IBSV_2008_M_23` | IPC Servicios/Bienes. Variacion % mensual |
| `96.3_ISV_2008_M_16` | IPC Servicios. Variacion % mensual |

### IPC CABA (Ciudad de Buenos Aires, GCBA)

```bash
py scripts/fetch_indec.py search "IPC ciudad buenos aires"
```

Ejemplo: `193.2_ESTACIONALLES_2021_0_12_84` (Nivel de precios estacionales CABA).

---

## 3. EMAE

**Estimador Mensual de Actividad Economica. Publicado por INDEC. Base 2004=100. Mensual.**

### Nivel general

| ID | Que es |
|----|--------|
| `143.3_NO_PR_2004_A_21` | EMAE Nivel general — **serie original** |
| `143.3_NO_PR_2004_A_31` | EMAE Nivel general — **serie desestacionalizada** |

### Sectoriales (subset)

| ID | Que es |
|----|--------|
| `11.3_VMATC_2004_M_12` | EMAE Sectorial Construccion. Mensual |
| `11.3_VIPAA_2004_M_5` | EMAE Sectorial Pesca. Mensual |
| `11.2_VMATC_2004_T_12` | EMAE Sectorial Construccion. Trimestral |
| `11.1_VMATC_2004_A_12` | EMAE Sectorial Construccion. Anual |
| `11.1_CMMR_2004_A_10` | EMAE Sectorial Enseñanza. Anual |
| `11.1_VIPAA_2004_A_5` | EMAE Sectorial Pesca. Anual |

> Para descubrir mas sectoriales:
> ```bash
> py scripts/fetch_indec.py search "EMAE" --limit 50
> ```

---

## 4. IPI Manufacturero

**Indice de Produccion Industrial Manufacturero. INDEC. Base 2004=100.**

| ID | Que es |
|----|--------|
| `453.1_SERIE_ORIGNAL_0_0_14_46` | IPI Nivel General Serie Original |

> Buscar variantes: `py scripts/fetch_indec.py search "IPI manufacturero"`.

---

## 5. ISAC (Construccion)

**Indicador Sintetico de la Actividad de la Construccion. INDEC. Base 2004=100. Mensual.**

| ID | Que es |
|----|--------|
| `33.2_ISAC_NIVELRAL_0_M_18_63` | ISAC Nivel General |
| `33.2_I_2004_M_4` | ISAC Nivel General — **variacion interanual %** |
| `33.5_ISAC_ASFALLTO_0_0_12_33` | ISAC Insumos. Asfalto. Tendencia |
| `33.5_ISAC_HIERRION_0_0_49_83` | ISAC Insumos. Hierro redondo y aceros. Tendencia |
| `35.1_NG_1993_A_13` | Indicador sintetico de servicios publicos Nivel General. Anual |
| `35.2_NG_1993_T_13` | Indicador sintetico de servicios publicos Nivel General. Trimestral |
| `35.1_NGD_1993_A_32` | Indicador sintetico de servicios publicos NG **desestacionalizado**. Anual |

### Historico discontinuado

| ID | Que es |
|----|--------|
| `32.1_IEV_2004_A_23` | ISAC Edificios para vivienda. Anual (discontinuado) |
| `32.2_ICP_2004_T_30` | ISAC Obras petroleras. Trimestral (discontinuado) |

---

## 6. Salarios

**Publicados por Secretaria de Trabajo, Empleo y Seguridad Social.**

| ID | Que es | Frecuencia | Units |
|----|--------|------------|-------|
| `158.1_REPTE_0_0_5` | **RIPTE** (Remuneracion Imponible Promedio Trabajadores Estables) | Mensual | Pesos corrientes |
| `57.1_SMVMM_0_M_34` | Salario minimo vital y movil — **mensual** | Mensual | Pesos corrientes |
| `57.1_SMVMD_0_M_33` | Salario minimo vital y movil — diario | Mensual | Pesos corrientes |
| `57.1_SMVMH_0_M_31` | Salario minimo vital y movil — horario | Mensual | Pesos corrientes |
| `58.1_MP_0_M_13` | Haber minimo jubilatorio | Mensual | Pesos corrientes |

### Series historicas

El SMVM tiene historico desde **1988**. El haber jubilatorio desde **1971**.

---

## 7. Empleo y EPH

**Encuesta Permanente de Hogares (EPH). INDEC. Trimestral.**

### Tasa de desocupacion (varias frecuencias)

| ID | Que es |
|----|--------|
| `42.3_EPH_PUNTUATAL_0_M_30` | Tasa desocupacion total — **EPH continua trimestral** |
| `42.2_EPDT_0_M_30` | Tasa desocupacion total — EPH puntual semestral (historico) |

### Tasa de desempleo por provincia (anual)

| ID | Provincia |
|----|-----------|
| `45.1_ECTDTF_0_A_41` | Formosa |
| `45.1_ECTDTP_0_A_43` | Patagonia |
| `45.1_ECTDTP_0_A_41` | Posadas |

> Buscar mas provincias:
> ```bash
> py scripts/fetch_indec.py search "tasa desempleo CABA"
> py scripts/fetch_indec.py search "tasa desempleo Gran Mendoza"
> ```

### Hogares con ingresos debajo linea de pobreza por aglomerado (% historico)

| ID | Aglomerado |
|----|-----------|
| `63.1_RG_0_0_12` | Rio Gallegos |
| `63.1_SNVC_0_0_30` | San Nicolas - Villa Constitucion |
| `63.1_LR_0_0_8` | La Rioja |
| `63.1_GTTV_0_0_23` | Gran Tucuman - Tafi Viejo |
| `63.1_GM_0_0_12` | Gran Mendoza |

---

## 8. Pobreza e indigencia

**INDEC. Frecuencia: mensual / semestral.**

### Linea de pobreza

| ID | Que es | Periodo |
|----|--------|---------|
| `150.1_LA_POBREZA_0_D_13` | Linea de pobreza pesos corrientes — **desde 2016** | Mensual |
| `59.3_LA_POBREZA_0_0_13` | Linea de pobreza pesos corrientes — historico 1992-2000 | Semestral |
| `59.4_LA_POBREZA_0_0_13` | Linea de pobreza pesos corrientes — 2000-2000 | Mensual |
| `59.2_LP_0_D_13` | Linea de pobreza desde 2000 hasta 2006 | Trimestral |
| `60.1_PP_0_0_15` | **% poblacion debajo linea pobreza** (1988-2003) — historico EPH puntual | Semestral |

---

## 9. Comercio exterior

**INDEC. Mensual / trimestral / anual.**

### Exportaciones totales

| ID | Frecuencia | Units |
|----|------------|-------|
| `75.3_IETG_0_M_31` | Mensual | Millones USD FOB |
| `75.2_IETG_0_T_31` | Trimestral | Millones USD FOB |
| `75.1_IETG_0_A_31` | Anual | Millones USD FOB |
| `74.3_IET_0_M_16` | Mensual | Millones de dolares |
| `83.1_EMD_2004_A_30` | Anual | Millones de dolares |

### Exportaciones por rubro (anuales)

| ID | Rubro |
|----|-------|
| `350.1_TOTAL_EXPOMOI__23` | MOI (Manufacturas de Origen Industrial) |
| `350.1_TOTAL_EXPO_PP__22` | PP (Productos Primarios) |

> Para MOA, combustibles, etc.: search `"exportaciones MOA"`, `"exportaciones combustibles"`.

---

## 10. Tipo de cambio (BCRA)

**Banco Central. Diario.**

| ID | Que es |
|----|--------|
| `168.1_T_CAMBIOR_D_0_0_26` | Tipo de cambio BNA (Vendedor). Pesos por dolar. Diario |

### Otros tipos de cambio

```bash
py scripts/fetch_indec.py search "tipo cambio mayorista"
py scripts/fetch_indec.py search "tipo cambio nominal"
py scripts/fetch_indec.py search "tipo cambio real multilateral"
```

### Tipo de cambio nominal anual / trimestral

| ID | Que es |
|----|--------|
| `9.1_TU_2004_A_17` | Tipo cambio nominal peso/dolar. Anual |
| `9.2_TU_2004_T_17` | Tipo cambio nominal peso/dolar. Trimestral |

---

## 11. Reservas internacionales (BCRA)

| ID | Que es | Frecuencia |
|----|--------|------------|
| `174.1_RRVAS_IDOS_0_0_36` | Reservas Internacionales BCRA — **Saldos** | Mensual |
| `174.1_RRVAS_IIOS_0_0_60` | Reservas Internacionales BCRA — **Promedio mensual de saldos diarios** | Mensual |
| `92.1_RID_0_0_32` | Reservas internacionales BCRA en **millones de dolares** | Mensual |
| `182.1_VARIACION_LES_0_M_43` | Variacion contable de Reservas Internacionales | Mensual |
| `300.1_AP_ACT_RESTER_0_M_21` | Apertura activo. Reservas internacionales | Mensual |

---

## 12. REM (Expectativas de mercado)

**Relevamiento de Expectativas de Mercado del BCRA. Mensual.**

### Tipo de cambio nominal

| ID | Que es |
|----|--------|
| `430.1_MEDIANA_IPT_5_M_0_0_31_0` | REM Mediana Tipo de Cambio Nominal — variacion mensual proximo trimestre |
| `430.1_MEDIANA_IP_12_M_0_0_27_59` | REM Mediana TCN — variacion interanual proximos 12 meses |
| `430.1_REM_TCN_VA025_M_0_0_19_9` | REM Mediana TCN var interanual año 2025 |

### Otras variables REM

```bash
py scripts/fetch_indec.py search "REM mediana inflacion"
py scripts/fetch_indec.py search "REM mediana PIB"
py scripts/fetch_indec.py search "REM mediana tasa BADLAR"
```

---

## 13. Como descubrir otros IDs

### Usando el script

```bash
# Buscar por keyword
py scripts/fetch_indec.py search "deuda publica"
py scripts/fetch_indec.py search "recaudacion tributaria"
py scripts/fetch_indec.py search "produccion soja"

# Buscar con limit alto
py scripts/fetch_indec.py search "EMAE" --limit 50
```

### Filtrar series activas (no discontinuadas)

```python
from fetch_indec import search_series

results = search_series("ipc nacional", limit=50)
active = [
    r for r in results['data']
    if 'DISCONTI' not in r['dataset']['title'].upper()
]
```

### Validar un ID antes de cachearlo

```bash
py scripts/fetch_indec.py validate "XXX_YYY_ZZZ"
```

### Inspeccionar metadata sin descargar datos

```bash
py scripts/fetch_indec.py series "XXX_YYY_ZZZ" --metadata only
```

### Workflow: descubrir → validar → usar

```bash
# 1. Buscar
py scripts/fetch_indec.py search "ipc CABA nivel general" --limit 5

# 2. Inspeccionar el primero
py scripts/fetch_indec.py series "<ID_ELEGIDO>" --metadata only

# 3. Si convence, fetchear data
py scripts/fetch_indec.py series "<ID_ELEGIDO>" --last 24
```

### Patron de nombres de IDs

Aunque son crípticos, los IDs siguen estos patrones:

- **Dataset numerico:** `XXX.Y_...` donde XXX es dataset_id y Y es distribution_id.
- **Slug del indicador:** `IPC_BIENES`, `INGNACUAL`, `REPTE`, etc.
- **Base:** `_DICI_` (diciembre), `_2004_`, `_2008_`, `_2016_`.
- **Frecuencia:** `_M_` (monthly), `_T_` (trimestral), `_A_` (anual), `_D_` (diario).
- **Field index:** numero final.

NO intentar adivinar — siempre buscar primero.
