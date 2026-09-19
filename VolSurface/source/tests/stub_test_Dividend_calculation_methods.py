# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 10:17:39 2019

@author: mmaurette
"""


import sys
sys.path.append('..')

from DataBaseAccess import DatabaseAccess
from Dividend_calculation_methods import dividend_calculation_methods, constant, historical_average, linear_approximation

import pandas as pd
import matplotlib.pyplot as plt


from datetime import datetime
    

print("****************************** \n Initiate database connection \n ******************************")

#DATABASES ARE PULLED
db_vendor = DatabaseAccess.createInstanceOfDatabaseAccess('Vendor',
                                                    'PROD-VNDR-DB', 
                                                    'IvyDBUS', 
                                                    'tqa_user', 
                                                    'tqa_user')
db_pandora = DatabaseAccess.createInstanceOfDatabaseAccess('Pandora',
                                                     'Pandora', 
                                                     'EJV_Derivs')


date = '2019-04-04'
ticker_1 = 'AAPL'
ticker_3 = 'SPX'
ticker_2 = 'GOOG'


securityID_1_vendor = db_vendor.getSecurityIDFromTicker(ticker_1)
securityID_2_vendor = db_vendor.getSecurityIDFromTicker(ticker_2)
securityID_3_vendor = db_vendor.getSecurityIDFromTicker(ticker_3)

securityID_1_ejv = db_pandora.getSecurityIDFromTicker(ticker_1, db='EJV')
securityID_2_ejv = db_pandora.getSecurityIDFromTicker(ticker_2, db='EJV')
securityID_3_ejv = db_pandora.getSecurityIDFromTicker(ticker_3, db='EJV')

securityID_1_oracle = db_pandora.getSecurityIDFromTicker(ticker_1, db='ORACLE')
securityID_3_oracle = 'NA'
securityID_2_oracle = db_pandora.getSecurityIDFromTicker(ticker_2, db='ORACLE')


"""

Calculations for Ticker1

"""


div_list_vendor_1 = db_vendor.pullDividendListFromTicker(securityID_1_vendor, date)
div_list_pandora_1 = db_pandora.pullDividendListFromTicker(ticker_1, date)


spot_vendor_1 = db_vendor.getUnderlyingSpotPriceFromTicker(ticker_1, date)
spot_pandora_1 = db_pandora.getUnderlyingSpotPriceFromTicker(ticker_1, date)


print("Div list last year from Vendor")
print(div_list_vendor_1)
print("Div list last year from Pandora")
print(div_list_pandora_1)



div_method_1_vendor_1 = constant()

dividend_yield_1_vendor_1 = div_method_1_vendor_1.get_dividend_yield(securityID_1_vendor, 
                                                                date, 
                                                                args_dict={'dividend_list' : div_list_vendor_1,
                                                                           'spot' : spot_vendor_1})

print("Dividend yield for "+ ticker_1 + " using Vendor data and Constant method:"+ str(dividend_yield_1_vendor_1))

div_method_2_vendor_1 = historical_average()

dividend_yield_2_vendor_1 = div_method_2_vendor_1.get_dividend_yield(securityID_1_vendor, 
                                                                date, 
                                                                args_dict={'dividend_list' : div_list_vendor_1,
                                                                           'spot' : spot_vendor_1})


print("Dividend yield for "+ ticker_1+ " using Vendor data and Average method:"+ str(dividend_yield_2_vendor_1))

div_method_1_pandora_1 = constant()

dividend_yield_1_pandora_1 = div_method_1_pandora_1.get_dividend_yield(securityID_1_ejv, 
                                                                date, 
                                                                args_dict={'dividend_list' : div_list_pandora_1,
                                                                           'spot' : spot_pandora_1})


print("Dividend yield for "+ ticker_1+ " using Pandora data and Constant method:"+ str(dividend_yield_1_pandora_1))

div_method_2_pandora_1 = historical_average()

dividend_yield_2_pandora_1 = div_method_2_pandora_1.get_dividend_yield(securityID_1_ejv, 
                                                                date, 
                                                                args_dict={'dividend_list' : div_list_pandora_1,
                                                                           'spot' : spot_vendor_1})


print("Dividend yield for "+ ticker_1+ " using Pandora data and Average method:"+ str(dividend_yield_2_pandora_1))



dividend_yield_DB_pandora_1 = db_pandora.getDividendYieldFromSecurityID(securityID_1_oracle, date)


print("Dividend yield for "+ ticker_1+ " using Pandora ORACLE database:"+ str(dividend_yield_DB_pandora_1))



"""

