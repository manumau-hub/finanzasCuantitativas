# Medidas de Riesgo

## Medidas de Dispersión

| Medida | Fórmula | Descripción |
|--------|---------|-------------|
| Volatilidad (MV) | sqrt(w^T Sigma w) | Desviación estándar del portafolio |
| MAD | mean(\|r - mean(r)\|) | Desviación media absoluta |
| MSV | sqrt(mean(r_neg^2)) | Semi-desviación (solo pérdidas) |

## Value at Risk (VaR)

Pérdida máxima esperada con nivel de confianza (1-alpha):

| Método | Descripción |
|--------|-------------|
| `var_historic` | Quantil empírico de los retornos |
| `var_gaussian` | VaR paramétrico asumiendo normalidad |

## Conditional VaR (CVaR / Expected Shortfall)

Pérdida promedio en el peor (alpha)% de los casos:
```
CVaR = mean(r[r <= VaR(alpha)])
```
Siempre es más negativo (peor) que el VaR.

## Drawdown

| Medida | Descripción |
|--------|-------------|
| MDD | Máxima caída desde pico: min(P/cummax(P) - 1) |
| CDaR | Promedio del peor alpha% de drawdowns |
| Calmar | Retorno anualizado / \|MDD\| |

## Diversificación

| Medida | Descripción |
|--------|-------------|
| DR = sum(w_i sigma_i) / sigma_p | Diversification Ratio (>=1) |
| Risk Contribution | Contribución marginal al riesgo |
| Risk Contribution % | RC como fracción del riesgo total |

## Medidas en el Notebook (Riskfolio-Lib)

| Clave | Descripción |
|-------|-------------|
| 'vol' | Desviación estándar |
| 'MV' | Varianza |
| 'KT' | Raíz cuadrada de Curtosis |
| 'MAD' | Desviación media absoluta |
| 'MSV' | Semi desviación estándar |
| 'SKT' | Raíz cuadrada de semicurtosis |
| 'FLPM' | Omega ratio |
| 'SLPM' | Sortino ratio |
| 'VaR' | Valor en riesgo |
| 'CVaR' | Valor en riesgo condicional |
| 'TG' | Gini de cola |
| 'EVaR' | Valor en riesgo entrópico |
| 'RLVaR' | Valor en riesgo relativista |
| 'WR' | Peor realización (Minimax) |
| 'RG' | Rango de rendimientos |
| 'CVRG' | Rango de CVaR |
| 'MDD' | Calmar |
| 'DaR' | Drawdown al riesgo |
| 'CDaR' | Drawdown condicional |
| 'EDaR' | Drawdown entrópico |
| 'UCI' | Índice de úlcera |
| 'DR' | Diversification Ratio |
| 'DD' | Diversification Delta |
| 'RCE' | Risk Concentration Equivalent |
| 'NBE' | Effective Number of Bets |
