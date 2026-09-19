# Referencia de Ratios

Cada ratio está implementado en `scripts/ratios.py` como funciones planas
(sin clases), vectorizadas con numpy, que aceptan escalares y arrays 1-D.

## Convención de Tipo de Retornos

| Ratio | Tipo de Retorno | Razón |
|-------|----------------|-------|
| CAGR, Vol, Sharpe, Sortino | Lineales | Annualización estándar |
| VaR, cVaR (todos), R², Beta, IR, TE | Lineales | Estimación ML / regresión |
| Payoff, Profit Factor, WinLoss | **Log** | Propiedad asimétrica de log returns |
| Rachev A/B/C, CSR, OWR, OLR | **Log** | Material del curso slides 82-86 |
| Kelly | **Log** | Course notebooks `getKelly()` |
| Risk of Ruin | Lineales | Course notebooks `RoR()` / `RoRemp()` |

## Advertencias (del material del curso)

1. **Calmar degenera con el tiempo**: en más de 20 años, CAGR tiende a 5-7%
   y MaxDD se pisa en ~40%, así que Calmar ≈ 0.1 para la mayoría de las
   estrategias. Usar solo para comparaciones del mismo horizonte.

2. **Kurtosis ≠ colas pesadas**: kurtosis alta puede significar concentración
   en el pico, no necesariamente colas más pesadas. Siempre verificar los
   quantiles reales de cola.

3. **VaR Normal vs Johnson SU**: Normal consistentemente **subestima** el VaR
   (subestima el riesgo de cola). Johnson SU da error aproximadamente cero
   (ni sobre ni subestimación sistemática). cVaR muestra el sesgo opuesto:
   Normal **sobreestima** cVaR.

4. **Rachev A vs B vs C**: La mayoría de las librerías solo implementan A
   (simple ratio de quantiles). El material del curso slides 82-85 introduce
   B (medias de cola) y C (áreas ponderadas por KDE) para información más
   rica.

5. **Retornos lineales vs log para estadísticas de trades**: Payoff ratio,
   profit factor y win/loss ratio DEBEN computarse sobre retornos log
   (slides 77-80). Usar lineales introduce sesgo de asimetría.

6. **Look-ahead bias en ventanas móviles**: la normalización z-score y el
   range bounding deben usar ventana **móvil** (rolling), no global, para
   evitar data leakage.

7. **Convención de retorno acumulado**: `cumulative_returns(r)[i]` = retorno
   acumulado después de observar los retornos `r[0]..r[i]`. El último elemento
   incluye todos los retornos.

8. **Rolling Sharpe**: Usar ventana TTM. Los valores individuales de Sharpe
   son ruidosos; analizar la distribución (histograma + KDE) sobre la serie
   rolling.