Calculations for Ticker2

"""


div_list_vendor_2 = db_vendor.pullDividendListFromTicker(ticker_2, date)
div_list_pandora_2 = db_pandora.pullDividendListFromTicker(ticker_2, date)

spot_vendor_2 = db_vendor.getUnderlyingSpotPriceFromTicker(ticker_2, date)
spot_pandora_2 = db_pandora.getUnderlyingSpotPriceFromTicker(ticker_2, date)


print("Div list last year from Vendor")
print(div_list_vendor_2)
print("Div list last year from Pandora")
print(div_list_pandora_2)



div_method_1_vendor_2 = constant()

dividend_yield_1_vendor_2 = div_method_1_vendor_2.get_dividend_yield(securityID_2_vendor, 
                                                                date, 
                                                                args_dict={'dividend_list' : div_list_vendor_2,
                                                                           'spot' : spot_vendor_2})

print("Dividend yield for "+ ticker_2 + " using Vendor data and Constant method:"+ str(dividend_yield_1_vendor_2))

div_method_2_vendor_2 = historical_average()

dividend_yield_2_vendor_2 = div_method_2_vendor_2.get_dividend_yield(securityID_2_vendor, 
                                                                date, 
                                                                args_dict={'dividend_list' : div_list_vendor_2,
                                                                           'spot' : spot_vendor_2})


print("Dividend yield for "+ ticker_2+ " using Vendor data and Average method:"+ str(dividend_yield_2_vendor_2))

div_method_1_pandora_2 = constant()

dividend_yield_1_pandora_2 = div_method_1_pandora_2.get_dividend_yield(securityID_2_ejv, 
                                                                date, 
                                                                args_dict={'dividend_list' : div_list_pandora_2,
                                                                           'spot' : spot_pandora_2})


print("Dividend yield for "+ ticker_2+ " using Pandora data and Constant method:"+ str(dividend_yield_1_pandora_2))

div_method_2_pandora_2 = historical_average()

dividend_yield_2_pandora_2 = div_method_2_pandora_2.get_dividend_yield(securityID_2_ejv, 
                                                                date, 
                                                                args_dict={'dividend_list' : div_list_pandora_2,
                                                                           'spot' : spot_vendor_2})


print("Dividend yield for "+ ticker_2+ " using Pandora data and Average method:"+ str(dividend_yield_2_pandora_2))

dividend_yield_DB_pandora_2 = db_pandora.getDividendYieldFromSecurityID(securityID_2_oracle, date)


print("Dividend yield for "+ ticker_2+ " using Pandora ORACLE database:"+ str(dividend_yield_DB_pandora_2))






"""

Calculations for Ticker3

"""


div_list_vendor_3 = db_vendor.pullDividendListFromTicker(securityID_3_vendor, date)
div_list_pandora_3 = db_pandora.pullDividendListFromTicker(ticker_3, date)

spot_vendor_3 = db_vendor.getUnderlyingSpotPriceFromTicker(ticker_3, date)
spot_pandora_3 = db_pandora.getUnderlyingSpotPriceFromTicker(ticker_3, date, 1)


div_method_3_pandora_3 = linear_approximation()

dividend_yield_3_pandora_3 = div_method_3_pandora_3.get_dividend_yield(securityID_3_ejv, 
                                                                date, 
                                                                args_dict={'num_days' : 40,
                                                                           'database_name':'Pandora',
                                                                           'database':db_pandora})


print("Dividend yield for "+ ticker_3+ " using Pandora data and linear reg method:"+ str(dividend_yield_3_pandora_3))





div_method_3_vendor_3 = linear_approximation()

dividend_yield_3_vendor_3 = div_method_3_vendor_3.get_dividend_yield(securityID_3_vendor, 
                                                                date, 
                                                                args_dict={'num_days' : 60,
                                                                           'database_name':'Vendor',
                                                                           'database': db_vendor})


print("Dividend yield for "+ ticker_3+ " using Pandora data and linear reg method:"+ str(dividend_yield_3_vendor_3))


dividend_yield_DB_vendor_3 = db_vendor.getDividendYieldFromSecurityID(securityID_3_vendor, date, 1)


print("Dividend yield for "+ ticker_3+ " using Vendor database:"+ str(dividend_yield_DB_vendor_3))



