# FRED Series Reference — 100+ Series Esenciales

Referencia completa de series FRED organizadas por categoría. Cada entrada incluye: `ID`, `Descripción`, `Frecuencia`, `Unidad` y `Desde`.

> **Nota:** valores `"."` en la API = dato no disponible.
> **Regenerar este archivo:** ver script `search_series.py` con `--output-catalog`.

---

## 1. Producto Interno Bruto (GDP)

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `GDP` | PIB Nominal | Trimestral | Billions $ | 1947 |
| `GDPC1` | PIB Real (chained 2017) | Trimestral | Billions $ | 1947 |
| `A191RL1Q225SBEA` | PIB Real % (QoQ anualizado) | Trimestral | % | 1947 |
| `GDPPOT` | PIB Potencial | Trimestral | Billions $ | 1949 |
| `GDPSAV` | Ahorro Nacional Bruto | Trimestral | Billions $ | 1947 |
| `GPDI` | Inversión Doméstica Bruta | Trimestral | Billions $ | 1947 |
| `GCEC1` | Consumo Gobierno Real | Trimestral | Billions $ | 1947 |
| `IMPGSC1` | Importaciones Reales | Trimestral | Billions $ | 1947 |
| `EXPGSC1` | Exportaciones Reales | Trimestral | Billions $ | 1947 |

---

## 2. Inflación — CPI

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `CPIAUCSL` | IPC General (todos los items) | Mensual | Índice 1982=100 | 1947 |
| `CPILFESL` | IPC Subyacente (sin alimentos/energía) | Mensual | Índice 1982=100 | 1957 |
| `CPIENGSL` | IPC Energía | Mensual | Índice 1982=100 | 1957 |
| `CPIFABSL` | IPC Alimentos | Mensual | Índice 1982=100 | 1967 |
| `CPITRNSL` | IPC Transporte | Mensual | Índice 1982=100 | 1935 |
| `CUSR0000SAD` | IPC Vivienda | Mensual | Índice 1982=100 | 1967 |
| `CPIAUCNS` | IPC General (sin ajuste estacional) | Mensual | Índice 1982=100 | 1913 |
| `CPIYOY` | IPC Variación Interanual | Mensual | % | 1914 |

---

## 3. Inflación — PCE

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `PCE` | Gasto Personal Consumo (PCE) | Mensual | Billions $ | 1959 |
| `PCEC96` | PCE Real | Mensual | Billions $ | 2002 |
| `PCECTPI` | PCE Price Index | Mensual | Índice 2017=100 | 1959 |
| `PCEPILFE` | PCE Subyacente (Core PCE, sin alimentos/energía) | Mensual | Índice 2017=100 | 1960 |
| `PCEPILFE_YOY` | Core PCE Variación Interanual | Mensual | % | 1960 |

---

## 4. Tasas de Interés — Fed

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `FEDFUNDS` | Tasa de Fondos Federales (target) | Diaria | % | 1954 |
| `DFF` | Tasa de Fondos Federales (efectiva) | Diaria | % | 1954 |
| `EFFR` | Tasa de Fondos Federales (Effective Federal Funds Rate) | Diaria | % | 2000 |
| `SOFR` | Secured Overnight Financing Rate | Diaria | % | 2018 |
| `IORB` | Interest on Reserve Balances | Diaria | % | 2008 |
| `PRIME` | Tasa Prime | Diaria | % | 1949 |
| `DISCBORR` | Tasa de Descuento (ventanilla) | Diaria | % | 1934 |

---

## 5. Tasas de Interés — Treasuries

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `DGS1MO` | Treasury 1 mes | Diaria | % | 2001 |
| `DGS3MO` | Treasury 3 meses | Diaria | % | 1981 |
| `DGS6MO` | Treasury 6 meses | Diaria | % | 1981 |
| `DGS1` | Treasury 1 año | Diaria | % | 1962 |
| `DGS2` | Treasury 2 años | Diaria | % | 1976 |
| `DGS3` | Treasury 3 años | Diaria | % | 1962 |
| `DGS5` | Treasury 5 años | Diaria | % | 1962 |
| `DGS7` | Treasury 7 años | Diaria | % | 1969 |
| `DGS10` | Treasury 10 años | Diaria | % | 1962 |
| `DGS20` | Treasury 20 años | Diaria | % | 1993 |
| `DGS30` | Treasury 30 años | Diaria | % | 1977 |
| `T10Y2Y` | Spread 10y - 2y (curva invertida) | Diaria | % | 1976 |
| `T10Y3M` | Spread 10y - 3m | Diaria | % | 1982 |
| `T5YIE` | Tasa de Inflación Implícita 5y (breakeven) | Diaria | % | 2003 |
| `T10YIE` | Tasa de Inflación Implícita 10y (breakeven) | Diaria | % | 2003 |
| `BAA10Y` | Spread BAA Corporate - 10y | Diaria | % | 1986 |

