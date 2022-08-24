
from bs4 import BeautifulSoup
import requests
import datetime


import pandas as pd

import sys

sys.path.append('..')

from Codigo.utils_opciones_byma import *


def web_scraping_opciones_iol():
    """ Scraping del panel de Opciones (IOL)"""
    url = 'https://iol.invertironline.com/mercado/cotizaciones/argentina/opciones/todas'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    opciones = soup.find('table', {'id': 'cotizaciones'})
    filas = opciones.find_all('tr')

    l = []
    tr = filas[0]
    td = tr.find_all('td')
    row = [tr.text for tr in td]
    l.append(row)
    for tr in filas[1:]:
        td = tr.find_all('td')
        row = [tr.text for tr in td]

        #Reemplazo ',' por '.' y paso el string a float
        for index in [1,2,3,4,5,6,7,8,9,10,11,12]:
            row[index] = row[index].replace('.', '')
            row[index] = row[index].replace(',', '.')
            try:
                row[index] = float(row[index])
            except:
                #Si no encuentra valor pone -99.99
                row[index] = -99.99

        l.append(row)

    """ Dataframe con data scrapeada"""
    panel_iol = pd.DataFrame(l[1:], columns=l[0])
    panel_iol = panel_iol.replace(r'\r+|\n+|\t+','', regex=True)
    panel_iol = panel_iol.replace(' ','', regex=True)

    #Me quedo con los operados
    panel_iol = panel_iol[panel_iol.ÚltimoOperado>0] 
    #Saco las columnas con informacion irrelevante 
    panel_iol = panel_iol[['Símbolo', 'ÚltimoOperado', 'Apertura', 'Mínimo', 'Máximo', 'ÚltimoCierre', 'MontoOperado']]
    #resetero los indices
    panel_iol = panel_iol.reset_index()
    del panel_iol['index']

    return panel_iol




def web_scraping_acciones_iol():

    l = []


    urlG = 'https://iol.invertironline.com/mercado/cotizaciones/argentina/acciones'

    page = requests.get(urlG)
    soup = BeautifulSoup(page.text, 'lxml')
    #precios = soup.find('table', {'class': 'tablapanel'})
    precios = soup.find('table', {'id': 'cotizaciones'})
    
    filas = precios.find_all('tr')

    l = []
    tr = filas[0]
    td = tr.find_all('td')
    row = [tr.text for tr in td]
    l.append(row)
    for tr in filas[1:]:
        td = tr.find_all('td')
        row = [tr.text for tr in td]

        #Reemplazo ',' por '.' y paso el string a float
        for index in [1,2,3,4,5,6,7,8,9,10,11,12]:
            row[index] = row[index].replace('.', '')
            row[index] = row[index].replace(',', '.')
            try:
                row[index] = float(row[index])
            except:
                #Si no encuentra valor pone -99.99
                row[index] = -99.99

        l.append(row)


    panel_acciones = pd.DataFrame(l[1:], columns=l[0])
    
    panel_acciones = panel_acciones.replace(r'\r+|\n+|\t+','', regex=True)
    panel_acciones = panel_acciones.replace(' ','', regex=True)

    return panel_acciones





