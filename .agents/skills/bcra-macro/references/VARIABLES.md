# Listado completo de variables de la API BCRA Macro v4.0 (nivel nacional)

**Total: 638 variables nacionales** (filtra las series provinciales/municipales).

Cada fila tiene: `ID` | `Descripción` | `Periodicidad` (D/M) | `Unidad` | `Moneda` (ML=pesos, ME=dólares, MEyML=agregado, USD=USD).

**Regenerar este archivo:**
```python
import requests, pandas as pd
r = requests.get("https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias", params={"Limit": 3000, "Offset": 0})
df = pd.DataFrame(r.json()["results"])
df = df[~df["descripcion"].str.contains("provincia de |Provincia de |Gobierno Provincial", na=False)]
df = df[~(df["descripcion"].str.contains("provincial|municipal", na=False) & ~df["descripcion"].str.contains("nacional", na=False))]
df.to_csv("VARIABLES.csv", index=False)
```

## Principales Variables (35 variables)

Indicadores macro headline (reservas, tipo de cambio, tasas, base monetaria, CER, UVA, IPC, agregados M1/M2/M3, banda cambiaria).

| ID | Descripción | Per. | Unidad | Moneda |
|---|---|---|---|---|
| 1 | Reservas internacionales | D | En millones de USD | ME |
| 4 | Tipo de cambio minorista (promedio vendedor) | D | Pesos argentinos por dólar estadounidense | ML |
| 5 | Tipo de cambio mayorista de referencia | D | Pesos argentinos por dólar estadounidense | ML |
| 7 | Tasa de interés BADLAR de bancos privados | D | En porcentaje nominal anual | ML |
| 8 | Tasa de interés TM20 de bancos privados  | D | En porcentaje nominal anual | ML |
| 11 | Tasa de interés de préstamos entre entidades financiera privadas (BAIBAR)   | D | En porcentaje nominal anual | ML |
| 12 | Tasa de interés de depósitos a 30 días de plazo en entidades financieras  | D | En porcentaje nominal anual | ML |
| 13 | Tasa de interés por adelantos en cuenta corriente  | D | En porcentaje nominal anual | ML |
| 14 | Tasa de interés de préstamos personales  | D | En porcentaje nominal anual | ML |
| 15 | Base monetaria | D | En millones de ARS | ML |
| 16 | Circulación monetaria  | D | En millones de ARS | ML |
| 17 | Billetes y monedas en poder del público | D | En millones de ARS | ML |
| 18 | Efectivo en pesos en entidades financieras  | D | En millones de ARS | ML |
| 19 | Depósitos de las entidades financieras en cuenta corriente en el BCRA | D | En millones de ARS | ML |
| 21 | Depósitos en efectivo en las entidades financieras  | D | En millones de ARS | MEyML |
| 22 | Depósitos en efectivo en las entidades financieras en cuentas corrientes(neto de utilización FUCO) | D | En millones de ARS | MEyML |
| 23 | Depósitos en efectivo en las entidades financieras en cajas de ahorro | D | En millones de ARS | MEyML |
| 24 | Depósitos a plazo en efectivo en las entidades financieras (incluye inversiones y excluye CEDROs)  | D | En millones de ARS | MEyML |
| 25 | Variación interanual del promedio móvil de 30 días del M2 privado | D | En porcentaje | ML |
| 26 | Préstamos de las entidades financieras al sector privado | D | En millones de ARS | MEyML |
| 27 | Variación mensual del índice de precios al consumidor | M | En porcentaje | ML |
| 28 | Variación interanual del índice de precios al consumidor | M | En porcentaje | ML |
| 29 | Mediana de la variación interanual próximos 12 meses del índice de precios al consumidor del relevamiento de expectativas de mercado | M | En porcentaje | ML |
| 30 | Coeficiente de estabilización de referencia (base 2.2.02=1) | D | Índice base 2.2.02=1 | ML |
| 31 | Unidad de valor adquisitivo (base 31.3.16=14.05) | D | En ARS | ML |
| 32 | Unidad de vivienda (base 31.3.16=14.05) | D | En ARS | ML |
| 35 | Tasa de interés BADLAR de bancos privados | D | En porcentaje efectivo anual | ML |
| 40 | Índice para Contratos de Locación (base 30.6.20=1) | D | Índice base 30.6.20=1 | ML |
| 43 | Tasa de interés Comunicado P 14.290 (Uso de justicia) | D | En porcentaje | ML |
| 44 | Tasa de interes TAMAR de bancos privados  | D | En porcentaje nominal anual | ML |
| 45 | Tasa de interés TAMAR de bancos privados | D | En porcentaje efectivo anual | ML |
| 1187 | Régimen de bandas cambiarias. Límite inferior | D | Pesos argentinos por dólar estadounidense | ML |
| 1188 | Régimen de bandas cambiarias. Límite superior | D | Pesos argentinos por dólar estadounidense | ML |
| 1197 | Tasa de Intereses Moratorios (TIM)  CCC, art. 768(c) | D | En porcentaje | ML |
| 1198 | Tasa pasiva Ley 27.802, art. 55(a) | D | En porcentaje | ML |

## Informe Monetario Diario (33 variables)

Series diarias del IMD: efectivo en entidades, cuentas corrientes en BCRA, factores de variación de la base.

| ID | Descripción | Per. | Unidad | Moneda |
|---|---|---|---|---|
| 1199 | Tasa de interés de adelantos en cuenta corriente a tasa fija  | M | En porcentaje nominal anual | ML |
| 1200 | Efectivo en moneda extranjera en entidades financieras  | D | En millones de USD | ME |
| 1201 | Líneas del exterior comerciales (obligaciones de las entidades financieras con entidades del exterior) | D | En millones de USD | ME |
| 1202 | Líneas del exterior financieras (obligaciones de las entidades financieras con entidades del exterior) | D | En millones de USD | ME |
| 1215 | Tasa de interés de financiaciones con tarjetas de crédito | M | En porcentaje nominal anual | ML |
| 1216 | Tasa de interés de documentos a sola firma a tasa fija  | M | En porcentaje nominal anual | ML |
| 1217 | Tasa de interés de préstamos hipotecarios a tasa fija  | M | En porcentaje nominal anual | ML |
| 1218 | Tasa de interés de préstamos prendarios a tasa fija  | M | En porcentaje nominal anual | ML |
| 1219 | Tasa de interés de préstamos personales a tasa fija  | M | En porcentaje nominal anual | ML |
| 1220 | Tasa de interés de financiaciones con tarjetas de crédito con tasa distinta de cero | M | En porcentaje nominal anual | ML |
| 1221 | Liquidez en pesos de las entidades financieras | D | Porcentaje de depósitos | ML |
| 1222 | Cheques Cancelatorios en moneda extranjera y Certificados de Depósitos para la Inversión (CEDIN) | D | En millones de USD | ME |
| 1223 | LEGAR y LEMIN  | D | En millones de ARS | ML |
| 1224 | Créditos del BCRA al sistema financiero | D | En millones de ARS | ML |
| 1225 | Adelantos transitorios del BCRA al Gobierno Nacional | D | En millones de ARS | ML |
| 1226 | Reservas Internacionales expresadas en pesos | D | En millones de ARS | ML |
| 1227 | Tasa de interes de depósitos a plazo fijo UVA | D | En porcentaje nominal anual | ML |
| 1228 | Liquidez de las entidades financieras en pesos y en moneda extranjera | D | Porcentaje de depósitos | MEyML |
| 1229 | Depósitos del sector público | D | En millones de ARS | ML |
| 1230 | Depósitos a la vista del sector público (cuentas corrientes y cajas de ahorro) | D | En millones de ARS | ML |
| 1231 | Depósitos a plazo del sector público (a plazo fijo e inversiones) | D | En millones de ARS | ML |
| 1232 | M1  (billetes y monedas en poder del público+cheques cancelatorios en pesos+ cuentas corrientes del s. priv. s. púb. en pesos) | D | En millones de ARS | ML |
| 1233 | M2 (M1 + cajas de ahorro del s. privado y del s. público en pesos) | D | En millones de ARS | ML |
| 1234 | M3 (M2 + depósitos a plazo y otros depósitos del s. privado y s. público en pesos) | D | En millones de ARS | ML |
| 1235 | Préstamos otorgados al sector privado mediante adelantos y documentos | D | En millones de ARS | MEyML |
| 1236 | Préstamos personales y mediante tarjetas de crédito | D | En millones de ARS | MEyML |
| 1237 | Préstamos hipotecarios y prendarios otorgados al sector privado | D | En millones de ARS | MEyML |
| 1238 | Otros préstamos otorgados al sector privado | D | En millones de ARS | MEyML |
| 1239 | M2 Privado (billetes y monedas en poder del público+ cheques cancelatorios en pesos+cuentas corrientes y cajas de ahorros en pesos del sector privado) | D | En millones de ARS | ML |
| 1240 | Tasa de interés de préstamos hipotecarios de UVA | M | En porcentaje nominal anual | ML |
| 1241 | Depósitos a la vista del sector privado (cuentas corrientes y cajas de ahorro) | D | En millones de ARS | ML |
| 1242 | Depósitos a plazo del sector privado (a plazo fijo e inversiones) | D | En millones de ARS | ML |
| 1243 | Cuentas corrientes en moneda extranjera en el BCRA | D | En millones de USD | ME |

