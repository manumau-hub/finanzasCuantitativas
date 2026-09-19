"""Modelos de pricing de opciones."""
from .european_bs import opcion_europea_bs
from .european_binomial import opcion_europea_bin
from .european_binomial_closed import opcion_europea_bin_c
from .european_mc import opcion_europea_mc, opcion_europea_mc_fv
from .european_fd import opcion_europea_fd
from .american_binomial import opcion_americana_bin
from .american_fd import opcion_americana_fd
from .american_bs import opcion_americana_bs
from .american_mc import opcion_americana_mc
from .strategy_pricer import (
    precio_estrategia,
    precio_estrategia_nombre,
    ESTRATEGIA_PIERNAS,
)

# QuantLib wrappers (misma firma que los modelos nativos)
try:
    from .european_bs_ql import opcion_europea_bs_ql
    from .european_binomial_ql import opcion_europea_bin_ql
    from .european_binomial_closed_ql import opcion_europea_bin_c_ql
    from .european_mc_ql import opcion_europea_mc_ql
    from .european_mc_fv_ql import opcion_europea_mc_fv_ql
    from .european_fd_ql import opcion_europea_fd_ql
    from .american_binomial_ql import opcion_americana_bin_ql
    from .american_fd_ql import opcion_americana_fd_ql
    from .american_bs_ql import opcion_americana_bs_ql
    from .american_mc_ql import opcion_americana_mc_ql
    _QL_AVAILABLE = True
except ImportError:
    opcion_europea_bs_ql = None
    opcion_europea_bin_ql = None
    opcion_europea_bin_c_ql = None
    opcion_europea_mc_ql = None
    opcion_europea_mc_fv_ql = None
    opcion_europea_fd_ql = None
    opcion_americana_bin_ql = None
    opcion_americana_fd_ql = None
    opcion_americana_bs_ql = None
    opcion_americana_mc_ql = None
    _QL_AVAILABLE = False

__all__ = [
    'opcion_europea_bs', 'opcion_europea_bin', 'opcion_europea_bin_c',
    'precio_estrategia', 'precio_estrategia_nombre', 'ESTRATEGIA_PIERNAS',
    'opcion_europea_mc', 'opcion_europea_mc_fv', 'opcion_europea_fd',
    'opcion_americana_bin', 'opcion_americana_fd', 'opcion_americana_bs', 'opcion_americana_mc',
    'opcion_europea_bs_ql', 'opcion_europea_bin_ql', 'opcion_europea_bin_c_ql',
    'opcion_europea_mc_ql', 'opcion_europea_mc_fv_ql', 'opcion_europea_fd_ql',
    'opcion_americana_bin_ql', 'opcion_americana_fd_ql',
    'opcion_americana_bs_ql', 'opcion_americana_mc_ql',
    '_QL_AVAILABLE',
]
