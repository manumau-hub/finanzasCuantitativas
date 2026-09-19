


# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:39:03 2019

@author: mmaurette
"""

import sys
sys.path.append('..')

from DataBaseAccess import DatabaseAccess
from Dividend_calculation_methods import constant
from implied_vol_calculator import ImpliedVolatilityCalculator
from volatility_surface import gaussian_smooth, cubic_spline
import pandas as pd
import matplotlib.pyplot as plt

# =============================================================================
# # variables definition:
# =============================================================================
ticker = 'C' # security to evaluate
date = '2019-08-05' #evaluation date

# initiating database access 
print("****************************** \n Vol surface calculation - Vendor\n ******************************")

db_vendor = DatabaseAccess.createInstanceOfDatabaseAccess('Vendor', server ='PROD-VNDR-DB',
                                                          database = 'IvyDBUS',
                                                          username = 'tqa_user',
                                                          password = 'tqa_user')
# testing database connection
securityID = db_vendor.getSecurityIDFromTicker(ticker) # getting secutiry ID

div_method = constant()
#ts = pd.to_datetime(str(db_vendor.get_last_ExDate(securityID, date)[0][0])) # get last Exdate
#last_ExDate = ts.strftime('%d-%b-%Y') # change the string stamp...

div_list = db_vendor.pullDividendListFromTicker(securityID, date)
spot=db_vendor.getUnderlyingSpotPriceFromSecurityID(securityID, date)
dividend_yield_vendor = div_method.get_dividend_yield(securityID, 
                                                date,
                                                 args_dict={'dividend_list' : div_list,
                                                                           'spot' : spot})

                                                                                       # dividend calculation
ZC_curve_vendor = db_vendor.pullZCurve(date)
option_prices_vendor = db_vendor.pullOptionPricesTable(securityID, date)
root_finder_max_iter = 100
pricing_model_max_iter = 1500
min_ttm =0

root_finder_method = 'bisection' #'ridder'#'toms748'#'brent'#, 'bisection' #'newton', 'jakel'
model_name='Trinomial'


iVol_obj_vendor = ImpliedVolatilityCalculator(root_finder_method,
                                              model_name,
                                              ZC_curve_vendor,
                                              dividend_yield_vendor,
                                              option_prices_vendor,
                                              date,
                                              min_ttm,
                                              root_finder_max_iter,
                                              pricing_model_max_iter)
model_prices_vendor = iVol_obj_vendor.calculateImpliedVol()


vol_surface_obj_vendor = gaussian_smooth()



vol_surface_vendor = vol_surface_obj_vendor.generate_volatility_surface(model_prices_vendor)

print(vol_surface_vendor.head())

vol_surface_raw = db_vendor.pullVolatilitySurfaceOfSecurityID(securityID, date)





# initiating database access 
print("****************************** \n Vol surface calculation - Pandora\n ******************************")

db_pandora = DatabaseAccess.createInstanceOfDatabaseAccess('Pandora',
                                                     'Pandora', 
                                                     'EJV_Derivs')
# testing database connection
securityID_ejv = db_pandora.getSecurityIDFromTicker(ticker) # getting secutiry ID
securityID_pandora =  db_pandora.getSecurityIDFromTicker(ticker, db='ORACLE') # getting secutiry ID
div_method_pandora = constant()

div_list_pandora = db_pandora.pullDividendListFromTicker(securityID_ejv, date)
spot_pandora = db_pandora.getUnderlyingSpotPriceFromSecurityID(securityID_pandora, date)
dividend_yield_pandora_1 = div_method_pandora.get_dividend_yield(securityID_pandora, 
                                                date,
                                                 args_dict={'dividend_list' : div_list_pandora,
                                                                           'spot' : spot_pandora})

dividend_yield_pandora_2 = db_pandora.getDividendYieldFromSecurityID(securityID_pandora, date)
                                                                                       # dividend calculation
ZC_curve_pandora = db_pandora.calculateZCurveReplication(date)
option_prices_pandora = db_pandora.pullOptionPricesTable(securityID_ejv, date)



iVol_obj_pandora = ImpliedVolatilityCalculator(root_finder_method,
                                               model_name,
                                               ZC_curve_pandora,
                                               dividend_yield_pandora_2,
                                               option_prices_pandora,
                                               date,
                                               min_ttm,
                                               root_finder_max_iter,
                                               pricing_model_max_iter)

model_prices_pandora = iVol_obj_pandora.calculateImpliedVol()


vol_surface_obj_pandora = gaussian_smooth()
vol_surface_pandora = vol_surface_obj_pandora.generate_volatility_surface(model_prices_pandora)



print("****************************** \n Vol surface calculation - Point\n ******************************")
 
type_1 = 'C'
days_1 = 45
delta_1 = 15
 
ivol_point_1 = vol_surface_obj_pandora.generate_volatility_surface_point(model_prices_pandora, type_1, days_1, delta_1)
     
type_2 = 'P'
days_2 = 100
delta_2 = -95
 
ivol_point_2 = vol_surface_obj_pandora.generate_volatility_surface_point(model_prices_pandora, type_2, days_2, delta_2)

