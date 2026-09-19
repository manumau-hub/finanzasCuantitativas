# Morningstar Data Points (securityDataPoints)

Lista de los **28 campos** disponibles en el endpoint `/security/screener`, mas los **5 categóricos**. Todos se pasan como una lista pipe-separated en el parametro `securityDataPoints` del query string.

**Total: 33 campos** (5 categóricos + 23 numéricos + 5 metadata).

---

## Como usar

```bash
# Ver todos
python scripts/fetch_morningstar.py fields

# Descargar un sub-set
python scripts/fetch_morningstar.py screener --universe XNAS \
    --fields Ticker Name ClosePrice MarketCap PERatio

# Default: los 33 campos (todos)
python scripts/fetch_morningstar.py screener --universe XNAS
```

---

## Metadata (5 campos, siempre disponibles)

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `Ticker` | string | Simbolo en el exchange (ej: `AAPL`, `YPFD`) |
| `Name` | string | Nombre completo de la empresa (ej: `Apple Inc`) |
| `PerformanceId` | string | ID unico por listing (formato `0P0000XXXXX`). **Es la clave primaria.** |
| `Universe` | string | Universe code (ej: `E0EXG$XNAS`, `E0EXG$XBUE`) |
| `MarketCountryName` | string | Pais del instrumento en formato `United States`, `Argentina`, etc. (siempre en inglés) |

> **PerformanceId** es la unica clave estable. El mismo "Apple Inc" en diferentes exchanges tiene diferentes PerformanceId. Si querés matchear datos entre universes, usar el nombre + ticker + market country, no PerformanceId.

---

## Categoricos (5 campos)

| Campo | Tipo | Valores posibles | Descripcion |
|-------|------|------------------|-------------|
| `SectorName` | string | 11 sectores (ver abajo) | Sector Morningstar |
| `IndustryName` | string | ~145 industrias (ver abajo) | Industria especifica |
| `EquityStyleBox` | int 1-9 | Matriz 3x3 (ver abajo) | Estilo + tamano |
| `QuantitativeStarRating` | float 1-5 | 1, 2, 3, 4, 5 | Rating cuantitativo (estrellas) |
| `ExchangeName` | string | (no incluido por default) | Exchange name (no usado por el notebook) |

### 11 Sectores posibles (SectorName)

```
Basic Materials
Communication Services
Consumer Cyclical
Consumer Defensive
Energy
Financial Services
Healthcare
Industrials
Real Estate
Technology
Utilities
```

### Matriz EquityStyleBox (1-9)

```
            Value    Blend    Growth
Large        1        2         3
Mid          4        5         6
Small        7        8         9
```

> Ejemplos:
> - `1` = Large Value (empresa grande, estilo value)
> - `5` = Mid Blend (mediana, mixta)
> - `9` = Small Growth (chica, crecimiento)

### QuantitativeStarRating

Rating cuantitativo de Morningstar:
- `1` = baja calidad
- `5` = alta calidad

> **Nota:** en muchos listings viene como `NaN`/vacio. Solo aplica a acciones con suficiente cobertura.

### ~145 Industrias (IndustryName)

Lista completa (las 145 del set estandar de Morningstar):

```
Advertising Agencies                 Aerospace & Defense                  Agricultural Inputs
Airlines                             Airports & Air Services              Aluminum
Apparel Manufacturing                Apparel Retail                       Asset Management
Auto & Truck Dealerships             Auto Manufacturers                  Auto Parts
Banks - Diversified                  Banks - Regional                     Beverages - Brewers
Beverages - Non-Alcoholic            Beverages - Wineries & Distilleries  Biotechnology
Broadcasting                         Building Materials                   Building Products & Equipment
Business Equipment & Supplies        Capital Markets                      Chemicals
Coking Coal                          Communication Equipment              Computer Hardware
Confectioners                        Conglomerates                        Consulting Services
Consumer Electronics                 Copper                               Credit Services
Department Stores                    Diagnostics & Research               Discount Stores
Drug Manufacturers - General         Drug Manufacturers - Specialty       Education & Training Services
Electrical Equipment & Parts         Electronic Components                Electronic Gaming & Multimedia
Electronics & Computer Distribution  Engineering & Construction            Entertainment
Farm & Heavy Construction Machinery  Farm Products                        Financial Conglomerates
Financial Data & Stock Exchanges     Food Distribution                    Footwear & Accessories
Furnishings, Fixtures & Appliances   Gambling                             Gold
Grocery Stores                       Health Information Services          Healthcare Plans
Home Improvement Retail              Household & Personal Products        Industrial Distribution
Information Technology Services      Infrastructure Operations            Insurance - Diversified
Insurance - Life                     Insurance - Property & Casualty       Insurance - Reinsurance
Insurance - Specialty                Insurance Brokers                    Integrated Freight & Logistics
Internet Content & Information       Internet Retail                      Leisure
Lodging                              Lumber & Wood Production             Luxury Goods
Marine Shipping                      Medical Care Facilities              Medical Devices
Medical Distribution                 Medical Instruments & Supplies       Metal Fabrication
Mortgage Finance                     Oil & Gas Drilling                   Oil & Gas E&P
Oil & Gas Equipment & Services       Oil & Gas Integrated                 Oil & Gas Midstream
Oil & Gas Refining & Marketing       Other Industrial Metals & Mining     Other Precious Metals & Mining
Packaged Foods                       Packaging & Containers               Paper & Paper Products
Personal Services                    Pharmaceutical Retailers             Pollution & Treatment Controls
Publishing                           REIT - Diversified                   REIT - Healthcare Facilities
REIT - Hotel & Motel                 REIT - Industrial                    REIT - Mortgage
REIT - Office                        REIT - Residential                   REIT - Retail
REIT - Specialty                     Railroads                            Real Estate - Development
Real Estate - Diversified            Real Estate Services                 Recreational Vehicles
Rental & Leasing Services            Residential Construction             Resorts & Casinos
Restaurants                          Scientific & Technical Instruments   Security & Protection Services
Semiconductor Equipment & Materials  Semiconductors                       Shell Companies
Silver                               Software - Application               Software - Infrastructure
Solar                                Specialty Business Services          Specialty Chemicals
Specialty Industrial Machinery       Specialty Retail                     Staffing & Employment Services
Steel                                Telecom Services                     Textile Manufacturing
Thermal Coal                         Tobacco                              Tools & Accessories
Travel Services                      Trucking                             Uranium
Utilities - Diversified              Utilities - Independent Power Producers
Utilities - Regulated Electric       Utilities - Regulated Gas            Utilities - Regulated Water
Utilities - Renewable                Waste Management
```

