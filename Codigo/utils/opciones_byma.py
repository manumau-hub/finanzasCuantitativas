import datetime
from calendar import *

def mes_nombre_a_numero(mes_nombre):
    """Auxiliar para pasar de nombre mes a numero mes"""
    if (mes_nombre == 'EN') or (mes_nombre == 'E'):
        mes_numero = 1
    elif (mes_nombre == 'FE') or (mes_nombre == 'F'):
        mes_numero = 2
    elif (mes_nombre == 'AB') or (mes_nombre == 'A'):
        mes_numero = 4
    elif (mes_nombre == 'JU') or (mes_nombre == 'J'):
        mes_numero = 6
    elif (mes_nombre == 'JL') or (mes_nombre == 'L'):
        mes_numero = 7
    elif (mes_nombre == 'AG') or (mes_nombre == 'G'):
        mes_numero = 8
    elif (mes_nombre == 'SE') or (mes_nombre == 'S'):
        mes_numero = 9
    elif (mes_nombre == 'OC') or (mes_nombre == 'O'):
        mes_numero = 10
    elif (mes_nombre == 'NO') or (mes_nombre == 'N'):
        mes_numero = 11
    elif (mes_nombre == 'DI') or (mes_nombre == 'D'):
        mes_numero = 12
    else:
        mes_numero = 0
    return mes_numero

def fecha_expiracion(mes_numero):
    """Fecha de expiracion de la opcion dado el mes"""
    hoy = datetime.date.today()
    day_hoy = hoy.day
    month_hoy = hoy.month
    year_hoy = hoy.year
    if mes_numero == 0:
        return datetime.date(1999, 1, 1)
    elif mes_numero > month_hoy:
        day_e = f(year_hoy, mes_numero, 4, 3)
        month_e = mes_numero
        year_e = year_hoy
    elif mes_numero < month_hoy:
        day_e = f(year_hoy + 1, mes_numero, 4, 3)
        month_e = mes_numero
        year_e = year_hoy + 1
    else:
        year_e = year_hoy
        month_e = mes_numero
        day_e = f(year_hoy, mes_numero, 4, 3)
        if day_e >= day_hoy:
            pass
        else:
            day_e = f(year_hoy, mes_numero, 4, 3)
            year_e = year_hoy + 1
    return datetime.date(year_e, month_e, day_e)

def f(y, m, d, w):
    """Auxiliar para generar el vencimiento (ej: 3er viernes de diciembre)"""
    x = monthcalendar(y, m)
    if x[0][d]:
        w -= 1
    return x[w][d]

def conversor_ticker(ticker_opcion):
    """Conversor de ticker de opcion a ticker activo - hardcoded"""
    mapping = {
        'AGR': 'AGRO', 'ALU': 'ALUA', 'BBA': 'BBAR', 'BHI': 'BHIP', 'BMA': 'BMA',
        'BOL': 'BOLT', 'BYM': 'BYMA', 'CAR': 'CARC', 'CEC': 'CECO2', 'CEP': 'CEPU',
        'COM': 'COME', 'CRE': 'CRES', 'EDN': 'EDN', 'GFG': 'GGAL', 'LOM': 'LOMA',
        'GVA': 'VALO', 'MIR': 'MIRG', 'MOR': 'MORI', 'PAM': 'PAMP', 'SUP': 'SUPV',
        'TEC': 'TECO2', 'TGN': 'TGNO4', 'TGS': 'TGSU2', 'TRA': 'TRAN', 'TXA': 'TXAR',
        'YPF': 'YPFD', 'TSL': 'TSLA', 'MEL': 'MELI', 'GOD': 'GOLD', 'APL': 'AAPL',
    }
    return mapping.get(ticker_opcion, ticker_opcion)
