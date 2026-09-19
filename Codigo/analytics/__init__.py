"""Analytics: volatilidad implícita, payoffs, superficie de volatilidad."""
from . import payoffs
from .vol_implicita import impvolfunc_bs, impvolfunc_bin, bisect
from .payoffs import *

# vol_surface no se importa aquí para evitar cargar el módulo cuando
# hay incompatibilidad numpy/pandas. Usar: from Codigo.analytics.vol_surface import ...

__all__ = [
    "impvolfunc_bs",
    "impvolfunc_bin",
    "bisect",
]
