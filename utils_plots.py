from matplotlib.dates import MonthLocator, YearLocator, DateFormatter
from matplotlib.ticker import FuncFormatter
from datetime import date
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


def plot_curve(ax, dates, rates, ymin=None, ymax=None, digits=2,
               format_rates=False):
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
