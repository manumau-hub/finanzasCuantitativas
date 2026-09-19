# Métodos Jerárquicos: HRP, HERC, NCO

## Motivación

Markowitz tiene un problema grave: las soluciones óptimas son muy inestables
con ruido (típico de la bolsa). Clusterizar grupos de activos y construir
sub-portafolios permite promediar errores de ruido blanco dentro de clusters
de activos similares.

Por ejemplo, en lugar de calcular covarianzas GGAL↔BTC, GGAL↔ETH, BBAR↔BTC, etc.
(ruidosas), armamos un sub-portafolio de ADRs y otro de cryptos: la covarianza
entre ambos portafolios es más robusta.

## Distancia y Clustering

### Correlación a Distancia

```
d = sqrt(2 * (1 - rho))
```

Es una métrica de distancia Euclídea propia.

### Métodos de Linkage

| Método | Descripción | Cuándo usar |
|--------|-------------|-------------|
| `single` | Menor distancia entre elementos | Conservador, evita agrupaciones agresivas |
| `complete` | Mayor distancia entre elementos | Clusters bien separados |
| `average` | Promedio de distancias | Balance |
| `ward` | Minimiza varianza intra-cluster | **Recomendado** para finanzas |
| `centroid` | Distancia entre centroides | Fácil interpretación |
| `median` | Similar a centroid pero robusto | Con ruido/outliers |

### Medidas de Codependencia

| Medida | Descripción |
|--------|-------------|
| `pearson` | Correlación lineal |
| `spearman` | Correlación de rangos (monótona) |
| `kendall` | Concordancia de pares |
| `distance` | Distancia Euclídea entre retornos |
| `mutual_info` | Dependencia total (lineal + no lineal) |

## HRP — Hierarchical Risk Parity (Lopez de Prado, 2016)

Algoritmo:
1. Calcular matriz de correlación → distancia → linkage → cuasi-diagonal
2. Recursively bisect el dendrograma
3. En cada división, asignar pesos inversamente proporcionales a la
   varianza de cada sub-portafolio
4. Sin optimización cuadrática — solo operaciones O(N)

Ventaja: extremadamente robusto, no sufre de inestabilidad de Markowitz.

## HERC — Hierarchical Equal Risk Contribution

Similar a HRP pero en cada bisect asigna pesos basados en riesgo igualitario:

```
alpha = risk_right / (risk_left + risk_right)
```

## NCO — Nested Clustered Optimization (De Prado, 2019)

Pipeline:
1. Clusterizar activos en K grupos
2. **Intra-cluster**: optimizar Markowitz dentro de cada cluster
3. **Inter-cluster**: optimizar la asignación entre clusters

Esto reduce la dimensionalidad del problema de optimización y promedia
ruido dentro de clusters.

### NCO con Restricciones (Pfitzinger & Katzke, 2019)

Extensión que permite incluir restricciones de pesos a priori,
manteniendo la robustez del NCO base:

- **Por activo**: `TEO >= 5%`, `SQQQ <= 3%`
- **Por clase**: `Cryptos >= 2%`, `ADR Bancos <= 6%`
- **Global**: `All assets <= 15%`

### Métodos de Asignación Intra-cluster

| Método | Descripción |
|--------|-------------|
| CHI-MD | Maximiza diversificación relativa |
| CHI-ERC | Maximiza Sharpe |
| HMV | Mínima varianza jerárquica |
| CMV | Mínima varianza por cluster |
| HRP | Hierarchical Risk Parity |
| CEW | Equal Weight por cluster |

### Métricas de Diversificación

| Métrica | Descripción |
|---------|-------------|
| DR | Diversification Ratio |
| DD | Diversification Delta |
| RCE | Risk Concentration Equivalent |
| NBE | Effective Number of Bets |
