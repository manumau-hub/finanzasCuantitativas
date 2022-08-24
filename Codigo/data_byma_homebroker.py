


import datetime
import pandas as pd
import numpy as np
from pyhomebroker import HomeBroker


# =============================================================================

# =============================================================================

def panel_opciones_homebroker(personal_data, ticker = '', clean_flag=True):
    
    ByMA_id = personal_data['ByMA_id']
    dni = personal_data['dni']
    user = personal_data['user']
    password = personal_data['password']
    
    
    
    hb = HomeBroker(ByMA_id)
    hb.auth.login(dni, user, password, raise_exception=True)
    # Connect to the server
    hb.online.connect()
    snapshot = hb.online.get_market_snapshot()
    panel_opciones = snapshot['options']
    panel_merval = snapshot['bluechips']
    panel_general = snapshot['general_board']
    panel_cedears = snapshot['cedears']
    
    
        #Si se provee un ticker, se filtra por ticker, si no, se provee el panel completo
     
    
    if clean_flag==True:
        
        panel_opciones = panel_opciones.reset_index()
        panel_opciones['Spot'] = 0.0 
        panel_opciones['TTM']=0
        panel_opciones['Moneyness']=0.0
        
        
        hoy = datetime.datetime.today()
      
        #Codigo para obtener el TTM
        x= (panel_opciones['expiration'] - hoy).values        
        days = x.astype('timedelta64[D]')
        ttm_f = (days+1) / np.timedelta64(1, 'D')
       
        panel_opciones['TTM'] = ttm_f.astype(np.int64) 
        
        panel_opciones = panel_opciones.rename(
            columns={'symbol':'Especie','underlying_asset':'Ticker', 'kind': 'CallPut', 'last': 'Last', 'strike': 'Strike','previous_close':'Close'}, inplace=False)
       
        panel_opciones['CallPut'] = pd.Series(panel_opciones['CallPut']).str.replace('CALL', 'C', regex=True)

        panel_opciones['CallPut'] = pd.Series(panel_opciones['CallPut']).str.replace('PUT', 'P', regex=True)
       
        panel_opciones = panel_opciones.sort_values(['TTM', 'Ticker', 'Strike', 'CallPut'])

        panel_opciones = panel_opciones[
            ['Especie','Ticker', 'Spot', 'CallPut', 'Strike', 'TTM', 'Last', 'Close','Moneyness']]
        
   
        ## Add Spot + moneyness ##        
    
        for fila in range(len(panel_opciones.Especie.values)):
            ticker_ = panel_opciones.Ticker.values[fila]
            panel_opciones['Spot'].values[fila] = get_spot_from_ticker(ticker_,snapshot)
        
        panel_opciones['Moneyness']= panel_opciones['Spot'] / panel_opciones['Strike']
    
        #Saco las Nan
        panel_opciones = panel_opciones[pd.notna(panel_opciones.Last)]
        

    
    
    if ticker == '':
        pass
    else:
        panel_opciones = panel_opciones[panel_opciones.Ticker == ticker]
    
  
    try:
        panel_opciones = panel_opciones.reset_index()
        del panel_opciones['index']
    except:
        pass
    
    return panel_opciones


def get_spot_from_ticker(ticker='GGAL', snapshot=''):
    spot = 0.0
     
    """Obtiene el precio spot de ticker """
    panel_merval = snapshot['bluechips'].reset_index() 
    panel_merval = panel_merval[panel_merval.settlement=='48hs']
    
    panel_general = snapshot['general_board'].reset_index()
    panel_general = panel_general[panel_general.settlement=='48hs']
    
    panel_cedears = snapshot['cedears'].reset_index()
    panel_cedears = panel_cedears[panel_cedears.settlement=='48hs']

    ticker_list_merval = list(panel_merval['symbol'].values)
    ticker_list_general = list(panel_general['symbol'].values)
    ticker_list_cedears = list(panel_cedears['symbol'].values)
    
    
    try:
        index = ticker_list_merval.index(ticker)
        spot = panel_merval['last'].values[index]
       
    except:
        try:
            index = ticker_list_general.index(ticker)
            spot = panel_general['last'].values[index]
        except:
            try:
                index = ticker_list_cedears.index(ticker)
                spot = panel_cedears['last'].values[index]
            except:
                spot = -99.99
    
    return spot