def obtener_panel_opciones_byma(ticker = 'GGAL', clean_flag = False ):
    #Obtengo el panel crudo de IOL
    panel_iol = web_scraping_opciones_iol()



    #Obtengo el panel crudo de acciones (para el spot)
    panel_acciones = obtener_panel_acciones_iol()

    #Genero el nuevo panel
    panel_opciones = panel_iol.copy()
    #Renombro algunas columnas
    panel_opciones.rename(columns={'Símbolo': 'Especie', 'ÚltimoCierre': 'Last', 'ÚltimoOperado': 'Last'}) 
    
    #Le agrego las nuevas columnas (ojo con los tipos string, float, int, datetime)
    panel_opciones['Ticker_Opcion'] = ''
    panel_opciones['Ticker_Stock'] = ''
    panel_opciones['Tipo'] = ''
    panel_opciones['Strike'] = 0.0
    panel_opciones['ExpiryMonthName'] = ''
    panel_opciones['ExpiryMonthNumber'] = 0
    panel_opciones['ExpiryDate'] = datetime.date.today()
    panel_opciones['Spot'] = 0.0
    panel_opciones['TTM'] = 0
    panel_opciones['Moneyness'] = 0.0

    # Recorro el dataframe (opcion por opcion y completo cada una de las nuevas columnas)
 
    for fila in range(len(panel_opciones.Especie.values)):

        panel_opciones.at[fila,'Ticker_Opcion']  = panel_opciones.Especie.values[fila][0:3]
        panel_opciones.at[fila,'Ticker_Stock'] = conversor_ticker(panel_opciones.Ticker_Opcion.values[fila])
        panel_opciones.at[fila,'Tipo'] = panel_opciones.Especie.values[fila][3:4]
        panel_opciones.at[fila,'Tipo']  = panel_opciones.Tipo.values[fila].replace('V', 'P')


        #ENCHASTRE PARA CORREGIR STRIKES POST DIVIDENDO inicio
        if panel_opciones.Ticker_Opcion.values[fila]=='GFG':
            try:
                int(panel_opciones.Especie.values[fila][4:9])
                panel_opciones.Strike.values[fila] = int(panel_opciones.Especie.values[fila][4:9])/100.0
                
                if panel_opciones.Strike.values[fila]>500:
                    panel_opciones.Strike.values[fila]=panel_opciones.Strike.values[fila]/10
                
                panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.Especie.values[fila][9:10]
                try:
                    panel_opciones.ExpiryMonthNumber.values[fila] = mes_nombre_a_numero(panel_opciones.ExpiryMonthName.values[fila])
                except:
                    panel_opciones.ExpiryMonthNumber.values[fila] = 0

            except:
            #HORRIBLE!    
                panel_opciones.Strike.values[fila] = panel_opciones.Especie.values[fila][4:8]

                panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.Especie.values[fila][8:10]

                try:
                    int(panel_opciones.ExpiryMonthName.values[fila][0])
                    panel_opciones.Strike.values[fila] = float(panel_opciones.Strike.values[fila] + int(panel_opciones.ExpiryMonthName.values[fila][0])+int(panel_opciones.ExpiryMonthName.values[fila][1]))
                    panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.ExpiryMonthName.values[fila][1]
                except:
                    panel_opciones.Strike.values[fila] = float(panel_opciones.Strike.values[fila])

                try:
                    panel_opciones.ExpiryMonthNumber.values[fila] = mes_nombre_a_numero(panel_opciones.ExpiryMonthName.values[fila])
                except:
                    panel_opciones.ExpiryMonthNumber.values[fila] = 0

            panel_opciones.ExpiryDate.values[fila] = fecha_expiracion(panel_opciones.ExpiryMonthNumber.values[fila])

        
        #ENCHASTRE PARA CORREGIR STRIKES POST DIVIDENDO fin    
        else:
        ###    
            panel_opciones.Strike.values[fila] = panel_opciones.Especie.values[fila][4:8]

            panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.Especie.values[fila][8:10]

            try:
                int(panel_opciones.ExpiryMonthName.values[fila][0])
                panel_opciones.Strike.values[fila] = float(panel_opciones.Strike.values[fila] + int(panel_opciones.ExpiryMonthName.values[fila][0])+int(panel_opciones.ExpiryMonthName.values[fila][1]))
                panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.ExpiryMonthName.values[fila][1]
            except:
                panel_opciones.Strike.values[fila] = float(panel_opciones.Strike.values[fila])

            try:
                panel_opciones.ExpiryMonthNumber.values[fila] = mes_nombre_a_numero(panel_opciones.ExpiryMonthName.values[fila])
            except:
                panel_opciones.ExpiryMonthNumber.values[fila] = 0

            panel_opciones.ExpiryDate.values[fila] = fecha_expiracion(panel_opciones.ExpiryMonthNumber.values[fila])

        ###
        panel_opciones.Spot.values[fila] = obtener_spot_ticker(panel_acciones, panel_opciones.Ticker_Stock.values[fila])


        hoy = datetime.date.today()
        panel_opciones.TTM.values[fila] = (panel_opciones.ExpiryDate.values[fila] - hoy).days

        panel_opciones.Moneyness.values[fila] = panel_opciones.Spot.values[fila] / panel_opciones.Strike.values[fila]

    #Si se provee un ticker, se filtra por ticker, si no, se provee el panel completo
    if ticker == '':
        pass
    else:
        panel_opciones = panel_opciones[panel_opciones.Ticker_Stock == ticker]

   
    # Panel limpio: cambio de nombre, reordenamiento y limpieza minima del panel
    if clean_flag == True:
        # Sacar opciones sobre bonos
        panel_opciones = panel_opciones[~panel_opciones.Especie.str.contains('A24')]

        panel_opciones = panel_opciones[
            ['Especie', 'Ticker_Stock', 'Spot', 'Tipo', 'Strike', 'TTM', 'Último', 'Anterior','Moneyness']]

        panel_opciones = panel_opciones.rename(
            columns={'Ticker_Stock': 'Ticker', 'Tipo': 'CallPut', 'Último': 'Last','Anterior':'Close'}, inplace=False)

        panel_opciones = panel_opciones.sort_values(['TTM', 'Ticker', 'Strike', 'CallPut'])

        # Remover TTMs mayores de un año o negativos (por algun error)
        panel_opciones = panel_opciones[panel_opciones.TTM < 364]
        panel_opciones = panel_opciones[panel_opciones.TTM > 0]

        #Saco los -99.90
        panel_opciones = panel_opciones[panel_opciones.Last >= 0]

    try:
        
        panel_opciones = panel_opciones.reset_index()
        del panel_opciones['index']
    except:
        pass
    
    return panel_opciones


