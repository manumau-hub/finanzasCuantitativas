# Clase 1 — Extracto del PPT (Derivados Financieros 1.pptx)

Texto extraído slide por slide para usar como base del notebook.

---

## Slide 1
Manu Maurette
Clase 1: Introducciones varias, opciones
Derivados Financieros 1 — 2022

---

## Slide 2 — Quién soy

## Slide 3 — Resultados Encuesta
¿Qué otras palabras/frases les vienen a la mente cuando piensan en la palabra QUANt?

---

## Slide 4 — Qué intentaremos cubrir (Teoría)
- Introducción a los derivados y motivación del problema
- Foco en Opciones, características propiedades
- Análisis y exploración de mercados de opciones
- El problema de valuación — modelos de precios: Binomial, Black Scholes, Montecarlo, Diferencias Finitas
- Sensibilidades de derivados para riesgo

## Slide 5 — Qué intentaremos cubrir (Python)
- Algo de Web Scraping
- Algunas APIs para conectarse al mercado (restringido a Opciones)
- "Limpieza" de dataframes
- Implementación de los algoritmos de precio
- Volatilidad Implícita, griegas
- QuantLib

---

## Slides 6–9 — Antes de empezar: Principios

**6.** Money Market: mercados de activos con plazo corto (<18 meses), bajo riesgo, elevada liquidez. Ej: bono corto soberano. Suelen denominarse libres de riesgo.

**8.** Arbitraje: There is no free lunch. Práctica de tomar ventaja de diferencia de precio entre mercados. Hipótesis: No existen posibilidades de arbitraje. ¿Qué ejemplos de arbitraje conocen?

**9.** Ventanas pequeñas. Existen oportunidades de arbitraje si existe portafolio que cumpla: empiezo gratis, termino positivo.

---

## Slide 10 — Números importantes

**En todo momento:**
- **Precio**: número que se observa en mercado, se pagaría/recibiría para negociar
- **Valor Mark-to-Market**: estimación de lo que se podría pagar/recibir — se necesitan Modelos
- **Prima (Premium)**: lo que realmente se paga/recibe

**A vencimiento:**
- **Payoff**: valor a tiempo final del contrato (determinístico)
- **Ganancia / PnL**: ganancia o pérdida total, incluyendo prima y valor del derivado o payoff realizado

---

## Slides 11–13 — Derivados

## Slides 14–21 — Derivados Lineales: Forward
- Ejemplo de contrato forward
- Flujos de pago
- Payoff contrato forward
- Valuación
- Precio forward que elimina arbitraje

## Slide 22 — Mercados de Futuros
Commodities, FX, Índices, Crypto. Links: MATBAROFEX, BYMA, Barchart, Binance.

## Slide 23 — Swaps
Contratos OTC que intercambian dos series de flujos. Flujos fijos, flotantes, varias monedas. Ver más en siguiente módulo.

---

## Slide 24 — Derivados No Lineales
Opciones. Valor evoluciona de forma no lineal con subyacentes. OTC o exchanges. Combinación → estrategias. Ej: opciones, convertibles, warrants, callable bonds.

## Slide 25 — Otros Derivados
- **Estructurados**: bono + derivado, OTC
- **Híbridos**: combinación de exposiciones, ej. bonos convertibles

---

## Slide 26 — Opciones (objeto de estudio)

**Definición:** Contrato que da al dueño el **derecho, pero no la obligación**, de negociar un activo (subyacente) por un precio (strike) en una fecha futura (expiración). Call = derecho a comprar; Put = derecho a vender.

Jerga: Underlying, Strike Price, Expiry/Maturity.

## Slide 27 — Opciones Call — Parangón
Depósito para compra de vivienda. 400K USD, depósito 20K. Si compro: dueño conserva depósito + obligación de vender. Si no compro: dueño conserva depósito.

## Slide 28 — Opciones Put — Parangón
Seguro de vivienda. Prima. Si hay daños: aseguradora paga reparaciones. Si no: aseguradora se queda con prima.

---

## Slide 29 — ¿Para qué se usan?
- Comprador: riesgo limitado (derecho, no obligación). Vendedor: riesgo mayor.
- Cobertura, beneficio ante movimientos, apalancamiento, estrategias.

## Slides 30–31 — Mercados
Opciones sobre: Equity (BYMA, Yahoo), FX, Índices, Commodities (ROFEX).

## Slides 32–33 — Ejercicio
- **Europeo**: solo al vencimiento
- **Americano**: en todo momento
- Bermuda: intermedio
- Equity/Commodities suelen ser americanas

---

## Slides 34–36 — Posiciones
- **Long**: compro la opción
- **Short**: vendo/escribo la opción
- Gráficos ganancia escritor call (K=100, prima=5) y put (K=70, prima=7)

## Slides 37–39 — Payoffs (4 posiciones)
Long call, Long put, Short call, Short put. Gráficos.

## Slide 40 — PnL
Gráficos PnL (Payoff − Prima) para las 4 posiciones.

---

## Slide 41 — Valor Intrínseco (VI)
VI = diferencia entre precio subyacente y strike. Siempre ≥ 0. Al vencimiento, VI = payoff. Valor temporal = Precio − VI.

## Slide 42 — Moneyness
ITM, ATM, OTM.

## Slide 43 — Venta cubierta vs descubierta (naked)
Venta cubierta: típica cobertura. Naked: riesgo mayor. Muchos brokers no permiten. Lotes de 100.

## Slides 44–45 — Margen (CBOE)
Fórmulas para call y put descubiertos. Ejemplo: call $5, K=$40, S=$38 → margen = max(1060, 880).

---

## Slides 46–49 — Caso 1: Especulación (AAPL)
Inversión 1: comprar acción $200. Inversión 2: call K=$210, prima $12. Escenarios: S<210 (pierdo $12), S entre 210–222 (reduzco pérdida), S>222 (ganancia). Break-even = $222.

## Slides 50–51 — Caso 2: Cobertura — Protective Put
Acción $150 + put. Protección ante caída, cediendo ganancia potencial.

## Slides 52–53 — Caso 3: Comprar volatilidad — Straddle
Call + Put mismo strike (ATM). Especula con movimiento sin dirección.

---

## Slide 54 — Preguntas Hull
Ejercicios teórico-prácticos.

## Slide 55 — Python: Paneles
BYMA (web scraping IOL), API homebroker, NYSE (Yahoo). Obtener paneles limpios para sensibilidades.