---

## 6. Empleo

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `UNRATE` | Tasa de Desempleo | Mensual | % | 1948 |
| `PAYEMS` | Nonfarm Payrolls (nóminas no agrícolas) | Mensual | Miles | 1939 |
| `CIVPART` | Tasa de Participación Laboral | Mensual | % | 1948 |
| `EMRATIO` | Relación Empleo/Población | Mensual | % | 1948 |
| `LNS14000006` | Desempleo Hombres | Mensual | % | 1948 |
| `LNS14000002` | Desempleo Mujeres | Mensual | % | 1948 |
| `U6RATE` | Desempleo Amplio (U-6, incluye subempleo) | Mensual | % | 1994 |
| `AWHMAN` | Horas Semanales Promedio (manufactura) | Mensual | Horas | 1939 |
| `CES0500000003` | Salario Promedio por Hora (Average Hourly Earnings) | Mensual | $ | 1964 |
| `JTSJOL` | Job Openings (JOLTS) | Mensual | Miles | 2000 |
| `JTSQUR` | Quits Rate (tasa de renuncias) | Mensual | % | 2000 |
| `ICSA` | Initial Jobless Claims (semanal) | Semanal | Miles | 1967 |

---

## 7. Dinero y Crédito

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `M1SL` | M1 Money Supply | Mensual | Billions $ | 1959 |
| `M2SL` | M2 Money Supply | Mensual | Billions $ | 1959 |
| `M2V` | Velocidad de M2 | Mensual | Ratio | 1959 |
| `M1V` | Velocidad de M1 | Mensual | Ratio | 1959 |
| `REALLN` | Préstamos Hipotecarios Residenciales | Mensual | Billions $ | 1947 |
| `BUSLOANS` | Préstamos Comerciales | Semanal | Billions $ | 1947 |
| `CONSUMER` | Crédito al Consumidor | Mensual | Billions $ | 1943 |
| `TOTBKCR` | Total de Crédito Bancario | Semanal | Billions $ | 1973 |
| `BOGMBASE` | Base Monetaria (St. Louis) | Semanal | Billions $ | 1984 |
| `WRESBAL` | Reservas Bancarias | Semanal | Billions $ | 1984 |

---

## 8. Mercados Financieros

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `VIXCLS` | VIX (volatilidad S&P 500, cierre) | Diaria | Índice | 1990 |
| `SP500` | S&P 500 (índice de precios) | Diaria | Índice | 1957 |
| `NASDAQCOM` | NASDAQ Composite | Diaria | Índice | 1971 |
| `DJIA` | Dow Jones Industrial Average | Diaria | Índice | 1896 |
| `WILL5000PR` | Wilshire 5000 (total market) | Diaria | Índice | 1971 |
| `DEXUSEU` | EUR/USD Spot Rate | Diaria | USD | 1999 |
| `DEXJPUS` | JPY/USD Spot Rate | Diaria | USD | 1971 |
| `DTWEXBGS` | Dólar Trade-Weighted Index (Broad) | Diaria | Índice | 2006 |
| `DTWEXM` | Dólar Trade-Weighted Index (Major) | Diaria | Índice | 1973 |
| `REAINTRATREARAT1YE` | Tasa Impositiva Real Promedio | Anual | % | 1948 |

---

## 9. Vivienda y Construcción

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `HOUST` | Housing Starts (viviendas iniciadas) | Mensual | Miles | 1959 |
| `HOUST1F` | Housing Starts (1 unidad) | Mensual | Miles | 1959 |
| `HOUST5F` | Housing Starts (5+ unidades) | Mensual | Miles | 1959 |
| `PERMIT` | Building Permits | Mensual | Miles | 1960 |
| `EXHOSLUSM495S` | Existing Home Sales | Mensual | Miles | 1999 |
| `CSUSHPISA` | Case-Shiller Home Price Index | Mensual | Índice | 1987 |
| `MORTGAGE30US` | Tasa Hipoteca 30 años (Freddie Mac) | Semanal | % | 1971 |
| `MORTGAGE15US` | Tasa Hipoteca 15 años (Freddie Mac) | Semanal | % | 1991 |
| `OBMMIC30YF` | Tasa Hipoteca 30 años (OptBlue) | Diaria | % | 2016 |