def obtener_curva(curva_nombre = 'badlar', tasa_badlar=0.405):
    """
    Curva de descuento:
    'badlar' contante
     o
    'caucion'
    """
    if curva_nombre == 'caucion':
        # Curva con valores de caucion
        l = []
        url = 'https://www.invertironline.com/mercado/cotizaciones/argentina/cauciones'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')
        cauciones = soup.find('table', {'class': 'table'})

        filas = cauciones.find_all('tr')

        tr = filas[0]
        td = tr.find_all('td')
        row = [tr.text for tr in td]
        row = row + ['Tasa']
        l.append(row)
        for tr in filas[1:]:
            td = tr.find_all('td')
            row = [tr.text for tr in td]

            row[0] = int(row[0])

            tasa = row[5].replace('%', '')
            tasa = tasa.replace(' ', '')
            tasa = float(tasa.replace(',', '.')) / 100.0
            row = row + [tasa]
            l.append(row)

        panel_cauciones = pd.DataFrame(l[1:], columns=l[0])

        panel_cauciones_final = panel_cauciones[panel_cauciones.Moneda == 'PESOS']

        panel_cauciones_final = panel_cauciones_final.rename(columns={'Plazo': 'Days', 'Tasa': 'Rate'}, inplace=False)

        panel_cauciones_final = panel_cauciones_final[['Days', 'Rate']]
        # remove missing values
        panel_cauciones_final = panel_cauciones_final[panel_cauciones_final['Rate'] > 0.001]

        curva = panel_cauciones_final

    elif curva_nombre == 'badlar':
        #Curva constante tasa badlar (puede ser curva tamabien)
        data = [[5, tasa_badlar], [360, tasa_badlar]]

        # Create the pandas DataFrame
        curva = pd.DataFrame(data, columns=['Days', 'Rate'])
    else:
        pass

    return curva


def obtener_spot_ticker(panel_acciones, ticker):
    """Obtiene el precio spot de ticker """
    ticker_list = list(panel_acciones['Especie'].values)

    try:
        index = ticker_list.index(ticker)
        spot = panel_acciones['Último'].values[index]
        spot = spot.replace('.', '')
        spot = float(spot.replace(',', '.'))
    except:
        try:
            index = ticker_list.index('CEDEAR'+ticker)
            spot = panel_acciones['Último'].values[index]
            spot = spot.replace('.', '')
            spot = float(spot.replace(',', '.'))
        except:
            spot = -99.99

    return spot


    ##############
