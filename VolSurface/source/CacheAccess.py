# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 11:51:44 2019

@author: mmaurette
"""

import pickle
from DataBaseAccess import DatabaseAccess
from Dividend_calculation_methods import dividend_calculation_methods, constant, historical_average
import pandas as pd
import os
import numpy as np
from datetime import datetime
import QuantLib as ql
from implied_vol_calculator import ImpliedVolatilityCalculator
from volatility_surface import gaussian_smooth


def save_curve_data_for_date(folder_location, date, database = 'vendor'):
    if database == 'vendor':
        username = 'tqa_user'
        password = 'tqa_user'
        db = DatabaseAccess.createInstanceOfDatabaseAccess('Vendor',
                                                            'PROD-VNDR-DB', 
                                                            'IvyDBUS',
                                                           username,
                                                           password)
    elif database=='pandora':
        
            db = DatabaseAccess.createInstanceOfDatabaseAccess('Pandora',
                                                          'Pandora', 
                                                          'EJV_derivs')
    
    folder_name = folder_location+ '/'+ str(date)
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
 
    if database == 'vendor':
        ZC_curve = db.pullZCurve(date)
    elif database == 'pandora': 
        ZC_curve = db.calculateZCurveReplication(date)
    
    file_name_0 = 'ZC_curve_' +str(date)+'_'+ database + '.csv'
    full_file_path = os.path.join(folder_name, file_name_0)
    ZC_curve.to_csv(full_file_path)    

    return


def save_option_data_for_date_ticker(folder_location, ticker, date, database = 'vendor'):
    if database == 'vendor':
        username = 'tqa_user'
        password = 'tqa_user'
        db = DatabaseAccess.createInstanceOfDatabaseAccess('Vendor',
                                                            'PROD-VNDR-DB', 
                                                            'IvyDBUS',
                                                           username,
                                                           password)
    elif database=='pandora':
        
            db = DatabaseAccess.createInstanceOfDatabaseAccess('Pandora',
                                                          'Pandora', 
                                                          'EJV_derivs')
    
    folder_name = folder_location+ '/'+ str(date)
    
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
 
#    if database == 'vendor':
#        ZC_curve = db.pull_ZCcurve_database(date)
#    elif database == 'pandora': 
#        ZC_curve = db.get_ZCcurve_replication(date)
#    
#    file_name_0 = 'ZC_curve_' +str(date)+'_'+ database + '.csv'
#    full_file_path = os.path.join(folder_name, file_name_0)
#    ZC_curve.to_csv(full_file_path)    
# 
    if database == 'vendor':
        secId = db.getSecurityIDFromTicker(ticker)
    elif database == 'pandora':
        secId = db.getSecurityIDFromTicker(ticker, 'ORACLE')
        
    folder_name = folder_location+ '/'+ str(date)+'/'+ ticker
        
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        
    file_name_1 = ticker + '_'+ str(date)+ '_option_prices_'+database+'.csv'
    
    full_file_path = os.path.join(folder_name, file_name_1)
    try:
        option_prices = db.pullOptionPricesOfTicker(ticker, date)
        option_prices.to_csv(full_file_path)  
    except:
        pass
    
    file_name_2 = ticker + '_'+ str(date)+ '_security_price_dividend_'+database+'.csv'
    full_file_path = os.path.join(folder_name, file_name_2)
            
    if database == 'vendor': 
        try:
            spot = db.getUnderlyingSpotPriceFromSecurityID(secId, date)
        except:
            spot = 0.0
        try:
            div_list = db.pullDividendListFromTicker(secId, date)
            
            div_method = historical_average()
            dividend_yield = div_method.get_dividend_yield(secId, date, args_dict={'dividend_list' : div_list,
                                                                                 'spot' : spot})
        except:
            dividend_yield = 0
       
    elif database == 'pandora': 
        try:
            dividend_yield = db.getDividendYieldFromSecurityID(secId, date)
        except:
            dividend_yield = 0
        try:
            spot = db.getUnderlyingSpotPriceFromSecurityID(secId, date)
        except:
            spot = 0.0
    
    security_prices_dividend = pd.DataFrame(index=None, data=None, columns=["Ticker","Id","Date","Spot", "DividendYield"] )
        
    new = pd.DataFrame(columns = security_prices_dividend.columns, index=None)
    new.loc[0]=[ticker, secId, date, spot, dividend_yield]
    security_prices_dividend= security_prices_dividend.append(new)
    security_prices_dividend.to_csv(full_file_path)    
        
    if database == 'vendor':
        file_name_3 = ticker + '_'+ str(date)+ '_volatility_surface_raw.csv'
        full_file_path = os.path.join(folder_name, file_name_3)
        try:
            volatility_surface_raw = db.pullVolatilitySurfaceOfSecurityID(secId, date)
            volatility_surface_raw.to_csv(full_file_path)    
        except:
            pass


def run_analytics_and_save_data_for_date_ticker(folder_location, ticker, date, database = 'vendor', 
                                                root_finder_method = 'bisection', model_name='Trinomial', min_ttm = 0,
                                                root_finder_max_iter = 100, pricing_model_max_iter = 2000):

    print(' SP500 security number. Ticker: ' + ticker + ' and Date: ' + date + '...')    
    try:
        ZC_curve = pull_ZCcurve_database(folder_location, date, database)
        print('0. SUCCESS: found curve for '+ date +' in Cache')
    except:
        print('0. FAIL: no curve for '+ date +' in Cache')
    
    
    folder_name = folder_location + str(date) + '/' + ticker
    try:
        option_prices = pull_optionprice_database(folder_location, ticker, date, database)
        print('1. SUCCESS: found option prices for '+ date + ' and ' + ticker + ' in Cache of ' + database + 'database')
    
    except:
        print('1. FAIL: no option prices for '+ date + ' and ' + ticker + ' in Cache of' + database + 'database')
    try:
        dividend_yield = get_dividend_yield(folder_location, ticker, date, database)
        print('2. SUCCESS: found div values for '+ date + ' and ' + ticker + ' in Cache of' + database + 'database')
    except:
        print('2. FAIL: no div values for '+ date + ' and ' + ticker + ' in Cache of' + database + 'database')
    try:
        ivol_class = ImpliedVolatilityCalculator(root_finder_method,
                                                 model_name,
                                                 ZC_curve,
                                                 dividend_yield,
                                                 option_prices,
                                                 date,
                                                 min_ttm,
                                                 root_finder_max_iter,
                                                 pricing_model_max_iter)
        
        file_name_4 = ticker+'_'+str(date)+'_modeled_prices_'+database+'.csv'
        full_file_path = os.path.join(folder_name, file_name_4)
        modeled_prices = ivol_class.getImpliedVolTable()
        modeled_prices.to_csv(full_file_path)
        print('3. SUCCESS: in ivol calc div for '+ date + ' and ' + ticker +' of' + database + 'database')
    except:
        print('3. FAIL: Error in ivol calc div for '+ date + ' and ' + ticker +' of' + database + 'database')
                
    try:
        file_name_5 = ticker+'_'+str(date)+'_volatility_surface_modeled_'+database+'.csv'
        full_file_path = os.path.join(folder_name, file_name_5)
        vol_surface_class = gaussian_smooth()
        vol_surface =  vol_surface_class.generate_volatility_surface(modeled_prices, 0.5, 10)
        vol_surface.to_csv(full_file_path)
        print('4. SUCCESS: in div vol surface calc for '+ date + ' and ' + ticker + ' of' + database + 'database')
    except:
        print('4. FAIL: Error in div vol surface calc for '+ date + ' and ' + ticker + ' of' + database + 'database')


  
def pull_ZCcurve_database(folder_location, date, database='vendor'):
    
    folder_name = folder_location+'/'+date
    file_name = 'ZC_curve_'+str(date)+'_'+database+ '.csv'
    full_file_path = os.path.join(folder_name, file_name)
    
    print(full_file_path)
    
    try:
        df = pd.read_csv(full_file_path)
    except:
        df=[]
        print('No data in Cache')
    return df 

def pull_optionprice_database(folder_location, ticker, date, database ='vendor'):
    folder_name = folder_location + '/' +date + '/' + ticker
    file_name = ticker + '_'+ str(date)+ '_option_prices_'+database+'.csv'
    full_file_path = os.path.join(folder_name, file_name)
    try:
        df = pd.read_csv(full_file_path)
    except:
        df=[]
        print('No data in Cache')
    return df    
  
def pull_volatilitysurface_database(folder_location,ticker, date, database='vendor'):
    folder_name = folder_location+'/'+date+'/'+ticker
    file_name = ticker +'_'+date + '_volatility_surface_raw.csv'
    full_file_path = os.path.join(folder_name, file_name)
    try:
        
        df = pd.read_csv(full_file_path)
    except:
        df=[]
        print('No Vendor data in Cache')
    return df    
   

#   def pull_modeled_prices(folder_location, ticker, date, database ='vendor'):
#        
#        folder_name = folder_location + '/' +date + '/' + ticker
#        file_name = ticker + '_'+ str(date)+ '_option_prices_+''vendor.csv'
#        if database == 'vendor':
#            try:
#                file_name = ticker + '_'+ str(date)+ '_option_prices_vendor.csv'
#                full_file_path = os.path.join(folder_name, file_name)
#                df = pd.read_csv(full_file_path)
#            except:
#                df=[]
#                print('No vendor data in Cache')
#        if database == 'pandora':
#            try:
#                file_name = ticker + '_'+ str(date)+ '_option_prices_pandora.csv'
#                full_file_path = os.path.join(folder_name, file_name)
#                df = pd.read_csv(full_file_path)
#            except:
#                df=[]
#                print('No pandora data in Cache')
#    

def pull_modeled_vol_surface(folder_location, ticker, date, database ='vendor'):
    
    folder_name = folder_location + '/' +date + '/' + ticker
    file_name = ticker + '_'+ str(date)+ '_volatility_surface_modeled_'+database+'.csv'
    full_file_path = os.path.join(folder_name, file_name)
    try:
        df = pd.read_csv(full_file_path)
    except:
        df=[]
        print('No vendor data in Cache')
    return df
 
def get_spot_from_securityID_date(folder_location, ticker, date, database = 'vendor'):
    
    folder_name = folder_location + '/' +date + '/' + ticker
    file_name = ticker + '_'+ str(date)+ '_security_price_dividend_'+database+'.csv'
    full_file_path = os.path.join(folder_name, file_name)
    try:
        df = pd.read_csv(full_file_path)
        spot = df.Spot.values[0]
    except:
        spot = 0
        print('No data in Cache')
    return spot


def get_dividend_yield(folder_location, ticker, date, database = 'vendor'):
    folder_name = folder_location + '/' +date + '/' + ticker
    file_name = ticker + '_'+ str(date)+ '_security_price_dividend_'+database+'.csv'
    full_file_path = os.path.join(folder_name, file_name)
    
    try:
        df = pd.read_csv(full_file_path)
        dividend_yield = df.DividendYield.values[0]
        
    except:
        dividend_yield = 0
        print('No data in Cache')
    return dividend_yield



def perform_analytics_for_date(date, tickers, database='vendor'):
        
    folder_location = 'D:/Cache/'
    ticker=tickers[0]
       
    print('SP500 security number: '+ str(tickers.index(ticker)) +', ticker: ' + ticker + ' and Date: ' + date + ' and '+ database + ' database')    
    try:
        
        vol_surface_vendor = pull_volatilitysurface_database(folder_location,ticker, date)
        
        
        vol_surface_replicated = pull_modeled_vol_surface(folder_location,ticker, date, database)
        
        vol_surface_output = vol_surface_vendor.drop(columns = ["Unnamed: 0", "SecurityID","ImpliedVolatility",'ImpliedStrike',"ImpliedPremium", "Dispersion"])
        
        vol_surface_output_replicated = vol_surface_output.copy()
        vol_surface_output_rel_difference = vol_surface_output.copy()
        vol_surface_output_difference = vol_surface_output.copy()
        
        
        vol_surface_output_replicated[ticker+'_replicated_Implied_vol'] = vol_surface_replicated['ImpliedVol']
        
        vol_surface_output[ticker+'_vendor_Implied_vol'] = vol_surface_vendor['ImpliedVolatility']
        
        
        vol_surface_output_rel_difference[ticker+'_rel_diff_per_Implied_vol_vendor'] = abs(vol_surface_output[ticker+'_vendor_Implied_vol'] - vol_surface_output_replicated[ticker+'_replicated_Implied_vol'] ) / vol_surface_output[ticker+'_vendor_Implied_vol']
        vol_surface_output_difference[ticker+'_rel_diff_per_Implied_vol_vendor'] = (vol_surface_output[ticker+'_vendor_Implied_vol'] - vol_surface_output_replicated[ticker+'_replicated_Implied_vol'] )
        
        

    except:
        pass            
    
    #for security_index in range(1, len(df_pickle_spy.AXIOMA_ID.values)):
    for ticker in tickers[1:]:        
        
        print('SP500 security number: '+ str(tickers.index(ticker)) +', ticker: ' + ticker + ' and Date: ' + date + ' and '+ database + ' database')
        
        
        
        try:
            vol_surface_vendor = pull_volatilitysurface_database(folder_location,ticker, date)
            vol_surface_replicated = pull_modeled_vol_surface(folder_location,ticker, date, database)
            vol_surface_output = vol_surface_vendor.drop(columns = ["Unnamed: 0", "SecurityID","ImpliedVolatility",'ImpliedStrike',"ImpliedPremium", "Dispersion"])
            vol_surface_output_replicated[ticker+'_replicated_Implied_vol'] = vol_surface_replicated['ImpliedVol']
            vol_surface_output[ticker+'_vendor_Implied_vol'] = vol_surface_vendor['ImpliedVolatility']
            vol_surface_output_rel_difference[ticker+'_rel_diff_per_Implied_vol'] = abs(vol_surface_output[ticker+'_vendor_Implied_vol'] - vol_surface_output_replicated[ticker+'_replicated_Implied_vol'] ) / vol_surface_output[ticker+'_vendor_Implied_vol']
            vol_surface_output_difference[ticker+'_rel_diff_per_Implied_vol'] = (vol_surface_output[ticker+'_vendor_Implied_vol'] - vol_surface_output_replicated[ticker+'_replicated_Implied_vol'] )
            
      
        except:
            pass
    
    folder_name = folder_location + '/' + str(date) + '/'
    file_name_test = str(date)+ '_tests_reults_relative_difference_with_raw_vol_surface_'+database+'.csv'
    full_file_path = os.path.join(folder_name, file_name_test)
    
    
    
    #Statistics
    
    vol_surface_output_rel_difference.loc['Mean'] = vol_surface_output_rel_difference.mean()
    temp = vol_surface_output_rel_difference.iloc[:,4:]
    
    vol_surface_output_rel_difference['Mean'] = temp.mean(axis=1)
    
    vol_surface_output_rel_difference.to_csv(full_file_path)
               
    return
        

  