---

## 10. Consumo y Ventas Minoristas

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `TOTALSA` | Retail Sales (ventas minoristas totales) | Mensual | Millions $ | 1992 |
| `MRTSSM44000USS` | Retail Sales: Motor Vehicle | Mensual | Millions $ | 1992 |
| `MRTSSM448USS` | Retail Sales: Clothing | Mensual | Millions $ | 1992 |
| `MRTSSM445USS` | Retail Sales: Food & Beverage | Mensual | Millions $ | 1992 |
| `PCESV` | Services Expenditures | Mensual | Billions $ | 1959 |
| `PCDG` | Durables Expenditures | Mensual | Billions $ | 1959 |
| `PCND` | Nondurables Expenditures | Mensual | Billions $ | 1959 |
| `PSAVERT` | Personal Saving Rate | Mensual | % | 1959 |
| `UMCSENT` | Consumer Sentiment (U. Michigan) | Mensual | Índice | 1978 |

---

## 11. Industria y Producción

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `INDPRO` | Industrial Production Index | Mensual | Índice 2017=100 | 1919 |
| `CAPUTL` | Capacity Utilization | Mensual | % | 1967 |
| `TCU` | Total Capacity Utilization | Mensual | % | 1967 |
| `IPMAN` | Manufacturing Output | Mensual | Índice 2017=100 | 1919 |
| `IPBUSEQ` | Business Equipment Output | Mensual | Índice 2017=100 | 1947 |
| `IPDCONGD` | Consumer Goods Output | Mensual | Índice 2017=100 | 1919 |
| `BUSINV` | Business Inventories | Mensual | Millions $ | 1947 |
| `AMTMNO` | Manufacturing New Orders (durables) | Mensual | Millions $ | 1992 |

---

## 12. Gobierno y Deuda

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `GFDEBTN` | Federal Debt Total | Trimestral | Billions $ | 1966 |
| `FYFSD` | Federal Budget Surplus/Deficit | Anual | Billions $ | 1901 |
| `FGEXPND` | Federal Government Expenditures | Mensual | Billions $ | 1901 |
| `FGRECPT` | Federal Government Receipts | Mensual | Billions $ | 1901 |
| `MTSDS133FMS` | Federal Debt Held by Public | Trimestral | Billions $ | 1998 |
| `SLGPRI` | State & Local Gov Spending | Mensual | Billions $ | 1959 |

---

## 13. Comercio Internacional

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `BOPGSTB` | Trade Balance (Bienes y Servicios) | Mensual | Millions $ | 1992 |
| `BOPCAT` | Current Account Balance | Trimestral | Billions $ | 1960 |
| `IMPGS` | Goods Imports | Mensual | Millions $ | 1992 |
| `EXPGS` | Goods Exports | Mensual | Millions $ | 1992 |
| `M0892AUS000NNBR` | Terms of Trade | Trimestral | Índice | 1953 |

---

## 14. Energía y Commodities

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `OILPRICE` | Crude Oil Price (WTI) | Diaria | $/barril | 1946 |
| `GASREGCOV` | Gasoline Regular (US Avg) | Semanal | $/galón | 1992 |
| `DHHNGSP` | Henry Hub Natural Gas Spot | Diaria | $/MMBTU | 1997 |
| `APU0000708111` | Electricity Price (Avg) | Mensual | $/kWh | 1978 |
| `PI0120211` | US Corn Price | Mensual | $/bushel | 1935 |
| `PI0120212` | US Wheat Price | Mensual | $/bushel | 1935 |
| `PI0120411` | US Soybean Price | Mensual | $/bushel | 1935 |

---

