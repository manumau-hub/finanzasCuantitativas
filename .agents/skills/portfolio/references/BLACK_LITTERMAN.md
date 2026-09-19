# Modelo Black-Litterman

## Problema que resuelve

Los modelos clásicos (Markowitz, NCO) tienen dos limitaciones importantes:
1. Las restricciones son una forma indirecta de introducir una view propia,
   pero limitan la optimización arbitrariamente.
2. No permiten diferenciar la incertidumbre por activo (a veces estamos más
   convencidos de ciertas views que de otras).

Black & Litterman (Goldman Sachs) desarrollan un modelo bayesiano que:
- Parte de una **condición de equilibrio del mercado** (retornos implícitos
  del portafolio de mercado vía CAPM inverso).
- Permite al inversor introducir **views con incertidumbre**.
- Genera un **vector de retornos a posteriori** combinando ambas fuentes.

## El Modelo

### Distribución a priori (equilibrio de mercado)

```
N ~ (Pi, tau * Sigma)
```

Donde:
- **Pi**: retornos implícitos de equilibrio
- **Sigma**: matriz de covarianza
- **tau**: escalar de incertidumbre (típicamente 0.01-0.05)

### Pi = delta * Sigma * w_mkt

- **delta**: aversión al riesgo implícita del mercado
- **w_mkt**: ponderaciones del portafolio de mercado (market caps)

### Distribución de las Views

```
N ~ (Q, Omega)
```

Donde:
- **Q**: vector de retornos esperados según las views (Kx1)
- **Omega**: matriz de incertidumbre de las views (KxK)

### Distribución a posteriori

```
E(R) = [(tau*Sigma)^-1 + P^T Omega^-1 P]^-1 *
       [(tau*Sigma)^-1 * Pi + P^T Omega^-1 * Q]
```

**Sigma_post** = Sigma + [(tau*Sigma)^-1 + P^T Omega^-1 P]^-1

Donde **P** es la matriz de mapeo entre views y activos (KxN).

## Views

### Absolutas
```
P = [1, 0, 0, ...]  →  Activo i tendrá retorno Q[i]
```
Ejemplo: `BMA: +25%`, `LOMA: +40%`, `MELI: -10%`

### Relativas
```
P = [1, -1, 0, ...]  →  Activo i > Activo j en Q[k]
```
Ejemplo: `GGAL > SUPV + 11%`, `GGAL > BBAR + 7%`

## Matriz Omega (Idzorek)

Omega se construye proporcional a `P * Sigma * P^T`, escalado por las
confidencias del inversor:

```
Omega[i,i] = (P * Sigma * P^T)[i,i] * (1 - conf_i) / conf_i * tau
```

Donde `conf_i` está entre 0 (mínima confianza) y 1 (máxima confianza).

## Pipeline Completo

1. Calcular **delta** = (E(Rm) - Rf) / sigma_m^2
2. Calcular **Pi** = delta * Sigma * w_mkt
3. Definir views (absolutas vía `view_dict`, relativas vía `view_pairs`)
4. Construir **Omega** vía Idzorek con confidencias
5. Calcular retornos **posteriores**
6. Usar retornos posteriores en Markowitz / NCO

## Extensiones

- **Entropy Pooling (Meucci, 2006)**: generaliza BL usando máxima entropía,
  permite views sobre distribuciones completas (no solo medias).
- **Avramov (2004)**: modelo bayesiano de factores con clustering jerárquico.
- **Dynamic BL**: adapta el modelo a múltiples periodos con views cambiantes.