## Series.xlsm (154 variables)

Factores de variación de la base monetaria, reservas internacionales, compras netas de divisas, LELIQ, pases, adelantos.

| ID | Descripción | Per. | Unidad | Moneda |
|---|---|---|---|---|
| 46 | Total de factores de explicación de la base monetaria | D | En millones de ARS | ML |
| 47 | Efecto monetario de las compras netas de divisas al sector privado y otros  | D | En millones de ARS | ML |
| 48 | Efecto monetario de las compras netas de divisas al tesoro nacional  | D | En millones de ARS | ML |
| 49 | Efecto monetario de los adelantos transitorios al tesoro nacional | D | En millones de ARS | ML |
| 50 | Efecto monetario de las transferencia de utilidades al tesoro nacional  | D | En millones de ARS | ML |
| 51 | Efecto monetario del resto de operaciones con el tesoro nacional | D | En millones de ARS | ML |
| 52 | Efecto monetario de las operaciones de pases  | D | En millones de ARS | ML |
| 53 | Efecto monetario de las LELIQ y NOTALQ  | D | En millones de ARS | ML |
| 54 | Efecto monetario de los redescuentos y adelantos  | D | En millones de ARS | ML |
| 55 | Efecto monetario de los intereses, primas y remuneración de cuentas corrientes asociados a op. de pases, LELIQ, NOTALQ, redescuentos y adel.  | D | En millones de ARS | ML |
| 56 | Efecto monetario de las LEBAC y NOBAC  | D | En millones de ARS | ML |
| 57 | Efecto monetario del rescate de cuasimonedas  | D | En millones de ARS | ML |
| 58 | Efecto monetario de las operaciones con letras fiscales de liquidez  | D | En millones de ARS | ML |
| 59 | Efecto monetario de otras operaciones que explican la variación de la base monetaria  | D | En millones de ARS | ML |
| 60 | Billetes y monedas en poder del público  | D | En millones de ARS | ML |
| 61 | Billetes y monedas en entidades financieras  | D | En millones de ARS | ML |
| 62 | Cheques cancelatorios  | D | En millones de ARS | ML |
| 63 | Cuentas corrientes en pesos en el BCRA | D | En millones de ARS | ML |
| 64 | Base monetaria | D | En millones de ARS | ML |
| 65 | Cuasimonedas  | D | En millones de ARS | ML |
| 66 | Base monetaria más cuasimonedas  | D | En millones de ARS | ML |
| 67 | Billetes y monedas en poder del público  | D | En millones de ARS | ML |
| 68 | Billetes y monedas en entidades financieras  | D | En millones de ARS | ML |
| 69 | Cheques cancelatorios  | D | En millones de ARS | ML |
| 70 | Cuentas corrientes en pesos en el BCRA  | D | En millones de ARS | ML |
| 71 | Base monetaria | D | En millones de ARS | ML |
| 72 | Cuasimonedas  | D | En millones de ARS | ML |
| 73 | Base monetaria más cuasimonedas | D | En millones de ARS | ML |
| 74 | Reservas internacionales (excluidas asignaciones deg 2009) | D | En millones de USD | ME |
| 75 | Oro, divisas, colocaciones a plazo y otros activos de reserva | D | En millones de USD | ME |
| 76 | Divisas-pase pasivo en dólares con el exterior | D | En millones de USD | ME |
| 77 | Reservas internacionales  | D | En millones de USD | ME |
| 78 | Variación de reservas internacionales por compra de divisas  | D | En millones de USD | ME |
| 79 | Variación de reservas internacionales por operaciones con organismos internacionales | D | En millones de USD | ME |
| 80 | Variación de reservas internacionales por otras operaciones del sector público  | D | En millones de USD | ME |
| 81 | Variación de reservas internacionales por efectivo mínimo  | D | En millones de USD | ME |
| 82 | Variación de reservas internacionales por otras operaciones no incluidas en otros rubros  | D | En millones de USD | ME |
| 83 | Asignaciones de DEGS del año 2009 | D | En millones de USD | ME |
| 84 | Tipo de cambio de valuación contable | D | Pesos argentinos por dólar estadounidense | ML |
| 85 | Cuentas corrientes de los sectores público y privado no financieros | D | En millones de ARS | ML |
| 86 | Cajas de ahorro de los sectores público y privado no financieros | D | En millones de ARS | ML |
| 87 | Depósitos a plazo no ajustables por CER/UVAS de los sectores público y privado no financieros | D | En millones de ARS | ML |
| 88 | Depósitos a plazo ajustables por CER/UVAS de los sectores público y privado no financieros | D | En millones de ARS | ML |
| 89 | Otros depósitos de los sectores público y privado no financieros | D | En millones de ARS | ML |
| 90 | Cedros con cer de los sectores público y privado no financieros | D | En millones de ARS | ML |
| 91 | Depósitos en pesos de los sectores público y privados no financieros (incluye cedros) | D | En millones de ARS | ML |
| 92 | BODEN de los sectores público y privado no financieros | D | En millones de ARS | ML |
| 93 | Depósitos de los sectores público y privados no financieros (incluye cedro y BODEN) | D | En millones de ARS | ML |
| 94 | Cuentas corrientes del sector privado no financiero  | D | En millones de ARS | ML |
| 95 | Cajas de ahorro del sector privado no financiero  | D | En millones de ARS | ML |
| 96 | Depósitos a plazo no ajustables por CER/UVAS del sector privado no financiero  | D | En millones de ARS | ML |
| 97 | Depósitos a plazo ajustables por CER/UVAS del sector privado no financiero  | D | En millones de ARS | ML |
| 98 | Otros depósitos del sector privado no financiero | D | En millones de ARS | ML |
| 99 | Cedros con cer del sector privado no financiero  | D | En millones de ARS | ML |
| 100 | Depósitos del sector privado no financiero (incluye cedros) | D | En millones de ARS | ML |
| 101 | BODEN del sector privado no financiero  | D | En millones de ARS | ML |
| 102 | Depósitos del sector privado no financiero (incluye cedro y BODEN) | D | En millones de ARS | ML |
| 103 | Depósitos  de los sectores público y privado no financieros | D | En millones de ARS | ME |
| 104 | Depósitos del sector privado no financiero | D | En millones de ARS | ME |
| 105 | Depósitos  de los sectores público y privado no financieros | D | En millones de ARS | MEyML |
| 106 | Depósitos del sector privado no financiero | D | En millones de ARS | MEyML |
| 107 | Depósitos  de los sectores público y privado no financieros | D | En millones de USD | ME |
| 108 | Depósitos del sector privado no financiero | D | En millones de USD | ME |
| 109 | M2  | D | En millones de ARS | ML |
| 110 | Préstamos otorgados mediante adelantos en cuenta al sector privado  | D | En millones de ARS | ML |
| 111 | Préstamos otorgados mediante documentos al sector privado  | D | En millones de ARS | ML |
| 112 | Préstamos hipotecaríos otorgados al sector privado | D | En millones de ARS | ML |
| 113 | Préstamos prendaríos otorgados al sector privado | D | En millones de ARS | ML |
| 114 | Préstamos personales otorgados al sector privado | D | En millones de ARS | ML |
| 115 | Préstamos mediante tarjeta de créditos otorgados al sector privado | D | En millones de ARS | ML |
| 116 | Otros préstamos otorgados al sector privado | D | En millones de ARS | ML |
| 117 | Préstamos otorgados al sector privado  | D | En millones de ARS | ML |
| 118 | Préstamos en cuenta corriente otorgados al sector privado  | D | En millones de USD | ME |
| 119 | Préstamos documentaríos otorgados al sector privado | D | En millones de USD | ME |
| 120 | Préstamos hipotecaríos otorgados al sector privado | D | En millones de USD | ME |
| 121 | Préstamos prendaríos otorgados al sector privado | D | En millones de USD | ME |
| 122 | Préstamos personales otorgados al sector privado | D | En millones de USD | ME |
| 123 | Préstamos en tarjeta de créditos otorgados al sector privado | D | En millones de USD | ME |
| 124 | Otros préstamos otorgados al sector privado | D | En millones de USD | ME |
| 125 | Préstamos otorgados al sector privado  | D | En millones de USD | ME |
| 126 | Préstamos otorgados al sector privado  | D | En millones de ARS | ME |
| 127 | Préstamos otorgados al sector privado  | D | En millones de ARS | MEyML |
| 135 | Tasa de interés TAMAR de bancos públicos y privados | D | En porcentaje nominal anual | ML |
| 136 | Tasa de interés TAMAR de bancos privados | D | En porcentaje nominal anual | ML |
| 137 | Tasa de interés TAMAR de bancos privados | D | En porcentaje efectivo anual | ML |
| 138 | Tasa de interés BADLAR de bancos públicos y privados | D | En porcentaje nominal anual | ML |
| 139 | Tasa de interés BADLAR de bancos privados | D | En porcentaje nominal anual | ML |
| 140 | Tasa de interés BADLAR de bancos privados | D | En porcentaje efectivo anual | ML |
| 141 | Tasa de interés TM20 de bancos públicos y privados | D | En porcentaje nominal anual | ML |
| 142 | Tasa de interésTM20 de bancos privados | D | En porcentaje nominal anual | ML |
| 143 | Tasa de interés TM20 de bancos privados | D | En porcentaje efectivo anual | ML |
| 144 | Tasa de interés de préstamos personales otorgados al sector privado | D | En porcentaje nominal anual | ML |
| 145 | Tasa de interés de adelantos en cuenta corriente, con acuerdo de 1 a 7 días y de 10 millones o más, a empresas del sector privado | D | En porcentaje nominal anual | ML |
| 146 | Tasa de interés de préstamos entre bancos privados (BAIBAR) | D | En porcentaje nominal anual | ML |
| 147 | Préstamos entre bancos privados (BAIBAR) | D | En millones de ARS | ML |
| 148 | Tasa de interés de préstamos entre entidades financieras locales | D | En porcentaje nominal anual | ML |
| 149 | Préstamos entre entidades financieras locales  | D | En millones de ARS | ML |
| 150 | Tasa de interés por operaciones de pases entre terceros a 1 día | D | En porcentaje nominal anual | ML |
| 151 | Operaciones de pases entre terceros a 1 día | D | En millones de ARS | ML |
| 152 | Pases pasivos para el BCRA (incluye pases pasivos con fci) | D | En millones de ARS | ML |
| 153 | Pases pasivos para el BCRA con fondos comunes de inversión | D | En millones de ARS | ML |
| 154 | Pases activos para el BCRA | D | En millones de ARS | ML |
| 155 | LELIQ y NOTALQ | D | En millones de ARS | ML |
| 156 | LEBAC y NOBAC , LEGAR y LEMIN  | D | En millones de ARS | ML |
| 157 | LEBAC y NOBAC  de entidades financieras  | D | En millones de ARS | ML |
| 158 | LEBAC, LEDIV y BOPREAL | D | En millones de USD | USD |
| 159 | NOCOM  | D | En millones de ARS | ML |
| 160 | Tasas de interés de política monetaria | D | En porcentaje nominal anual | ML |
| 161 | Tasas de interés de política monetaria | D | En porcentaje efectivo anual | ML |
| 162 | Tasa de interés por pases pasivos para el BCRA a 1 día | D | En porcentaje nominal anual | ML |
| 163 | Tasa de interés por pases pasivos para el BCRA a 7 días | D | En porcentaje nominal anual | ML |
| 164 | Tasa de interés por pases activos para el BCRA a 1 día | D | En porcentaje nominal anual | ML |
| 165 | Tasa de interés por pases activos para el BCRA a 7 días | D | En porcentaje nominal anual | ML |
| 166 | Tasa de interés de LEBAC / LELIQ de 1 mes | D | En porcentaje nominal anual | ML |
| 167 | Tasa de interés de LEBAC de 2 meses | D | En porcentaje nominal anual | ML |
| 168 | Tasa de interés de LEBAC de 3 meses | D | En porcentaje nominal anual | ML |
| 169 | Tasa de interés de LEBAC de 4 meses | D | En porcentaje nominal anual | ML |
| 170 | Tasa de interés de LEBAC de 5 meses | D | En porcentaje nominal anual | ML |
| 171 | Tasa de interés de LEBAC / LELIQ a 6 meses | D | En porcentaje nominal anual | ML |
| 172 | Tasa de interés de LEBAC  de 7 meses | D | En porcentaje nominal anual | ML |
| 173 | Tasa de interés de LEBAC  de 8 meses | D | En porcentaje nominal anual | ML |
| 174 | Tasa de interés de LEBAC  de 9 meses | D | En porcentaje nominal anual | ML |
| 175 | Tasa de interés de LEBAC  de 10 meses | D | En porcentaje nominal anual | ML |
| 176 | Tasa de interés de LEBAC  de 11 meses | D | En porcentaje nominal anual | ML |
| 177 | Tasa de interés de LEBAC  de 12 meses | D | En porcentaje nominal anual | ML |
| 178 | Tasa de interés de LEBAC  de 18 meses | D | En porcentaje nominal anual | ML |
| 179 | Tasa de interés de LEBAC  de 24 meses | D | En porcentaje nominal anual | ML |
| 180 |  Tasa de interés de LEBAC  ajustables por CER de 6 meses | D | En porcentaje nominal anual | ML |
| 181 | Tasa de interés de LEBAC ajustables por CER de 12 meses | D | En porcentaje nominal anual | ML |
| 182 | Tasa de interés de LEBAC ajustables por CER de 18 meses | D | En porcentaje nominal anual | ML |
| 183 | Tasa de interés de LEBAC ajustables por CER de 24 meses | D | En porcentaje nominal anual | ML |
| 184 | Tasa de interés de LEBAC USD con liquidación en pesos, de 1 mes | D | En porcentaje nominal anual | USD |
| 185 | Tasa de interés de LEBAC USD con liquidación en pesos, de 6 meses | D | En porcentaje nominal anual | USD |
| 186 | Tasa de interés de LEBAC USD con liquidación en pesos, de 12 meses | D | En porcentaje nominal anual | USD |
| 187 | Tasa de interés de LEBAC de 1 mes | D | En porcentaje nominal anual | USD |
| 188 | Tasa de interés de LEBAC de 3 meses | D | En porcentaje nominal anual | USD |
| 189 | Tasa de interés de LEBAC de 6 meses | D | En porcentaje nominal anual | USD |
| 190 | Tasa de interés de LEBAC de 12 meses | D | En porcentaje nominal anual | USD |
| 191 | Margen sobre BADLAR bancos privados de NOBAC de 9 meses | D | En porcentaje nominal anual | ML |
| 192 | Margen sobre bancos privados de NOBAC de 12 meses  | D | En porcentaje nominal anual | ML |
| 193 | Margen sobre BADLAR total de NOBAC de 2 años | D | En porcentaje nominal anual | ML |
| 194 | Margen sobre BADLAR bancos privados de NOBAC de 2 años | D | En porcentaje nominal anual | ML |
| 195 | Margen sobre tasa de politica monetaria de NOTALIQ en pesos de 190 días | D | En porcentaje nominal anual | ML |
| 196 | LEFI en cartera de entidades financieras, en valor técnico | D | En millones de ARS | ML |
| 197 | M2 transaccional del sector privado | D | En millones de ARS | ML |
| 198 | Otros | D | En millones de ARS | ML |
| 1189 | Tasa de interés de depósitos a plazo fijo en pesos | D | En porcentaje nominal anual | ML |
| 1190 | Tasa de interés de depósitos a plazo fijo en pesos de personas humanas | D | En porcentaje nominal anual | ML |
| 1191 | Tasa de interés de depósitos a plazo fijo en pesos de prestadores de servicios financieros | D | En porcentaje efectivo anual | ML |
| 1192 | Tasa de interés de depósitos a plazo fijo en pesos de otras personas jurídicas | D | En porcentaje nominal anual | ML |
| 1193 | Tasa de interés de depósitos a plazo fijo en dólares | D | En porcentaje nominal anual | ME |
| 1194 | Tasa de interés de depósitos a plazo fijo en dólares de personas humanas | D | En porcentaje nominal anual | ME |
| 1195 | Tasa de interés de depósitos a plazo fijo en dólares de personas jurídicas | D | En porcentaje nominal anual | ME |
| 1196 | Tasa de interés de depósitos a la vista remunerados en pesos de prestadores de servicios financieros | D | En porcentaje nominal anual | ML |