## 15. Series Calculadas y Spreads

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `RECESSION` | Indicador de Recesión (NBER) | Mensual | 0/1 | 1854 |
| `USREC` | Indicador de Recesión (US) | Mensual | 0/1 | 1947 |
| `T10Y2Y` | Treasury Spread 10y - 2y | Diaria | % | 1976 |
| `T10Y3M` | Treasury Spread 10y - 3m | Diaria | % | 1982 |
| `BAA10Y` | Credit Spread BAA - 10y | Diaria | % | 1986 |
| `T5YIE` | Breakeven Inflation 5y | Diaria | % | 2003 |
| `T10YIE` | Breakeven Inflation 10y | Diaria | % | 2003 |
| `STLFSI` | St. Louis Financial Stress Index | Semanal | Índice | 1993 |
| `NFCI` | Chicago Financial Conditions Index | Semanal | Índice | 1973 |

---

## 16. Indicadores de Recesión y Crisis

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `USREC` | Recession indicator (1=recesión) | Mensual | 0/1 | 1854 |
| `USRECDM` | NBER Recession indicator mensual | Mensual | 0/1 | 1854 |
| `STLFSI` | St. Louis Financial Stress Index | Semanal | Índice | 1993 |
| `NFCI` | National Financial Conditions Index | Semanal | Índice | 1973 |
| `TEDRATE` | TED Spread (LIBOR - T-Bill 3m) | Diaria | % | 1986 |
| `DFII10` | Treasury 10y TIPS Yield | Diaria | % | 2003 |
| `EXPINF1YR` | Expected Inflation 1-year | Mensual | % | 1978 |
| `EXPINF10YR` | Expected Inflation 10-year | Mensual | % | 1978 |

---

## 17. Bonos Corporativos

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `BAA` | BAA Bond Yield | Diaria | % | 1919 |
| `AAA` | AAA Bond Yield | Diaria | % | 1919 |
| `BAA10Y` | Spread BAA - 10y Treasury | Diaria | % | 1986 |
| `AAA10Y` | Spread AAA - 10y Treasury | Diaria | % | 1986 |
| `MBAA` | Mortgage Bankers Association Index | Semanal | Índice | 1990 |

---

## 18. Indicadores de Confianza y Encuestas

| Serie | Descripción | Freq | Unidad | Desde |
|-------|-------------|------|--------|-------|
| `UMCSENT` | Consumer Sentiment (U. Michigan) | Mensual | Índice | 1978 |
| `CSCICP03USM665S` | Consumer Confidence (OECD) | Mensual | Índice | 1960 |
| `NAPM` | ISM Manufacturing PMI | Mensual | Índice | 1948 |
| `ISM.NMI` | ISM Services PMI (non-manufacturing) | Mensual | Índice | 1997 |
| `BPPRIV` | Business Production Index | Mensual | Índice | 2003 |
| `NFCI` | National Financial Conditions Index | Semanal | Índice | 1973 |

---

## 19. Datos Regionales (Selección)

| Serie | Descripción | Freq | Unidad |
|-------|-------------|------|--------|
| `NYURSA` | Unemployment Rate - New York | Mensual | % |
| `CAURSA` | Unemployment Rate - California | Mensual | % |
| `TXURSA` | Unemployment Rate - Texas | Mensual | % |
| `FLURSA` | Unemployment Rate - Florida | Mensual | % |
| `NYBPPRIV` | Business Production - New York | Mensual | Índice |
| `CAHOUST` | Housing Starts - California | Mensual | Miles |

---

## Cómo encontrar más series

Usar el endpoint `series/search` con `search_type=full_text`:

```python
import requests
API_KEY = "TU_API_KEY"
params = {
    "api_key": API_KEY,
    "file_type": "json",
    "search_text": "unemployment rate youth",
    "search_type": "full_text",
    "limit": 50
}
r = requests.get("https://api.stlouisfed.org/fred/series/search", params=params)
```

Alternativamente, usar el script [`search_series.py`](../scripts/search_series.py).

---

## Tags útiles para filtrar

| Tag | Descripción |
|-----|-------------|
| `daily` | Frecuencia diaria |
| `monthly` | Frecuencia mensual |
| `quarterly` | Frecuencia trimestral |
| `annual` | Frecuencia anual |
| `weekly` | Frecuencia semanal |
| `seasonally adjusted` | Ajuste estacional |
| `not seasonally adjusted` | Sin ajuste estacional |
| `nation` | Datos nacionales |
| `regional` | Datos regionales |
| `industry` | Datos sectoriales |
| `money` | Monetarios |
| `interest rate` | Tasas de interés |
| `inflation` | Inflación |
| `employment` | Empleo |
| `gdp` | PIB |
| `housing` | Vivienda |
