# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 17:05:45 2019

@author: mmaurette
"""


import os
import sys

sys.path.append('..')
from CacheAccess import *
import pandas as pd

 
# =============================================================================
# df_pickle_spy = pd.read_pickle('tickers_SP500_clean.pkl')
# tickers = (df_pickle_spy.Ticker)
# tickers =tickers.str.replace(' ','')
# tickers = list(tickers.str.replace(' ',''))
#     
# =============================================================================
folder_location = 'D:/Cache/'

dbs = ['vendor', 'pandora']

dates = ['2019-08-05', '2019-08-06', '2019-08-07', '2019-08-08', '2019-08-09', 
         '2019-08-12', '2019-08-13', '2019-08-14', '2019-08-15', '2019-08-16', 
         '2019-08-19', '2019-08-20', '2019-08-21', '2019-08-22', '2019-08-23', 
         '2019-08-26', '2019-08-27', '2019-08-28', '2019-08-29', '2019-08-30',
         '2019-09-03', '2019-09-04', '2019-09-05', '2019-09-06',
         '2019-09-09', '2019-09-10', '2019-09-11', '2019-09-12', '2019-09-13',
         '2019-09-16', '2019-09-17', '2019-09-18', '2019-09-19', '2019-09-20',
         '2019-09-23', '2019-09-24', '2019-09-25', '2019-09-26', '2019-09-27',
         '2019-09-30', '2019-10-01', '2019-10-02', '2019-10-03', '2019-10-04',
         '2019-10-07', '2019-10-08', '2019-10-09', '2019-10-10', '2019-10-11',
         '2019-10-14', '2019-10-15', '2019-10-16', '2019-10-17', '2019-10-18',
         '2019-10-21', '2019-10-22', '2019-10-23', '2019-10-24', '2019-10-25',
         '2019-10-28', '2019-10-29', '2019-10-30', '2019-10-31', '2019-11-01',
         '2019-11-04', '2019-11-05', '2019-11-06', '2019-11-07', '2019-11-08',
         '2019-11-11', '2019-11-12', '2019-11-13', '2019-11-14', '2019-11-15',
         '2019-11-18', '2019-11-19', '2019-11-20', '2019-11-21', '2019-11-22',
         '2019-11-25', '2019-11-26', '2019-11-27',               '2019-11-29']
         
root_finder_method = 'bisection'
model_name='Trinomial'
min_ttm = 0
root_finder_max_iter = 100
pricing_model_max_iter = 1000
# =============================================================================
# #for dates 0, 1... 4...7
# for date in dates[5:7]:
#     for ticker in tickers:
#         for db in dbs:
#             try:
#                 
#                 run_analytics_and_save_data_for_date_ticker(folder_location, ticker, date, db, 
#                                                 root_finder_method = 'bisection', model_name='Trinomial', min_ttm = 0,
#                                                 root_finder_max_iter = root_finder_max_iter, pricing_model_max_iter = pricing_model_max_iter)
#             except:
#                 pass
# =============================================================================
            
            
            


## just a couple of tickers, many dates
tickers = ['AAPL', 'BA', 'K']

date='2019-11-05'
ticker='AAPL'
db='vendor'
                
for date in dates[7:]:
    
    print(date)
    try:
        save_curve_data_for_date(folder_location, date, db)
        
    except:
        pass
    for ticker in tickers:
        print(date)
        for db in dbs:
            print(db)
            try:
                save_option_data_for_date_ticker(folder_location, ticker, date, db)
                #run_analytics_and_save_data_for_date_ticker(folder_location, ticker, date, db, 
                #                                root_finder_method = 'bisection', model_name='Trinomial', min_ttm = 0,
                #                                root_finder_max_iter = root_finder_max_iter, pricing_model_max_iter = pricing_model_max_iter)
            except:
                pass
            

 



           
            