## Tasas de interés de depósitos (10 variables)

Tasas de interés de depósitos desagregadas por moneda y plazo (caja de ahorro, plazo fijo, total).

| ID | Descripción | Per. | Unidad | Moneda |
|---|---|---|---|---|
| 1203 | Tasas de interés de depósitos en cajas de ahorro | D | En porcentaje nominal anual | ML |
| 1204 | Tasa de interés del total de depósitos a plazo fijo | D | En porcentaje nominal anual | ML |
| 1205 | Tasa de interés de depósitos a plazo fijo de 7 a 59 días | D | En porcentaje nominal anual | ML |
| 1207 | Tasa de interés de depósitos a plazo fijo de 30 días | D | En porcentaje nominal anual | ML |
| 1208 | Tasa de interés de depósitos a plazo fijo de 60 días o más | D | En porcentaje nominal anual | ML |
| 1209 | Tasas de interés de depósitos en cajas de ahorro | D | En porcentaje nominal anual | ME |
| 1210 | Tasa de interés del total de depósitos a plazo fijo | D | En porcentaje nominal anual | ME |
| 1211 | Tasa de interés de depósitos a plazo fijo de 7 a 59 días | D | En porcentaje nominal anual | ME |
| 1213 | Tasa de interés de depósitos a plazo fijo de 30 días | D | En porcentaje nominal anual | ME |
| 1214 | Tasa de interés de depósitos a plazo fijo de 60 días o más | D | En porcentaje nominal anual | ME |

