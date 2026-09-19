import yfinance as yf
import datetime
import pandas as pd


def get_stock_price(ticker: str) -> float:
    """
    Obtiene el precio spot actual del activo (mismo método que obtener_opciones_yahoo_finance).

    Parámetros
    ----------
    ticker : str
        Símbolo (ej. AAPL, GGAL).

    Retorna
    -------
    float
        Precio de cierre más reciente.
    """
    data = yf.Ticker(ticker)
    hist = data.history()
    if hist.empty:
        raise ValueError(f"No hay datos de precio para {ticker}")
    return float(hist.tail(1)["Close"].iloc[0])


def obtener_opciones_yahoo_finance(ticker='GGAL'):
    data = yf.Ticker(ticker)
    vencimientos = data.options
    calls = data.option_chain(vencimientos[0])[0]
    puts = data.option_chain(vencimientos[0])[1]
    for vencimiento in vencimientos[1:]:
        try:
            calls = pd.concat([calls, data.option_chain(vencimiento)[0]], ignore_index=True)
        except Exception:
            pass
        try:
            puts = pd.concat([puts, data.option_chain(vencimiento)[1]], ignore_index=True)
        except Exception:
            pass
    panel_opciones = pd.concat([calls, puts], ignore_index=True)
    panel_opciones['Ticker'] = ticker
    hist = data.history()
    panel_opciones['Spot'] = hist.tail(1)['Close'].iloc[0]
    return panel_opciones


def obtener_panel_opciones_nyse(ticker='GGAL', clean_flag=False):
    panel_opciones = obtener_opciones_yahoo_finance(ticker)
    panel_opciones['Moneyness'] = 0.0
    panel_opciones['TTM'] = 0
    panel_opciones['CallPut'] = ''
    panel_opciones = panel_opciones.reset_index()
    len_tick = len(ticker)
    for idx in list(panel_opciones.index.values):
        year = 2000 + int(panel_opciones.contractSymbol.values[idx][len_tick:len_tick+2])
        month = int(panel_opciones.contractSymbol.values[idx][len_tick+2:len_tick+4])
        day = int(panel_opciones.contractSymbol.values[idx][len_tick+4:len_tick+6])
        callput = panel_opciones.contractSymbol.values[idx][len_tick+6:len_tick+7]
        hoy = datetime.date.today()
        expiry_datetime = datetime.date(year, month, day)
        ttm = (expiry_datetime - hoy).days
        panel_opciones['TTM'].values[idx] = ttm
        panel_opciones['CallPut'].values[idx] = callput
        panel_opciones['Moneyness'].values[idx] = panel_opciones['Spot'].values[idx] / panel_opciones['strike'].values[idx]
    if clean_flag:
        panel_opciones = panel_opciones.rename(
            columns={'lastTradeDate': 'Last_Date', 'contractSymbol': 'Especie', 'strike': 'Strike', 'bid': 'Bid',
                     'ask': 'Ask', 'lastPrice': 'Last'}, inplace=False)
        panel_opciones = panel_opciones.sort_values(['TTM', 'Ticker', 'Strike', 'CallPut'])
        panel_opciones = panel_opciones[['Especie', 'Ticker', 'Spot', 'CallPut', 'Strike', 'TTM', 'Last', 'Moneyness', 'impliedVolatility', 'Bid', 'Ask']]
    try:
        panel_opciones = panel_opciones.reset_index()
        del panel_opciones['index']
    except Exception:
        pass
    return panel_opciones
