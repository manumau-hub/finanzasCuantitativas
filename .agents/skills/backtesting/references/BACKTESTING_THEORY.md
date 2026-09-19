# Teoría de Backtesting — Marco Conceptual

## GIGO (Garbage In, Garbage Out)

El backtesting más sofisticado es inútil si los datos de entrada son basura.
Fuentes comunes de basura:

- **Precios ajustados incorrectamente** — splits, dividendos y recompras mal
  ajustados distorsionan retornos.
- **Survivorship bias** — usar solo activos que sobreviven hasta hoy ignora
  los que quebraron y sesga los retornos al alza.
- **Look-ahead bias** — usar información que no estaba disponible en el momento
  de la decisión (ej: estadísticas globales en vez de rolling).
- **Data snooping** — probar 1000 estrategias sobre el mismo dataset y
  quedarse con la mejor sin ajustar por múltiples comparaciones.

## El Trilema del Backtesting

Todo backtesting enfrenta tres fuerzas en conflicto:

```
         Realismo
            ╱╲
           ╱  ╲
          ╱    ╲
         ╱      ╲
   Simpleza ――――― Robustez
```

- **Realismo**: incluir costos, slippage, impacto de mercado, restricciones
  regulatorias. Más realista = más parámetros = más overfitting.
- **Simpleza**: pocos parámetros, reglas claras. Más simple = menos overfitting
  = menos realista.
- **Robustez**: la estrategia funciona en diferentes mercados, períodos y
  regímenes. Más robustez requiere más tests = más grados de libertad.

No se puede maximizar todo simultáneamente. El arte está en el equilibrio.

## Las 5 Etapas del Backtesting

El framework sigue 5 etapas secuenciales:

### Etapa 1: Datos
Obtener datos limpios, ajustados, sin sesgos. Múltiples fuentes para
cross-validation. Mínimo 5 años de datos diarios (preferiblemente 10+).
Incluir múltiples regímenes de mercado (bull, bear, lateral, alta/baja vol).

### Etapa 2: Investigación
Formular hipótesis de trading basadas en lógica económica o behavioral.
No hacer data mining ciego — cada estrategia debe tener una razón de ser.
Documentar el edge esperado y bajo qué condiciones debería funcionar o fallar.

### Etapa 3: Métricas
Calcular los 30+ ratios de performance y riesgo sobre el período IS
(in-sample). No mirar solo el Sharpe — analizar drawdowns, colas, consistencia
por períodos, y relación riesgo/retorno desde múltiples ángulos.

### Etapa 4: Parametrización
Optimizar parámetros de la estrategia (ventanas de SMA, umbrales de RSI, etc.)
dentro del período IS. Técnicas:
- **Parameter sweep**: grilla 2D/3D de parámetros.
- **Monte Carlo**: muestreo aleatorio del espacio de parámetros.
- **Walk-forward**: validación fuera de muestra con ventanas deslizantes.

⚠️ El error común es optimizar parámetros para maximizar Sharpe IS y luego
presentar ese Sharpe como si fuera representativo. El Sharpe OOS (walk-forward)
es el que realmente importa.

### Etapa 5: Validación
Confirmar que la estrategia generaliza fuera de la muestra:
- **Walk-forward CV**: IS/OOS con gap. Si el Sharpe OOS es muy inferior al IS,
  hay overfitting.
- **Stress testing**: ¿qué pasa si el mercado cambia de régimen? (shocks de
  volatilidad, correlaciones, tasas).
- **Simulación forward-looking**: miles de paths sintéticos con Johnson SU +
  cópula. Da una distribución completa de resultados posibles, no un solo
  número.
- **Portability**: probar en diferentes activos, mercados y períodos.

## Errores Comunes

| Error | Consecuencia | Cómo evitarlo |
|-------|-------------|---------------|
| Optimizar parámetros en全体 datos | Sharpe inflado, no replicable | Walk-forward CV |
| Ignorar costos de transacción | Estrategias de alta frecuencia parecen rentables | Incluir commission + slippage |
| Usar datos sin ajustar | Retornos distorsionados por splits/dividendos | Usar precios ajustados |
| Probar 100 estrategias y reportar la mejor | Sesgo de selección (data snooping) | Penalizar por múltiples comparaciones |
| No separar IS/OOS | Overfitting no detectado | Siempre tener un período OOS |
| Usar métricas globales para normalización | Look-ahead bias | Rolling windows exclusivamente |
| Confundir correlación con causalidad | Estrategias espurias | Exigir lógica económica subyacente |
