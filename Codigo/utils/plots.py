from matplotlib.dates import MonthLocator, YearLocator, DateFormatter
from matplotlib.ticker import FuncFormatter
from datetime import date
import numpy as np
import pylab

default_plot_size = (12, 8)

def plot(figsize=None):
    f = pylab.figure(figsize=figsize or default_plot_size)
    ax = f.add_subplot(1, 1, 1)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    ax.xaxis.grid(True, 'major', color=(0.9, 0.9, 0.9))
    ax.yaxis.grid(True, 'major', color=(0.9, 0.9, 0.9))
    return f, ax

def highlight_x_axis(ax):
    ax.axhline(0.0, linewidth=1, color=(0.5, 0.5, 0.5))

def to_datetime(d):
    return date(d.year(), d.month(), d.dayOfMonth())

def format_rate(r, digits=2):
    format = '%.' + str(digits) + 'f %%'
    return format % (r * 100.0)

def rate_formatter(digits=2):
    return FuncFormatter(lambda r, pos: format_rate(r, digits))

def date_formatter():
    return DateFormatter("%b '%y")

def locator(span):
    if span < 400:
        return MonthLocator()
    elif 400 <= span < 800:
        return MonthLocator(bymonth=[1, 4, 7, 10])
    elif 800 <= span < 3700:
        return YearLocator()
    else:
        return YearLocator(5)

def plot_curve(ax, dates, rates, ymin=None, ymax=None, digits=2, format_rates=False):
    span = dates[-1] - dates[0]
    dates = [to_datetime(d) for d in dates]
    for (rs, style) in rates:
        ax.plot_date(dates, rs, style)
    ax.set_xlim(min(dates), max(dates))
    ax.xaxis.set_major_locator(locator(span))
    ax.xaxis.set_major_formatter(date_formatter())
    ax.autoscale_view()
    ax.set_ylim(ymin, ymax)
    if format_rates:
        ax.yaxis.set_major_formatter(rate_formatter(digits))


def plot_payoff(payoff_func, S_range=None, ax=None, label=None, title=None, n_points=200, **payoff_kwargs):
    """
    Grafica el payoff de una estrategia en función del precio del subyacente S.

    Parámetros
    ----------
    payoff_func : callable
        Función (S, ...) que retorna el payoff. Ej: payoff_call, payoff_BullCS.
    S_range : array, optional
        Array de precios S. Si None, se infiere de los strikes en payoff_kwargs.
    ax : matplotlib axes, optional
        Ejes. Si None, se crea figura nueva.
    label : str, optional
        Etiqueta para la leyenda.
    title : str, optional
        Título del gráfico.
    n_points : int
        Número de puntos si S_range se genera automáticamente.
    payoff_kwargs
        Argumentos para payoff_func (K, K1, K2, K3, K4, n1, n2, etc.).

    Retorna
    -------
    ax
        Ejes matplotlib (para composición en notebooks).

    Ejemplo
    -------
    from Codigo.analytics import payoff_BullCS
    from Codigo.utils.plots import plot_payoff
    plot_payoff(payoff_BullCS, K1=90, K2=110, label="Bull Call Spread")
    """
    if payoff_kwargs:
        strikes = [
            v for k, v in payoff_kwargs.items()
            if (k.startswith("K") or k == "B") and isinstance(v, (int, float))
        ]
    else:
        strikes = [100.0]

    if S_range is None:
        S_min = min(strikes) * 0.5 if strikes else 50
        S_max = max(strikes) * 1.5 if strikes else 150
        S_range = np.linspace(S_min, S_max, n_points)

    S_range = np.asarray(S_range, dtype=float)
    payoff_vals = payoff_func(S_range, **payoff_kwargs)

    if ax is None:
        fig, ax = plot(figsize=default_plot_size)
    highlight_x_axis(ax)

    ax.plot(S_range, payoff_vals, label=label or payoff_func.__name__)
    ax.set_xlabel("Precio del subyacente S")
    ax.set_ylabel("Payoff")
    if title:
        ax.set_title(title)
    if label:
        ax.legend()
    ax.autoscale_view()
    return ax