## Préstamos por tipo de titular y destino (74 variables)

Préstamos por destino (hipotecarios, prendarios, personales, comerciales) y por moneda. Nivel nacional.

| ID | Descripción | Per. | Unidad | Moneda |
|---|---|---|---|---|
| 1113 | Préstamos hipotecarios para construcción de viviendas | M | En miles de ARS | MEyML |
| 1114 | Préstamos hipotecarios para refacción de vivienda | M | En miles de ARS | MEyML |
| 1115 | Préstamos hipotecarios para compra de nuevas viviendas | M | En miles de ARS | MEyML |
| 1116 | Préstamos hipotecarios para compra de viviendas usadas | M | En miles de ARS | MEyML |
| 1117 | Préstamos hipotecarios para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | MEyML |
| 1118 | Préstamos prendarios para compra de automotores | M | En miles de ARS | MEyML |
| 1119 | Préstamos prendarios para compra de maquinarias | M | En miles de ARS | MEyML |
| 1120 | Préstamos prendarios no destinados a la compra de automotores o maquinarias | M | En miles de ARS | MEyML |
| 1121 | Préstamos hipotecarios para construcción de viviendas | M | En miles de ARS | ML |
| 1122 | Préstamos hipotecarios para refacción de vivienda | M | En miles de ARS | ML |
| 1123 | Préstamos hipotecarios para compra de nuevas viviendas | M | En miles de ARS | ML |
| 1124 | Préstamos hipotecarios para compra de viviendas usadas | M | En miles de ARS | ML |
| 1125 | Préstamos hipotecarios para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | ML |
| 1126 | Préstamos prendarios para compra de automotores | M | En miles de ARS | ML |
| 1127 | Préstamos prendarios para compra de maquinarias | M | En miles de ARS | ML |
| 1128 | Préstamos prendarios no destinados a la compra de automotores o maquinarias | M | En miles de ARS | ML |
| 1129 | Préstamos hipotecarios para construcción de viviendas | M | En miles de ARS | ME |
| 1130 | Préstamos hipotecarios para refacción de vivienda | M | En miles de ARS | ME |
| 1131 | Préstamos hipotecarios para compra de nuevas viviendas | M | En miles de ARS | ME |
| 1132 | Préstamos hipotecarios para compra de viviendas usadas | M | En miles de ARS | ME |
| 1133 | Préstamos hipotecarios para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | ME |
| 1134 | Préstamos prendarios para compra de automotores | M | En miles de ARS | ME |
| 1135 | Préstamos prendarios para compra de maquinarias | M | En miles de ARS | ME |
| 1136 | Préstamos prendarios no destinados a la compra de automotores o maquinarias | M | En miles de ARS | ME |
| 1137 | Préstamos hipotecarios a personas humanas para construcción de viviendas | M | En miles de ARS | MEyML |
| 1138 | Préstamos hipotecarios a personas humanas para refacción de vivienda | M | En miles de ARS | MEyML |
| 1139 | Préstamos hipotecarios a personas humanas para compra de nuevas viviendas | M | En miles de ARS | MEyML |
| 1140 | Préstamos hipotecarios a personas humanas para compra de viviendas usadas | M | En miles de ARS | MEyML |
| 1141 | Préstamos hipotecarios a personas humanas para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | MEyML |
| 1142 | Préstamos prendarios a personas humanas para compra de automotores | M | En miles de ARS | MEyML |
| 1143 | Préstamos prendarios a personas humanas para compra de maquinarias | M | En miles de ARS | MEyML |
| 1144 | Préstamos prendarios a personas humanas no destinados a la compra de automotores o maquinarias | M | En miles de ARS | MEyML |
| 1145 | Préstamos hipotecarios a personas humanas para construcción de viviendas | M | En miles de ARS | ML |
| 1146 | Préstamos hipotecarios a personas humanas para refacción de vivienda | M | En miles de ARS | ML |
| 1147 | Préstamos hipotecarios a personas humanas para compra de nuevas viviendas | M | En miles de ARS | ML |
| 1148 | Préstamos hipotecarios a personas humanas para compra de viviendas usadas | M | En miles de ARS | ML |
| 1149 | Préstamos hipotecarios a personas humanas para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | ML |
| 1150 | Préstamos prendarios a personas humanas a para compra de automotores a | M | En miles de ARS | ML |
| 1151 | Préstamos prendarios a personas humanas a para compra de maquinarias a | M | En miles de ARS | ML |
| 1152 | Préstamos prendarios a personas humanas a no destinados a la compra de automotores o maquinarias a | M | En miles de ARS | ML |
| 1153 | Préstamos hipotecarios a personas humanas para construcción de viviendas a | M | En miles de ARS | ME |
| 1154 | Préstamos hipotecarios a personas humanas para refacción de vivienda a | M | En miles de ARS | ME |
| 1155 | Préstamos hipotecarios a personas humanas para compra de nuevas viviendas a | M | En miles de ARS | ME |
| 1156 | Préstamos hipotecarios a personas humanas para compra de viviendas usadas a | M | En miles de ARS | ME |
| 1157 | Préstamos hipotecarios a personas humanas a para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | ME |
| 1158 | Préstamos prendarios a personas humanas a para compra de automotores a | M | En miles de ARS | ME |
| 1159 | Préstamos prendarios a personas humanas a para compra de maquinarias a | M | En miles de ARS | ME |
| 1160 | Préstamos prendarios a personas humanas no destinados a la compra de automotores o maquinarias | M | En miles de ARS | ME |
| 1161 | Préstamos hipotecarios a personas jurídicas para construcción de viviendas | M | En miles de ARS | MEyML |
| 1162 | Préstamos hipotecarios a personas jurídicas para refacción de vivienda | M | En miles de ARS | MEyML |
| 1163 | Préstamos hipotecarios a personas jurídicas para compra de nuevas viviendas | M | En miles de ARS | MEyML |
| 1164 | Préstamos hipotecarios a personas jurídicas para compra de viviendas usadas | M | En miles de ARS | MEyML |
| 1165 | Préstamos hipotecarios a personas jurídicas para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | MEyML |
| 1166 | Préstamos prendarios a personas jurídicas para compra de automotores | M | En miles de ARS | MEyML |
| 1167 | Préstamos prendarios a personas jurídicas para compra de maquinarias | M | En miles de ARS | MEyML |
| 1168 | Préstamos prendarios a personas jurídicas no destinados a la compra de automotores o maquinarias | M | En miles de ARS | MEyML |
| 1169 | Préstamos hipotecarios a personas jurídicas para construcción de viviendas | M | En miles de ARS | ML |
| 1170 | Préstamos hipotecarios a personas jurídicas para refacción de vivienda | M | En miles de ARS | ML |
| 1171 | Préstamos hipotecarios a personas jurídicas para compra de nuevas viviendas | M | En miles de ARS | ML |
| 1172 | Préstamos hipotecarios a personas jurídicas para compra de viviendas usadas | M | En miles de ARS | ML |
| 1173 | Préstamos hipotecarios a personas jurídicas para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | ML |
| 1174 | Préstamos prendarios a personas jurídicas para compra de automotores | M | En miles de ARS | ML |
| 1175 | Préstamos prendarios a personas jurídicas para compra de maquinarias | M | En miles de ARS | ML |
| 1176 | Préstamos prendarios a personas jurídicas no destinados a la compra de automotores o maquinarias | M | En miles de ARS | ML |
| 1177 | Préstamos hipotecarios a personas jurídicas para construcción de viviendas | M | En miles de ARS | ME |
| 1178 | Préstamos hipotecarios a personas jurídicas para refacción de vivienda | M | En miles de ARS | ME |
| 1179 | Préstamos hipotecarios a personas jurídicas para compra de nuevas viviendas | M | En miles de ARS | ME |
| 1180 | Préstamos hipotecarios a personas jurídicas para compra de viviendas usadas | M | En miles de ARS | ME |
| 1181 | Préstamos hipotecarios a personas jurídicas para otras operaciones distinas a construcción, refacción y compra de vivienda | M | En miles de ARS | ME |
| 1182 | Préstamos prendarios a personas jurídicas para compra de automotores | M | En miles de ARS | ME |
| 1183 | Préstamos prendarios a personas jurídicas para compra de maquinarias | M | En miles de ARS | ME |
| 1184 | Préstamos prendarios a personas jurídicas no destinados a la compra de automotores o maquinarias | M | En miles de ARS | ME |
| 1185 | Total de préstamos al sector privado no financiero | M | En miles de ARS | ME |
| 1186 | Total de préstamos a personas humanas | M | En miles de ARS | ME |

