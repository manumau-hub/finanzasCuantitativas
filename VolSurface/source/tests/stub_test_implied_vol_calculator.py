# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 18:23:38 2019

@author: mmaurette
"""



# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:39:03 2019

@author: dpedroso
"""

import sys
sys.path.append('..')

from DataBaseAccess import DatabaseAccess
from Dividend_calculation_methods import constant
from implied_vol_calculator import ImpliedVolatilityCalculator
import pandas as pd
import matplotlib.pyplot as plt

# =============================================================================
# # variables definition:
# =============================================================================
ticker = 'AAPL' # security to evaluate
date = '2019-04-04' #evaluation date

# initiating database access 
print("****************************** \n Initiate database connection \n ******************************")
db_vendor = DatabaseAccess.createInstanceOfDatabaseAccess('Vendor', server ='PROD-VNDR-DB',
                                                           database = 'IvyDBUS',
                                                           username = 'tqa_user',
                                                           password = 'tqa_user')
# db_vendor=DatabaseAccess.createInstanceOfDatabaseAccess('Pluto')

# testing database connection
print("****************************** \n testing connection... \n ******************************")
securityID = db_vendor.getSecurityIDFromTicker(ticker) # getting secutiry ID
print ("For ticker "+ticker+" securityID is: "+securityID)

print("****************************** \n Dividend calculation... \n ******************************")
# initiate dividend calculation methods:

div_method = constant()
ts = pd.to_datetime(str(db_vendor.getLastExerciseDate(securityID, date))) # get last Exdate
last_ExDate = ts.strftime('%d-%b-%Y') # change the string stamp...

last_div = db_vendor.getLastDividend(securityID, date)

div_list = db_vendor.pullDividendListFromTicker(securityID, date)
# ...and calculate the distribution yield
spot=db_vendor.getUnderlyingSpotPriceFromSecurityID(securityID, date)
dividend_yield = div_method.get_dividend_yield(securityID, 
                                                date,
                                                 args_dict={'dividend_list' : div_list,
                                                                           'spot' : spot})

                                                                                       # dividend calculation
print("====> Evaluation date:"+date)
print("====> Last Exdate:"+last_ExDate)
print("Dividend rate calculated: "+ str(dividend_yield))
print("Vendor Dividend yield on last ExDate: "+str(last_div))



print("****************************** \n Zero coupon rate \n ******************************")
# get zero rate curve
ZC_curve = db_vendor.pullZCurve(date)
#ZC_curve['TTM']=ZC_curve['Days']/daycount
print(ZC_curve.columns)
print(ZC_curve.head())

print("****************************** \n Security price list \n ******************************")
# get price list
option_prices = db_vendor.pullOptionPricesTable(securityID, date)

print("****************************** \n Implied volatility \n ******************************")


root_finder_max_iter = 100
pricing_model_max_iter = 1500
min_ttm =0


root_finder_method = 'bisection' #'ridder'#'toms748'#'brent'#, 'bisection' #'newton', 'jakel'
model_name='Trinomial'


""" 1 1"""
iVol_obj = ImpliedVolatilityCalculator(root_finder_method,
                                       model_name,
                                       ZC_curve,
                                       dividend_yield,
                                       option_prices,
                                       date,
                                       min_ttm,
                                       root_finder_max_iter,
                                       pricing_model_max_iter)


model_prices = iVol_obj.calculateImpliedVol()

print('\n Ivols using vendor data')
print(model_prices.head(10))



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
dividend_yield_pandora_1 = div_method.get_dividend_yield(securityID_pandora, 
                                                date,
                                                 args_dict={'dividend_list' : div_list_pandora,
                                                                           'spot' : spot_pandora})

dividend_yield_pandora_2 = db_pandora.getDividendYieldFromSecurityID(securityID_pandora, date)
                                                                                       # dividend calculation
ZC_curve_pandora = db_pandora.calculateZCurveReplication(date)
option_prices_pandora = db_pandora.pullOptionPricesTable(ticker, date)
root_finder_max_iter = 100
pricing_model_max_iter = 1500
min_ttm =0

root_finder_method = 'bisection' #'ridder'#'toms748'#'brent'#, 'bisection' #'newton', 'jakel'
model_name='Trinomial'


iVol_obj_pandora = ImpliedVolatilityCalculator(root_finder_method,
                                               model_name,
                                               ZC_curve,
                                               dividend_yield_pandora_2,
                                               option_prices_pandora,
                                               date,
                                               min_ttm,
                                               root_finder_max_iter,
                                               pricing_model_max_iter)

model_prices_pandora = iVol_obj_pandora.calculateImpliedVol()
print('\n Ivols using Pandora data')
model_prices_pandora.head(10)










