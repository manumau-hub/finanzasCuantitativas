# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 15:32:43 2019

@author: mmaurette
"""


import sys
sys.path.append('..')

from DataBaseAccess import DatabaseAccess
import matplotlib.pyplot as plt
import pandas as pd

# variables definition:
ticker = 'AAPL' # security to evaluate
date= "2019-04-04"

# initiating database access 
print("****************************** \n Initiate database connection \n ******************************")

str_vendor_database = 'Vendor'
server = 'PROD-VNDR-DB'
database = 'IvyDBUS'
username = 'tqa_user'
password = 'tqa_user'

db_vendor = DatabaseAccess.createInstanceOfDatabaseAccess(str_vendor_database, server, database, username, password)



# testing database connection
print("****************************** \n method: get_securityid_from_ticker \n ******************************")

"""def get_securityid_from_ticker(self, ticker, date='', country=''):"""

securityID = db_vendor.getSecurityIDFromTicker(ticker) # getting secutiry ID

print("\n Security ID for "+ticker+ " is :"+securityID)


print("****************************** \n method: get_ticker_from_securityID \n ******************************")

"""get_ticker_from_securityID(self, securityID, date='', country=''):"""

tick = db_vendor.getTickerFromSecurityID(securityID) # getting secutiry ID

print("\n Ticker for "+ securityID + " is : "+tick)




print("****************************** \n method: get_exercise_style \n ******************************")

"""get_exercise_style(self, securityID):"""

style = db_vendor.getOptionExerciseStyle(securityID) # getting secutiry ID

print("\n Ex. Style for "+ securityID + " is : "+ style)


print("****************************** \n method: pull_optionprice_database\n ******************************")

"""def pull_optionprice_database(self, str_security, date):"""

option_prices= db_vendor.pullOptionPricesTable(securityID, date)
print("****************************** \n Option price list \n ******************************")
print(option_prices.columns) # get list of columns of the dataframe
print(option_prices.head())




print("****************************** \n method: pull_optionprice_database_ticker\n ******************************")

"""def pull_optionprice_database_ticker(self, str_ticker, date):"""

option_prices_ticker= db_vendor.pullOptionPricesOfTicker(ticker, date)
print("****************************** \n Option price list \n ******************************")
print(option_prices_ticker.columns) # get list of columns of the dataframe
print(option_prices_ticker.head())



print("****************************** \n method: is_index\n ******************************")

"""  def is_index(self, securityID, table = 'SECURITY'):"""

indx = db_vendor.isIndex(securityID)
print("Index flag for security "+securityID+": "+ str(indx))





print("****************************** \n method: pullVolatilitySurfaceOfSecurityID\n ******************************")

"""def pull_optionprice_database(self, str_security, date):"""

vol_surface = db_vendor.pullVolatilitySurfaceOfSecurityID(securityID, date)
print("****************************** \n Option price list \n ******************************")
print(vol_surface.columns) # get list of columns of the dataframe
print(vol_surface.head())


print("****************************** \n method: pullVolatilitySurfaceOfTicker\n ******************************")

"""def pull_optionprice_database_ticker(self, str_ticker, date):"""

vol_surface_ticker= db_vendor.pullVolatilitySurfaceOfTicker(ticker, date)
print("****************************** \n Option price list \n ******************************")
print(vol_surface_ticker.columns) # get list of columns of the dataframe
print(vol_surface_ticker.head())



print("****************************** \n method: pull_ZCcurve_database\n ******************************")

"""pull_ZCcurve_database(self, date, curve = '', currency = ''):"""

ZC_curve= db_vendor.pullZCurve(date)
print("****************************** \n ZC_curve\n ******************************")
print(ZC_curve.head())




print("****************************** \n method: get_spot_from_securityID_date\n ******************************")

"""def get_spot_from_securityID_date(self, securityID, date):"""

spot = db_vendor.getUnderlyingSpotPriceFromSecurityID(securityID, date) # getting secutiry ID

print("\n Spot for "+ securityID + " and : "+date + ": "+ str(spot))



print("****************************** \n method: get_spot_from_ticker_date\n ******************************")

"""def get_spot_from_ticker_date(self, ticker, date):"""

spot_tick = db_vendor.getUnderlyingSpotPriceFromTicker(ticker, date) # getting secutiry ID

print("\n Spot for "+ securityID + " and : "+date + ": "+ str(spot_tick))





print("****************************** \n method: def get_option_info\n ******************************")

"""def get_option_info(self, securityID, table = 'OPTION_info'):"""

option_info = db_vendor.getOptionInfo(securityID) # getting secutiry ID

print("Option Info: ",option_info)







print("****************************** \n method: pull_securityids_database\n ******************************")

"""def pull_securityids_database(self):"""

sec_list= db_vendor.pull_securityids_database() # getting secutiry ID

print("Security List: ", sec_list.head())




print("****************************** \n method: get_securityid_from_CUSIP\n ******************************")

"""def get_securityid_from_CUSIP(self, CUSIP):"""


cusip = "03783310"
securityID_cusip = db_vendor.getSecurityIDFromCUSIP(cusip) # getting secutiry ID

print("Security ID for CUSIP : ",cusip, " is: ", securityID_cusip)



print("****************************** \n method: get_spot_list_from_securityID\n ******************************")

"""def get_spot_list_from_securityID(self, securityID, numdays, date, index =0):"""

spot_list = db_vendor.pullSpotListFromSecurityId(securityID, 20, date)

print(spot_list.head())



print("****************************** \n method: get_dividend_list\n ******************************")

"""def get_dividend_list(self, ticker, date):"""


div_list = db_vendor.pullDividendListFromTicker(ticker, date)

print(div_list)

print("****************************** \n method: get_last_dividend\n ******************************")

"""def get_last_dividend(self, securityID):"""

last_div = db_vendor.getLastDividend(securityID, date)

print("Last dividend for ", ticker, "is: ",last_div)

print("****************************** \n method: get_last_ExDate\n ******************************")

"""def get_last_ExDate(self, securityID):"""

last_ex_date = db_vendor.getLastExerciseDate(securityID, date)

print("Last ExDate for ", ticker, "is: ",last_ex_date)



print("****************************** \n method: get_last_option_price_list_from_securityID \n ******************************")

"""get_last_option_price_list_from_securityID(self, numdays, securityID, date): """

option_prices_list = db_vendor.pullLastNDaysOptionPriceFromSecurityId(securityID, 5, date)

print(option_prices_list.head()) 




print("****************************** \n method: get_last_volatility_surfaces_from_securityID \n ******************************")

"""get_last_volatility_surfaces_from_securityID(self, numdays, securityID, date): """

vol_surface_list = db_vendor.pullNDaysOfVolatilitySurfaceFromSecurityId(securityID, 10, date)


print(vol_surface_list.head()) 



print("****************************** \n method: get_dividend\n ******************************")

"""    def get_dividend(self, securityID , date , isIndex = 0): """


secID = db_vendor.getSecurityIDFromTicker('SPX')
div_index = db_vendor.getDividendYieldFromSecurityID(secID, date)


db_vendor.getDividendYieldFromSecurityID(secID, date)

print("Dividend yield for ", secID, "is: ",div_index)