## Préstamos por tipo de titular (120 variables)

Préstamos al sector público nacional, al sector privado y agregados por moneda (incluye total nacional).

| ID | Descripción | Per. | Unidad | Moneda |
|---|---|---|---|---|
| 199 | Préstamos a los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ML |
| 200 | Préstamos a la administración central | M | En miles de ARS | ML |
| 201 | Préstamos a entidades descentralizadas | M | En miles de ARS | ML |
| 204 | Préstamos a las corporaciones integubernamentales | M | En miles de ARS | ML |
| 205 | Préstamos a empresas y otros entes públicos nacionales | M | En miles de ARS | ML |
| 208 | Préstamos a empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ML |
| 219 | Préstamos a los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ME |
| 220 | Préstamos a la administración central | M | En miles de ARS | ME |
| 221 | Préstamos a entidades descentralizadas | M | En miles de ARS | ME |
| 224 | Préstamos a las corporaciones integubernamentales | M | En miles de ARS | ME |
| 225 | Préstamos a empresas y otros entes públicos nacionales | M | En miles de ARS | ME |
| 228 | Préstamos a empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ME |
| 320 | Total de préstamos a la Ciudad Autónoma de Buenos Aires | M | En miles de ARS | ML |
| 463 | Total de préstamos a la Ciudad Autónoma de Buenos Aires | M | En miles de ARS | ME |
| 511 | Total de préstamos a municipios de la PBA | M | En miles de ARS | ML |
| 513 | Total de préstamos a municipios de GBA | M | En miles de ARS | ML |
| 515 | Total de préstamos a municipios de la PBA no incluidos en el GBA | M | En miles de ARS | ML |
| 636 | Total de préstamos a municipios de la PBA | M | En miles de ARS | ME |
| 638 | Total de préstamos a municipios de GBA | M | En miles de ARS | ME |
| 640 | Total de préstamos a municipios de la PBA no incluidos en el GBA | M | En miles de ARS | ME |
| 642 | Total de préstamos a municipios de Catamarca | M | En miles de ARS | ME |
| 882 | Total de préstamos al sector privado no financiero | M | En miles de ARS | MEyML |
| 883 | Total de préstamos a personas humanas | M | En miles de ARS | MEyML |
| 884 | Total de préstamos a personas jurídicas | M | En miles de ARS | MEyML |
| 885 | Total de préstamos a las prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 886 | Total de préstamos a las compañías de seguros | M | En miles de ARS | MEyML |
| 887 | Total de préstamos a los fondos comunes de inversión | M | En miles de ARS | MEyML |
| 888 | Total de préstamos a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | MEyML |
| 889 | Total de préstamos a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | MEyML |
| 890 | Total de préstamos a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 891 | Total de préstamos a pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 892 | Total de préstamos a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 893 | Total de préstamos al sector privado no financiero | M | En miles de ARS | ML |
| 894 | Total de préstamos a personas humanas | M | En miles de ARS | ML |
| 895 | Total de préstamos a personas jurídicas | M | En miles de ARS | ML |
| 896 | Total de préstamos a las prestadoras de servicios financieros | M | En miles de ARS | ML |
| 897 | Total de préstamos a las compañías de seguros | M | En miles de ARS | ML |
| 898 | Total de préstamos a los fondos comunes de inversión | M | En miles de ARS | ML |
| 899 | Total de préstamos a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ML |
| 900 | Total de préstamos a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ML |
| 901 | Total de préstamos a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ML |
| 902 | Total de préstamos a pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 903 | Total de préstamos a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 904 | Total de préstamos al sector privado no financiero | M | En miles de ARS | ME |
| 905 | Total de préstamos a personas humanas | M | En miles de ARS | ME |
| 906 | Total de préstamos a personas jurídicas | M | En miles de ARS | ME |
| 907 | Total de préstamos a las prestadoras de servicios financieros | M | En miles de ARS | ME |
| 908 | Total de préstamos a las compañías de seguros | M | En miles de ARS | ME |
| 909 | Total de préstamos a los fondos comunes de inversión | M | En miles de ARS | ME |
| 910 | Total de préstamos a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ME |
| 911 | Total de préstamos a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ME |
| 912 | Total de préstamos a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ME |
| 913 | Total de préstamos a pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 914 | Total de préstamos a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 915 | Total de préstamos hipotecaRíos al sector privado | M | En miles de ARS | MEyML |
| 916 | Préstamos hipotecarios a personas humanas | M | En miles de ARS | MEyML |
| 917 | Préstamos hipotecarios a personas jurídicas | M | En miles de ARS | MEyML |
| 918 | Préstamos hipotecarios a las prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 919 | Préstamos hipotecarios a las compañías de seguros | M | En miles de ARS | MEyML |
| 920 | Préstamos hipotecarios a los fondos comunes de inversión | M | En miles de ARS | MEyML |
| 921 | Préstamos hipotecarios a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | MEyML |
| 922 | Préstamos hipotecarios a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | MEyML |
| 923 | Préstamos hipotecarios a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 924 | Préstamos hipotecarios a pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 925 | Préstamos hipotecarios a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 926 | Total de préstamos hipotecarios al sector privado | M | En miles de ARS | ML |
| 927 | Préstamos hipotecarios a personas humanas | M | En miles de ARS | ML |
| 928 | Préstamos hipotecarios a personas jurídicas | M | En miles de ARS | ML |
| 929 | Préstamos hipotecarios a las prestadoras de servicios financieros | M | En miles de ARS | ML |
| 930 | Préstamos hipotecarios a las compañías de seguros | M | En miles de ARS | ML |
| 931 | Préstamos hipotecarios a los fondos comunes de inversión | M | En miles de ARS | ML |
| 932 | Préstamos hipotecarios a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ML |
| 933 | Préstamos hipotecarios a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ML |
| 934 | Préstamos hipotecarios a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ML |
| 935 | Préstamos hipotecarios a pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 936 | Préstamos hipotecarios a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 937 | Total de préstamos hipotecarios al sector privado | M | En miles de ARS | ME |
| 938 | Préstamos hipotecarios a personas humanas | M | En miles de ARS | ME |
| 939 | Préstamos hipotecarios a personas jurídicas | M | En miles de ARS | ME |
| 940 | Préstamos hipotecarios a las prestadoras de servicios financieros | M | En miles de ARS | ME |
| 941 | Préstamos hipotecarios a las compañías de seguros | M | En miles de ARS | ME |
| 942 | Préstamos hipotecarios a los fondos comunes de inversión | M | En miles de ARS | ME |
| 943 | Préstamos hipotecarios a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ME |
| 944 | Préstamos hipotecarios a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ME |
| 945 | Préstamos hipotecarios a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ME |
| 946 | Préstamos hipotecarios a pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 947 | Préstamos hipotecarios a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 948 | Total de préstamos prendarios al sector privado | M | En miles de ARS | MEyML |
| 949 | Préstamos prendarios a personas humanas | M | En miles de ARS | MEyML |
| 950 | Préstamos prendarios a personas jurídicas | M | En miles de ARS | MEyML |
| 951 | Préstamos prendarios a las prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 952 | Préstamos prendarios a las compañías de seguros | M | En miles de ARS | MEyML |
| 953 | Préstamos prendarios a los fondos comunes de inversión | M | En miles de ARS | MEyML |
| 954 | Préstamos prendarios a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | MEyML |
| 955 | Préstamos prendarios a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | MEyML |
| 956 | Préstamos prendarios a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 957 | Préstamos prendarios a pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 958 | Préstamos prendarios a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 959 | Total de préstamos prendarios al sector privado | M | En miles de ARS | ML |
| 960 | Préstamos prendarios a personas humanas | M | En miles de ARS | ML |
| 961 | Préstamos prendarios a personas jurídicas | M | En miles de ARS | ML |
| 962 | Préstamos prendarios a las prestadoras de servicios financieros | M | En miles de ARS | ML |
| 963 | Préstamos prendarios a las compañías de seguros | M | En miles de ARS | ML |
| 964 | Préstamos prendarios a los fondos comunes de inversión | M | En miles de ARS | ML |
| 965 | Préstamos prendarios a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ML |
| 966 | Préstamos prendarios a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ML |
| 967 | Préstamos prendarios a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ML |
| 968 | Préstamos prendarios a pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 969 | Préstamos prendarios a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 970 | Total de préstamos prendarios al sector privado | M | En miles de ARS | ME |
| 971 | Préstamos prendarios a personas humanas | M | En miles de ARS | ME |
| 972 | Préstamos prendarios a personas jurídicas | M | En miles de ARS | ME |
| 973 | Préstamos prendarios a las prestadoras de servicios financieros | M | En miles de ARS | ME |
| 974 | Préstamos prendarios a las compañías de seguros | M | En miles de ARS | ME |
| 975 | Préstamos prendarios a los fondos comunes de inversión | M | En miles de ARS | ME |
| 976 | Préstamos prendarios a las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ME |
| 977 | Préstamos prendarios a las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ME |
| 978 | Préstamos prendarios a empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ME |
| 979 | Préstamos prendarios a pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 980 | Préstamos prendarios a las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ME |

