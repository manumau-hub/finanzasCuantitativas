
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



# function with 4 inputs
def f(y, m, d, w):
    """ Auxiliar para generar el vencimiento"""
    # Ej El 3er viernes de diciembre de 2019
    # r = f(2019, 12, 4, 3)

    # get a 2-D array representing the specified month
    # each week is represented by an array
    # and the value of each element is its date of the month
    # Monday is the 0th element of each week, Sunday is the 6th element
    # days of the first week of the month before the 1st are 0s
    x = monthcalendar(y, m)
    # if the first week of the month includes the desired day of week
    # convert the week of month to 0-index so that it takes into account the first week
    if x[0][d]: w -= 1
    # return the weekday of the week number specified
    return x[w][d]


def conversor_ticker(ticker_opcion):
    """Conversor de ticker de opcion a ticker activo - hardcoded"""
    if ticker_opcion == 'AGR':
        ticker_stock = 'AGRO'

    elif ticker_opcion == 'ALU':
        ticker_stock = 'ALUA'

    elif ticker_opcion == 'BBA':
        ticker_stock = 'BBAR'

    elif ticker_opcion == 'BHI':
        ticker_stock = 'BHIP'

    elif ticker_opcion == 'BMA':
        ticker_stock = 'BMA'

    elif ticker_opcion == 'BOL':
        ticker_stock = 'BOLT'

    elif ticker_opcion == 'BYM':
        ticker_stock = 'BYMA'

    elif ticker_opcion == 'CAR':
        ticker_stock = 'CARC'

    elif ticker_opcion == 'CEC':
        ticker_stock = 'CECO2'

    elif ticker_opcion == 'CEP':
        ticker_stock = 'CEPU'

    elif ticker_opcion == 'COM':
        ticker_stock = 'COME'

    elif ticker_opcion == 'CRE':
        ticker_stock = 'CRES'

    elif ticker_opcion == 'EDN':
        ticker_stock = 'EDN'

    elif ticker_opcion == 'GFG':
        ticker_stock = 'GGAL'

    elif ticker_opcion == 'LOM':
        ticker_stock = 'LOMA'

    elif ticker_opcion == 'GVA':
        ticker_stock = 'VALO'

    elif ticker_opcion == 'MIR':
        ticker_stock = 'MIRG'

    elif ticker_opcion == 'MOR':
        ticker_stock = 'MORI'

    elif ticker_opcion == 'PAM':
        ticker_stock = 'PAMP'

    elif ticker_opcion == 'SUP':
        ticker_stock = 'SUPV'

    elif ticker_opcion == 'TEC':
        ticker_stock = 'TECO2'

    elif ticker_opcion == 'TGN':
        ticker_stock = 'TGNO4'

    elif ticker_opcion == 'TGS':
        ticker_stock = 'TGSU2'

    elif ticker_opcion == 'TRA':
        ticker_stock = 'TRAN'

    elif ticker_opcion == 'TXA':
        ticker_stock = 'TXAR'

    elif ticker_opcion == 'GVA':
        ticker_stock = 'VALO'


    elif ticker_opcion == 'YPF':
        ticker_stock = 'YPFD'

    elif ticker_opcion == 'TSL':
        ticker_stock = 'TSLA'
    
    elif ticker_opcion == 'MEL':
        ticker_stock = 'MELI'
    
    elif ticker_opcion == 'GOD':
        ticker_stock = 'GOLD'
    
    elif ticker_opcion == 'APL':
        ticker_stock = 'AAPL'



    else:
        ticker_stock = ticker_opcion

    return ticker_stock


