# Teoría de Portafolios (MPT)

## Supuestos Básicos

1. Dado un nivel de retorno buscado, los inversores prefieren el portafolio
   menos volátil (la volatilidad como riesgo).
2. Dada una aversión al riesgo (volatilidad tolerada), los inversores buscan
   el portafolio de máximo retorno para ese nivel de volatilidad.
3. El riesgo es el costo a pagar por el retorno buscado: no existe retorno
   sin riesgo (o a largo plazo es despreciable).

## Fórmulas Base

### Portafolio de 2 activos

**Retorno esperado:**
```
E(Rp) = w_i * E(Ri) + w_j * E(Rj)
```

**Varianza:**
```
V(Rp) = w_i^2 * sigma_i^2 + w_j^2 * sigma_j^2 + 2 * w_i * w_j * rho_ij * sigma_i * sigma_j
```

### Portafolio de N activos (notación matricial)

**Retorno esperado:**
```
E(Rp) = w^T * mu
```

**Varianza:**
```
V(Rp) = w^T * Sigma * w
```

## Markowitz (1952)

Harry Markowitz plantea que un inversor racional construye su portafolio
maximizando el retorno para una varianza asumida, moviéndose dentro de
curvas de indiferencia e isovarianza.

### Frontera Eficiente

Conjunto de portafolios que ofrecen el máximo retorno para cada nivel de
riesgo (o mínimo riesgo para cada nivel de retorno).

### Limitaciones de Markowitz

1. **Inestabilidad**: las soluciones óptimas son muy sensibles al ruido
   (típico de mercados financieros).
2. **Retornos desconocidos**: no conocemos los retornos ni varianzas a
   posteriori.
3. **Supuestos fuertes**: normalidad de retornos, homocedasticidad.

### Soluciones a las limitaciones

- **Clustering** → NCO, HRP, HERC (reducir ruido promediando errores dentro
  de clusters de activos similares).
- **Black-Litterman** → Incorporar visión personal con incertidumbre.
- **Shrinkage** → Ledoit-Wolf, OAS para covarianzas más robustas.

## CAPM

```
E[Ri] = Rf + beta_i * (E[Rm] - Rf)
```

Relaciona el rendimiento esperado de un activo con su riesgo sistemático
(beta) respecto al mercado.

## Fama-French (3 factores)

Agrega al CAPM los factores:
- **SMB** (Small Minus Big): tamaño
- **HML** (High Minus Low): valor libros/precio

## Capital Market Line (CML)

Recta tangente desde la tasa libre de riesgo (Rf) al portafolio óptimo
sobre la frontera eficiente. El portafolio tangente maximiza el Sharpe ratio.

```
E(Rp) = Rf + Sharpe_t * sigma_p
```

### Leverage y Deleverage sobre la CML

El portafolio tangente (máximo Sharpe) define la pendiente de la CML.
Cualquier punto sobre esta recta se obtiene combinando linealmente el
activo libre de riesgo (Rf) con el portafolio tangente — sin cambiar el
Sharpe ratio.

Sea `w` el peso asignado al portafolio tangente (y `1-w` al activo libre
de riesgo):

```
E(Rp) = (1-w) * Rf + w * E(Rt) = Rf + w * (E(Rt) - Rf)
sigma_p = w * sigma_t
Sharpe_p = (E(Rp) - Rf) / sigma_p = Sharpe_t
```

Casos según `w`:

| w | Qué significa | Efecto |
|---|---------------|--------|
| 0 < w < 1 | **Deleverage**: parte en Rf, parte en tangencia | Menor riesgo y retorno, mismo Sharpe |
| w = 1 | Portafolio tangente puro | Riesgo y retorno del tangente |
| w > 1 | **Leverage**: pide prestado a Rf para invertir más del 100% en tangencia | Mayor riesgo y retorno, mismo Sharpe |

Esto es conceptualmente distinto a moverse sobre la frontera eficiente
(solo activos riesgosos, sin Rf). La CML domina a la frontera eficiente
porque para cualquier nivel de riesgo ofrece mayor retorno (o menor riesgo
para el mismo retorno).
