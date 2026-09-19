# Codigo

Módulos de finanzas cuantitativas para el curso de Derivados.

## Estructura

```
Codigo/
├── data/           # Extractores de datos (byma, nyse, homebroker)
├── pricing/        # Modelos de pricing (BS, binomial, MC, FD)
├── utils/          # Utilidades (plots, opciones_byma)
├── analytics/      # Vol implicita, payoffs
└── calculadoras/   # GUIs
```

Los archivos en la raíz (`opcion_europea_bs.py`, `data_byma.py`, etc.) son stubs de compatibilidad que re-exportan desde los módulos nuevos.
