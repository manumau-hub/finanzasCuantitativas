# Simulaciones — Pipeline de Johnson SU + t-Copula

## Pipeline

El pipeline de simulación sigue el material del curso (slides 70-76, TP-Libs
ej5-ej6-ej9):

```
retornos históricos → fit marginal (Johnson SU) → transformar a U(0,1) via CDF
→ fit t-copula (matriz de correlación P, df) → samplear de t-copula
→ back-transform via PPF (Johnson SU) → agregar drift → wealth paths
```

### Paso a paso

1. **Fit marginal**: para cada activo, ajustar una distribución Johnson SU a
   sus retornos históricos. Johnson SU captura asimetría y colas pesadas
   mejor que cualquier distribución paramétrica estándar.
2. **Transformación a U(0,1)**: aplicar la CDF de Johnson SU a los retornos.
   El resultado son valores uniformes [0,1] que preservan la dependencia
   ordinal entre activos.
3. **Fit cópula**: sobre los U(0,1), ajustar una t-copula que captura la
   estructura de dependencia (correlación + dependencia de colas).
4. **Sampling**: samplear de la t-copula para generar N paths × horizonte.
5. **Back-transform**: aplicar la PPF (inversa de la CDF) de Johnson SU para
   convertir los U(0,1) en retornos sintéticos.
6. **Drift + wealth**: agregar drift diario y calcular wealth acumulado.

## Distribuciones Marginales

5 distribuciones: Normal, t, NCt, Laplace, Johnson SU.

Johnson SU es empíricamente el mejor fit para retornos de equities. El slide
71 del curso muestra que Normal subestima consistentemente el VaR, mientras
que Johnson SU produce error aproximadamente cero.

**Validación:** test de Kolmogorov-Smirnov sobre cada marginal. Si el p-valor
del KS es < 0.05, la distribución es rechazada para ese nivel de confianza.
En SPY, Normal es sistemáticamente rechazada (p < 0.001) mientras que
Johnson SU no lo es (p > 0.2).

## Familias de Cópulas

| Cópula | Simetría | Dependencia de Colas | Caso de Uso |
|--------|----------|----------------------|-------------|
| t | Simétrica | Inferior + superior | Clusters de equities, correlación en crisis |
| Gaussiana | Simétrica | Ninguna | Baseline, aproximación de bajo rango |
| Clayton | Asimétrica | Inferior | Clustering de drawdowns |
| Gumbel | Asimétrica | Superior | Clustering de rallies |
| Frank | Simétrica | Ninguna | Correlación de bonos / FX |

### Cuándo usar cada una

- **t-Copula**: la opción por defecto para portfolios de equities. Captura
  el hecho de que en las crisis todas las correlaciones tienden a 1.
- **Gaussiana**: útil como baseline o cuando los datos son aproximadamente
  normales multivariados (bonos investment grade, FX majors).
- **Clayton**: captura asimetría donde las caídas son más correlacionadas que
  las subidas (mercados emergentes, high yield).
- **Gumbel**: captura asimetría donde las subidas son más correlacionadas
  (rallies de crypto, squeezes).
- **Frank**: útil para activos con correlación débil y sin estructura de colas
  (commodities vs equities).

## Validación de la Cópula

Comparar la matriz de correlación simulada vs la real mediante error absoluto
medio. También comparar con diferentes valores de df (como en ej6) para
encontrar el óptimo. Un df bajo (2-4) indica fuerte dependencia de colas; un
df alto (> 10) se aproxima a la cópula gaussiana.

## Escenarios Multi-CAGR

Correr la misma simulación a múltiples niveles de drift
(−30%, −15%, 0%, +20%, +35%, +50%) para stress-testear un portfolio bajo
diferentes regímenes macro. Esto permite responder preguntas como:
"¿qué probabilidad hay de perder 30% en 1 año si el CAGR real es 0%?"
vs "¿y si el CAGR real es 15%?"

## Interpretación de Resultados

- **Fan chart**: percentiles 5/25/50/75/95 del wealth acumulado. El ancho del
  abanico mide la incertidumbre — crece con el horizonte.
- **Forward VaR 95%**: peor retorno esperado en el percentil 5. Si es -20%,
  hay 5% de probabilidad de perder 20% o más.
- **Expected Shortfall (cVaR)**: pérdida promedio en el peor 5%. Siempre es
  peor que el VaR. La diferencia entre VaR y cVaR mide la severidad de las
  colas.
- **MaxDD forward**: máximo drawdown esperado en cada path. El percentil 95
  del MaxDD es una medida conservadora del riesgo de drawdown.
- **Probabilidad de ruina**: fracción de paths que terminan por debajo de un
  umbral (ej: 50% del capital inicial). Debe ser cercana a 0 para estrategias
  viables.