## Depósitos por tipo de titular (212 variables)

Depósitos del sector público nacional, privado y agregados por moneda, cuenta y plazo (incluye total nacional).

| ID | Descripción | Per. | Unidad | Moneda |
|---|---|---|---|---|
| 209 | Depósitos de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ML |
| 210 | Depósitos de la administración central | M | En miles de ARS | ML |
| 211 | Depósitos de las entidades descentralizadas | M | En miles de ARS | ML |
| 214 | Depósitos de corporaciones integubernamentales | M | En miles de ARS | ML |
| 215 | Depósitos de empresas y otros entes públicos nacionales | M | En miles de ARS | ML |
| 218 | Depósitos de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ML |
| 229 | Depósitos de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ME |
| 230 | Depósitos de la administración central | M | En miles de ARS | ME |
| 231 | Depósitos de las entidades descentralizadas | M | En miles de ARS | ME |
| 234 | Depósitos de corporaciones integubernamentales | M | En miles de ARS | ME |
| 235 | Depósitos de empresas y otros entes públicos nacionales | M | En miles de ARS | ME |
| 238 | Depósitos de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ME |
| 239 | Depósitos en cuentas corrientes de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ML |
| 240 | Depósitos en cuentas corrientes de la administración central | M | En miles de ARS | ML |
| 241 | Depósitos en cuentas corrientes de las entidades descentralizadas | M | En miles de ARS | ML |
| 244 | Depósitos en cuentas corrientes de los gobiernos de corporaciones integubernamentales | M | En miles de ARS | ML |
| 245 | Depósitos en cuentas corrientes de empresas y otros entes públicos nacionales | M | En miles de ARS | ML |
| 248 | Depósitos en cuentas corrientes de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ML |
| 249 | Depósitos en cajas de ahorro de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ML |
| 250 | Depósitos en caja de ahorros de la administración central | M | En miles de ARS | ML |
| 251 | Depósitos en caja de ahorros de las entidades descentralizadas | M | En miles de ARS | ML |
| 254 | Depósitos en caja de ahorros de los gobiernos de corporaciones integubernamentales | M | En miles de ARS | ML |
| 255 | Depósitos en caja de ahorros de empresas y otros entes públicos nacionales | M | En miles de ARS | ML |
| 258 | Depósitos en caja de ahorros de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ML |
| 259 | Depósitos a plazo fijo de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ML |
| 260 | Depósitos en plazo fijo de la administración central | M | En miles de ARS | ML |
| 261 | Depósitos en plazo fijo de las entidades descentralizadas | M | En miles de ARS | ML |
| 264 | Depósitos en plazo fijo de los gobiernos de corporaciones integubernamentales | M | En miles de ARS | ML |
| 265 | Depósitos en plazo fijo de empresas y otros entes públicos nacionales | M | En miles de ARS | ML |
| 268 | Depósitos en plazo fijo de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ML |
| 269 | Otros depósitos de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ML |
| 270 | Otros depósitos de la administración central | M | En miles de ARS | ML |
| 271 | Otros depósitos de las entidades descentralizadas | M | En miles de ARS | ML |
| 274 | Otros depósitos de corporaciones integubernamentales | M | En miles de ARS | ML |
| 275 | Otros depósitos de empresas y otros entes públicos nacionales | M | En miles de ARS | ML |
| 278 | Otros depósitos de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ML |
| 279 | Depósitos en cuentas corrientes de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ME |
| 280 | Depósitos en cuentas corrientes de la administración central | M | En miles de ARS | ME |
| 281 | Depósitos en cuentas corrientes de las entidades descentralizadas | M | En miles de ARS | ME |
| 284 | Depósitos en cuentas corrientes de los gobiernos de corporaciones integubernamentales | M | En miles de ARS | ME |
| 285 | Depósitos en cuentas corrientes de empresas y otros entes públicos nacionales | M | En miles de ARS | ME |
| 288 | Depósitos en cuentas corrientes de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ME |
| 289 | Depósitos en cajas de ahorro de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ME |
| 290 | Depósitos en caja de ahorros de la administración central | M | En miles de ARS | ME |
| 291 | Depósitos en caja de ahorros de las entidades descentralizadas | M | En miles de ARS | ME |
| 294 | Depósitos en caja de ahorros de los gobiernos de corporaciones integubernamentales | M | En miles de ARS | ME |
| 295 | Depósitos en caja de ahorros de empresas y otros entes públicos nacionales | M | En miles de ARS | ME |
| 298 | Depósitos en caja de ahorros de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ME |
| 299 | Depósitos a plazo fijo de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ME |
| 300 | Depósitos en plazo fijo de la administración central | M | En miles de ARS | ME |
| 301 | Depósitos en plazo fijo de las entidades descentralizadas | M | En miles de ARS | ME |
| 304 | Depósitos en plazo fijo de los gobiernos de corporaciones integubernamentales | M | En miles de ARS | ME |
| 305 | Depósitos en plazo fijo de empresas y otros entes públicos nacionales | M | En miles de ARS | ME |
| 308 | Depósitos en plazo fijo de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ME |
| 309 | Otros depósitos de los gobiernos nacional, provinciales, municipales y corporaciones intergubernamentales | M | En miles de ARS | ME |
| 310 | Otros depósitos de la administración central | M | En miles de ARS | ME |
| 311 | Otros depósitos de las entidades descentralizadas | M | En miles de ARS | ME |
| 314 | Otros depósitos de corporaciones integubernamentales | M | En miles de ARS | ME |
| 315 | Otros depósitos de empresas y otros entes públicos nacionales | M | En miles de ARS | ME |
| 318 | Otros depósitos de empresas y otros entes públicos intergubernamentales | M | En miles de ARS | ME |
| 319 | Utilización de fondos unificados de la Ciudad Autónoma de Buenos Aires | M | En miles de ARS | ML |
| 321 | Total de depósitos de la Ciudad Autónoma de Buenos Aires | M | En miles de ARS | ML |
| 391 | Depósitos en cuentas corrientes de la Ciudad Autónoma de Buenos Aires | M | En miles de ARS | ML |
| 392 | Depósitos en caja de ahorros de la Ciudad Autónoma de Buenos Aires | M | En miles de ARS | ML |
| 393 | Depósitos a plazo fijo de la Ciudad Autónoma de Buenos Aires | M | En miles de ARS | ML |
| 464 | Total de depósitos de la Ciudad Autónoma de Buenos Aires | M | En miles de ARS | ME |
| 512 | Total de depósitos de municipios de la PBA | M | En miles de ARS | ML |
| 514 | Total de depósitos de municipios de GBA | M | En miles de ARS | ML |
| 516 | Total de depósitos municipios de la PBA no incluidos en GBA | M | En miles de ARS | ML |
| 561 | Depósitos en cuentas corrientes de municipios de la PBA | M | En miles de ARS | ML |
| 562 | Depósitos en caja de ahorros de municipios de la PBA | M | En miles de ARS | ML |
| 563 | Depósitos en plazo fijo de municipios de la PBA | M | En miles de ARS | ML |
| 564 | Depósitos en cuentas corrientes de municipios del GBA | M | En miles de ARS | ML |
| 565 | Depósitos en caja de ahorros de municipios del GBA | M | En miles de ARS | ML |
| 566 | Depósitos en plazo fijo de municipios del GBA | M | En miles de ARS | ML |
| 567 | Depósitos en cuentas corrientes de municipios de la PBA no incluidos en GBA | M | En miles de ARS | ML |
| 568 | Depósitos en caja de ahorros de municipios no incluidos en GBA | M | En miles de ARS | ML |
| 569 | Depósitos a plazo fijo de municipios no incluidos en el GBA | M | En miles de ARS | ML |
| 639 | Total de depósitos de municipios de GBA | M | En miles de ARS | ME |
| 641 | Total de depósitos de municipios de la PBA no incluidos en GBA | M | En miles de ARS | ME |
| 981 | Total de depósitos del sector privado no financiero | M | En miles de ARS | MEyML |
| 982 | Total de depósitos de personas humanas | M | En miles de ARS | MEyML |
| 983 | Total de depósitos de personas jurídicas | M | En miles de ARS | MEyML |
| 984 | Total de depósitos de las prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 985 | Total de depósitos de las compañías de seguros | M | En miles de ARS | MEyML |
| 986 | Total de depósitos de los fondos comunes de inversión | M | En miles de ARS | MEyML |
| 987 | Total de depósitos de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | MEyML |
| 988 | Total de depósitos de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | MEyML |
| 989 | Total de depósitos de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 990 | Total de depósitos de pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 991 | Total de depósitos de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 992 | Total de depósitos del sector privado no financiero | M | En miles de ARS | ML |
| 993 | Total de depósitos de personas humanas | M | En miles de ARS | ML |
| 994 | Total de depósitos de personas jurídicas | M | En miles de ARS | ML |
| 995 | Total de depósitos de las prestadoras de servicios financieros | M | En miles de ARS | ML |
| 996 | Total de depósitos de las compañías de seguros | M | En miles de ARS | ML |
| 997 | Total de depósitos de los fondos comunes de inversión | M | En miles de ARS | ML |
| 998 | Total de depósitos de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ML |
| 999 | Total de depósitos de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ML |
| 1000 | Total de depósitos de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ML |
| 1001 | Total de depósitos de pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 1002 | Total de depósitos de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 1003 | Total de depósitos del sector privado no financiero | M | En miles de ARS | ME |
| 1004 | Total de depósitos de personas humanas | M | En miles de ARS | ME |
| 1005 | Total de depósitos de personas jurídicas | M | En miles de ARS | ME |
| 1006 | Total de depósitos de las prestadoras de servicios financieros | M | En miles de ARS | ME |
| 1007 | Total de depósitos de las compañías de seguros | M | En miles de ARS | ME |
| 1008 | Total de depósitos de los fondos comunes de inversión | M | En miles de ARS | ME |
| 1009 | Total de depósitos de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ME |
| 1010 | Total de depósitos de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ME |
| 1011 | Total de depósitos de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ME |
| 1012 | Total de depósitos de pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 1013 | Total de depósitos de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 1014 | Total de depósitos en cuentas corrientes del sector privado | M | En miles de ARS | MEyML |
| 1015 | Depósitos en cuentas corrientes de personas humanas | M | En miles de ARS | MEyML |
| 1016 | Depósitos en cuentas corrientes de personas jurídicas | M | En miles de ARS | MEyML |
| 1017 | Depósitos en cuentas corrientes de las prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 1018 | Depósitos en cuentas corrientes de las compañías de seguros | M | En miles de ARS | MEyML |
| 1019 | Depósitos en cuentas corrientes de los fondos comunes de inversión | M | En miles de ARS | MEyML |
| 1020 | Depósitos en cuentas corrientes de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | MEyML |
| 1021 | Depósitos en cuentas corrientes de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | MEyML |
| 1022 | Depósitos en cuentas corrientes de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 1023 | Depósitos en cuentas corrientes de pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 1024 | Depósitos en cuentas corrientes de las empresas no constituidas como pequeños y medianos emprendimien | M | En miles de ARS | MEyML |
| 1025 | Total de depósitos en cuentas corrientes del sector privado | M | En miles de ARS | ML |
| 1026 | Depósitos en cuentas corrientes de personas humanas | M | En miles de ARS | ML |
| 1027 | Depósitos en cuentas corrientes de personas jurídicas | M | En miles de ARS | ML |
| 1028 | Depósitos en cuentas corrientes de las prestadoras de servicios financieros | M | En miles de ARS | ML |
| 1029 | Depósitos en cuentas corrientes de las compañías de seguros | M | En miles de ARS | ML |
| 1030 | Depósitos en cuentas corrientes de los fondos comunes de inversión | M | En miles de ARS | ML |
| 1031 | Depósitos en cuentas corrientes de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ML |
| 1032 | Depósitos en cuentas corrientes de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ML |
| 1033 | Depósitos en cuentas corrientes de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ML |
| 1034 | Depósitos en cuentas corrientes de pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 1035 | Depósitos en cuentas corrientes de las empresas no constituidas como pequeños y medianos emprendimien | M | En miles de ARS | ML |
| 1036 | Total de depósitos en cuentas corrientes del sector privado | M | En miles de ARS | ME |
| 1037 | Depósitos en cuentas corrientes de personas humanas | M | En miles de ARS | ME |
| 1038 | Depósitos en cuentas corrientes de personas jurídicas | M | En miles de ARS | ME |
| 1039 | Depósitos en cuentas corrientes de las prestadoras de servicios financieros | M | En miles de ARS | ME |
| 1040 | Depósitos en cuentas corrientes de las compañías de seguros | M | En miles de ARS | ME |
| 1041 | Depósitos en cuentas corrientes de los fondos comunes de inversión | M | En miles de ARS | ME |
| 1042 | Depósitos en cuentas corrientes de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ME |
| 1043 | Depósitos en cuentas corrientes de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ME |
| 1044 | Depósitos en cuentas corrientes de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ME |
| 1045 | Depósitos en cuentas corrientes de pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 1046 | Depósitos en cuentas corrientes de las empresas no constituidas como pequeños y medianos emprendimien | M | En miles de ARS | ME |
| 1047 | Total de depósitos en caja de ahorros del sector privado | M | En miles de ARS | MEyML |
| 1048 | Depósitos en caja de ahorros de personas humanas | M | En miles de ARS | MEyML |
| 1049 | Depósitos en caja de ahorros de personas jurídicas | M | En miles de ARS | MEyML |
| 1050 | Depósitos en caja de ahorros de las prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 1051 | Depósitos en caja de ahorros de las compañías de seguros | M | En miles de ARS | MEyML |
| 1052 | Depósitos en caja de ahorros de los fondos comunes de inversión | M | En miles de ARS | MEyML |
| 1053 | Depósitos en caja de ahorros de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | MEyML |
| 1054 | Depósitos en caja de ahorros de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | MEyML |
| 1055 | Depósitos en caja de ahorros de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 1056 | Depósitos en caja de ahorros de pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 1057 | Depósitos en caja de ahorros de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 1058 | Total de depósitos en caja de ahorros del sector privado | M | En miles de ARS | ML |
| 1059 | Depósitos en caja de ahorros de personas humanas | M | En miles de ARS | ML |
| 1060 | Depósitos en caja de ahorros de personas jurídicas | M | En miles de ARS | ML |
| 1061 | Depósitos en caja de ahorros de las prestadoras de servicios financieros | M | En miles de ARS | ML |
| 1062 | Depósitos en caja de ahorros de las compañías de seguros | M | En miles de ARS | ML |
| 1063 | Depósitos en caja de ahorros de los fondos comunes de inversión | M | En miles de ARS | ML |
| 1064 | Depósitos en caja de ahorros de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ML |
| 1065 | Depósitos en caja de ahorros de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ML |
| 1066 | Depósitos en caja de ahorros de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ML |
| 1067 | Depósitos en caja de ahorros de pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 1068 | Depósitos en caja de ahorros de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 1069 | Total de depósitos en caja de ahorros del sector privado | M | En miles de ARS | ME |
| 1070 | Depósitos en caja de ahorros de personas humanas | M | En miles de ARS | ME |
| 1071 | Depósitos en caja de ahorros de personas jurídicas | M | En miles de ARS | ME |
| 1072 | Depósitos en caja de ahorros de las prestadoras de servicios financieros | M | En miles de ARS | ME |
| 1073 | Depósitos en caja de ahorros de las compañías de seguros | M | En miles de ARS | ME |
| 1074 | Depósitos en caja de ahorros de los fondos comunes de inversión | M | En miles de ARS | ME |
| 1075 | Depósitos en caja de ahorros de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ME |
| 1076 | Depósitos en caja de ahorros de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ME |
| 1077 | Depósitos en caja de ahorros de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ME |
| 1078 | Depósitos en caja de ahorros de pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 1079 | Depósitos en caja de ahorros de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 1080 | Total de depósitos a plazo fijo del sector privado | M | En miles de ARS | MEyML |
| 1081 | Depósitos a plazo fijo de personas humanas | M | En miles de ARS | MEyML |
| 1082 | Depósitos a plazo fijo de personas jurídicas | M | En miles de ARS | MEyML |
| 1083 | Depósitos a plazo fijo de las prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 1084 | Depósitos a plazo fijo de las compañías de seguros | M | En miles de ARS | MEyML |
| 1085 | Depósitos a plazo fijo de los fondos comunes de inversión | M | En miles de ARS | MEyML |
| 1086 | Depósitos a plazo fijo de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | MEyML |
| 1087 | Depósitos a plazo fijo de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | MEyML |
| 1088 | Depósitos a plazo fijo de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | MEyML |
| 1089 | Depósitos a plazo fijo de pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 1090 | Depósitos a plazo fijo de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | MEyML |
| 1091 | Total de depósitos a plazo fijo del sector privado | M | En miles de ARS | ML |
| 1092 | Depósitos a plazo fijo de personas humanas | M | En miles de ARS | ML |
| 1093 | Depósitos a plazo fijo de personas jurídicas | M | En miles de ARS | ML |
| 1094 | Depósitos a plazo fijo de las prestadoras de servicios financieros | M | En miles de ARS | ML |
| 1095 | Depósitos a plazo fijo de las compañías de seguros | M | En miles de ARS | ML |
| 1096 | Depósitos a plazo fijo de los fondos comunes de inversión | M | En miles de ARS | ML |
| 1097 | Depósitos a plazo fijo de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ML |
| 1098 | Depósitos a plazo fijo de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ML |
| 1099 | Depósitos a plazo fijo de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ML |
| 1100 | Depósitos a plazo fijo de pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 1101 | Depósitos a plazo fijo de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ML |
| 1102 | Total de depósitos a plazo fijo del sector privado | M | En miles de ARS | ME |
| 1103 | Depósitos a plazo fijo de personas humanas | M | En miles de ARS | ME |
| 1104 | Depósitos a plazo fijo de personas jurídicas | M | En miles de ARS | ME |
| 1105 | Depósitos a plazo fijo de las prestadoras de servicios financieros | M | En miles de ARS | ME |
| 1106 | Depósitos a plazo fijo de las compañías de seguros | M | En miles de ARS | ME |
| 1107 | Depósitos a plazo fijo de los fondos comunes de inversión | M | En miles de ARS | ME |
| 1108 | Depósitos a plazo fijo de las administradoras de fondos de jubilaciones y pensiones | M | En miles de ARS | ME |
| 1109 | Depósitos a plazo fijo de las sociedades autorizadas para actuar como fiduciario financiero | M | En miles de ARS | ME |
| 1110 | Depósitos a plazo fijo de empresas que no son prestadoras de servicios financieros | M | En miles de ARS | ME |
| 1111 | Depósitos a plazo fijo de pequeños y medianos emprendimientos | M | En miles de ARS | ME |
| 1112 | Depósitos a plazo fijo de las empresas no constituidas como pequeños y medianos emprendimientos | M | En miles de ARS | ME |