##### LEGACY #########
    ##############






### esto es usando el viejo de rava
def obtener_panel_opciones_byma_rava(ticker = 'GGAL', clean_flag = False ):
    #Obtengo el panel crudo de Rava
    panel_rava = web_scraping_opciones_rava()
    #Obtengo el panel crudo de acciones (para el spot)
    panel_acciones = obtener_panel_acciones()

    #Genero el nuevo panel
    panel_opciones = panel_rava.copy()

    #Le agrego las nuevas columnas (ojo con los tipos string, float, int, datetime)
    panel_opciones['Ticker_Opcion'] = ''
    panel_opciones['Ticker_Stock'] = ''
    panel_opciones['Tipo'] = ''
    panel_opciones['Strike'] = 0.0
    panel_opciones['ExpiryMonthName'] = ''
    panel_opciones['ExpiryMonthNumber'] = 0
    panel_opciones['ExpiryDate'] = datetime.date.today()
    panel_opciones['Spot'] = 0.0
    panel_opciones['TTM'] = 0
    panel_opciones['Moneyness'] = 0.0

    # Recorro el dataframe (opcion por opcion y completo cada una de las nuevas columnas)
 
    for fila in range(len(panel_opciones.Especie.values)):

        panel_opciones.Ticker_Opcion.values[fila] = panel_opciones.Especie.values[fila][0:3]

        panel_opciones.Ticker_Stock.values[fila] = conversor_ticker(panel_opciones.Ticker_Opcion.values[fila])

        panel_opciones.Tipo.values[fila] = panel_opciones.Especie.values[fila][3:4]
        panel_opciones.Tipo.values[fila] = panel_opciones.Tipo.values[fila].replace('V', 'P')

        #ENCHASTRE PARA CORREGIR STRIKES POST DIVIDENDO inicio
        if panel_opciones.Ticker_Opcion.values[fila]=='GFG':
            try:
                int(panel_opciones.Especie.values[fila][4:9])
                panel_opciones.Strike.values[fila] = int(panel_opciones.Especie.values[fila][4:9])/100.0
                
                if panel_opciones.Strike.values[fila]>500:
                    panel_opciones.Strike.values[fila]=panel_opciones.Strike.values[fila]/10
                
                panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.Especie.values[fila][9:10]
                try:
                    panel_opciones.ExpiryMonthNumber.values[fila] = mes_nombre_a_numero(panel_opciones.ExpiryMonthName.values[fila])
                except:
                    panel_opciones.ExpiryMonthNumber.values[fila] = 0

            except:
            #HORRIBLE!    
                panel_opciones.Strike.values[fila] = panel_opciones.Especie.values[fila][4:8]

                panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.Especie.values[fila][8:10]

                try:
                    int(panel_opciones.ExpiryMonthName.values[fila][0])
                    panel_opciones.Strike.values[fila] = float(panel_opciones.Strike.values[fila] + int(panel_opciones.ExpiryMonthName.values[fila][0])+int(panel_opciones.ExpiryMonthName.values[fila][1]))
                    panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.ExpiryMonthName.values[fila][1]
                except:
                    panel_opciones.Strike.values[fila] = float(panel_opciones.Strike.values[fila])

                try:
                    panel_opciones.ExpiryMonthNumber.values[fila] = mes_nombre_a_numero(panel_opciones.ExpiryMonthName.values[fila])
                except:
                    panel_opciones.ExpiryMonthNumber.values[fila] = 0

            panel_opciones.ExpiryDate.values[fila] = fecha_expiracion(panel_opciones.ExpiryMonthNumber.values[fila])

        
        #ENCHASTRE PARA CORREGIR STRIKES POST DIVIDENDO fin    
        else:
        ###    
            panel_opciones.Strike.values[fila] = panel_opciones.Especie.values[fila][4:8]

            panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.Especie.values[fila][8:10]

            try:
                int(panel_opciones.ExpiryMonthName.values[fila][0])
                panel_opciones.Strike.values[fila] = float(panel_opciones.Strike.values[fila] + int(panel_opciones.ExpiryMonthName.values[fila][0])+int(panel_opciones.ExpiryMonthName.values[fila][1]))
                panel_opciones.ExpiryMonthName.values[fila] = panel_opciones.ExpiryMonthName.values[fila][1]
            except:
                panel_opciones.Strike.values[fila] = float(panel_opciones.Strike.values[fila])

            try:
                panel_opciones.ExpiryMonthNumber.values[fila] = mes_nombre_a_numero(panel_opciones.ExpiryMonthName.values[fila])
            except:
                panel_opciones.ExpiryMonthNumber.values[fila] = 0

            panel_opciones.ExpiryDate.values[fila] = fecha_expiracion(panel_opciones.ExpiryMonthNumber.values[fila])

        ###
        panel_opciones.Spot.values[fila] = obtener_spot_ticker(panel_acciones, panel_opciones.Ticker_Stock.values[fila])


        hoy = datetime.date.today()
        panel_opciones.TTM.values[fila] = (panel_opciones.ExpiryDate.values[fila] - hoy).days

        panel_opciones.Moneyness.values[fila] = panel_opciones.Spot.values[fila] / panel_opciones.Strike.values[fila]

    #Si se provee un ticker, se filtra por ticker, si no, se provee el panel completo
    if ticker == '':
        pass
    else:
        panel_opciones = panel_opciones[panel_opciones.Ticker_Stock == ticker]

   
    # Panel limpio: cambio de nombre, reordenamiento y limpieza minima del panel
    if clean_flag == True:
        # Sacar opciones sobre bonos
        panel_opciones = panel_opciones[~panel_opciones.Especie.str.contains('A24')]

        panel_opciones = panel_opciones[
            ['Especie', 'Ticker_Stock', 'Spot', 'Tipo', 'Strike', 'TTM', 'Último', 'Anterior','Moneyness']]

        panel_opciones = panel_opciones.rename(
            columns={'Ticker_Stock': 'Ticker', 'Tipo': 'CallPut', 'Último': 'Last','Anterior':'Close'}, inplace=False)

        panel_opciones = panel_opciones.sort_values(['TTM', 'Ticker', 'Strike', 'CallPut'])

        # Remover TTMs mayores de un año o negativos (por algun error)
        panel_opciones = panel_opciones[panel_opciones.TTM < 364]
        panel_opciones = panel_opciones[panel_opciones.TTM > 0]

        #Saco los -99.90
        panel_opciones = panel_opciones[panel_opciones.Last >= 0]

    try:
        
        panel_opciones = panel_opciones.reset_index()
        del panel_opciones['index']
    except:
        pass
    
    return panel_opciones



"""
Desacople de scraping y toqueteo
"""


### Deprecada, dado que dejo de funcionar, si alguien al arregla, bienvenido sea.
def web_scraping_opciones_rava():
    """ Scraping del panel de Opciones (Rava)"""
    # url = 'https://www.byma.com.ar/opciones/'
    url = 'http://www.rava.com/precios/panel.php?m=OPC'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    opciones = soup.find('table', {'class': 'tablapanel2'})
    filas = opciones.find_all('tr')

    l = []
    tr = filas[0]
    td = tr.find_all('td')
    row = [tr.text for tr in td]
    l.append(row)
    for tr in filas[1:]:
        td = tr.find_all('td')
        row = [tr.text for tr in td]

        #Reemplazo ',' por '.' y paso el string a float
        for index in [1,2,3,4,5,6,8,9]:
            row[index] = row[index].replace('.', '')
            row[index] = row[index].replace(',', '.')
            try:
                row[index] = float(row[index])
            except:
                #Si no encuentra valor pone -99.99
                row[index] = -99.99

        l.append(row)

    """ Dataframe con data scrapeada"""
    panel_rava = pd.DataFrame(l[1:], columns=l[0])

    return panel_rava