> **Nota:** CEDEARs en XBUE usan las industrias en inglés (porque el script fuerza `languageId=en-GB`). En universes europeos, los nombres vienen en el idioma local.

---

## Numericos (23 campos)

### Tamano y precio (2)

| Campo | Tipo | Unidad | Descripcion |
|-------|------|--------|-------------|
| `ClosePrice` | float | moneda del universe | Precio de cierre |
| `MarketCap` | float | moneda del universe | Capitalizacion de mercado (en la currency local, ej: ARS para XBUE, EUR para XETR) |

### Valuacion (3)

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `PERatio` | float | Price-to-Earnings (TTM) |
| `PEGRatio` | float | Price/Earnings to Growth ratio |
| `DividendYield` | float | Dividend yield anualizado (%) |

### Calidad financiera (6)

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `DebtEquityRatio` | float | Deuda total / Equity |
| `NetMargin` | float | Net income / Revenue (%) |
| `EBTMarginYear1` | float | Earnings Before Tax margin (ultimo año fiscal, %) |
| `ROATTM` | float | Return on Assets (TTM, %) |
| `ROETTM` | float | Return on Equity (TTM, %) |
| `ROEYear1` | float | Return on Equity (ultimo año fiscal, %) |
| `ROICYear1` | float | Return on Invested Capital (ultimo año fiscal, %) |

### Crecimiento (2)

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `EPSGrowth3YYear1` | float | EPS growth 3Y anualizado (%) |
| `RevenueGrowth3Y` | float | Revenue growth 3Y anualizado (%) |

### Retornos (9)

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `ReturnD1` | float | Retorno 1 dia (%) |
| `ReturnW1` | float | Retorno 1 semana (%) |
| `ReturnM0` | float | Retorno mes actual / MTD (%) |
| `ReturnM1` | float | Retorno 1 mes (%) |
| `ReturnM3` | float | Retorno 3 meses (%) |
| `ReturnM6` | float | Retorno 6 meses (%) |
| `ReturnM12` | float | Retorno 12 meses / 1Y (%) |
| `ReturnM36` | float | Retorno 36 meses / 3Y (%) |
| `ReturnM60` | float | Retorno 60 meses / 5Y (%) |
| `ReturnM120` | float | Retorno 120 meses / 10Y (%) |

> **Nota:** muchos CEDEARs (XBUE) y small caps tienen `NaN` (vacio) en algunos campos, especialmente DividendYield, PERatio, ROE/ROA, etc. Es normal.

---

## Ejemplo de response

```json
{
  "rows": [
    {
      "Ticker": "AAPL",
      "PerformanceId": "0P000000GY",
      "Name": "Apple Inc",
      "ClosePrice": 311.23,
      "MarketCap": 4571145807880,
      "MarketCountryName": "United States",
      "SectorName": "Technology",
      "IndustryName": "Consumer Electronics",
      "EquityStyleBox": 6.0,
      "QuantitativeStarRating": 4.0,
      "PERatio": 32.5,
      "PEGRatio": 2.5,
      "DividendYield": 0.4,
      "DebtEquityRatio": 1.5,
      "NetMargin": 0.25,
      "EBTMarginYear1": 0.28,
      "ROATTM": 0.15,
      "ROETTM": 1.5,
      "ROEYear1": 1.6,
      "ROICYear1": 0.4,
      "EPSGrowth3YYear1": 0.05,
      "RevenueGrowth3Y": 0.03,
      "ReturnD1": 0.31,
      "ReturnW1": 1.2,
      "ReturnM0": 5.0,
      "ReturnM1": 5.0,
      "ReturnM3": 10.0,
      "ReturnM6": 12.0,
      "ReturnM12": 25.0,
      "ReturnM36": 50.0,
      "ReturnM60": 100.0,
      "ReturnM120": 800.0,
      "Universe": "E0EXG$XNAS"
    }
  ]
}
```

> Los valores son ilustrativos. En la realidad son los datos actuales de cada listing.

---

## Cuantos campos se pueden pedir?

No hay limite explicito documentado. El script usa los 33 por default y anda bien. Pedir mas campos puede hacer la respuesta mas lenta pero no deberia fallar.
