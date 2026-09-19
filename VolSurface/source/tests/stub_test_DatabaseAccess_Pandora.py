# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 15:32:43 2019

@author: mmaurette
"""


import sys
sys.path.append('..')

from DataBaseAccess import DatabaseAccess

# variables definition:
ticker = 'AAPL' # security to evaluate
date = "2019-04-04" #evaluation date


# initiating database access 
print("****************************** \n Initiate database connection \n ******************************")

db_pandora = DatabaseAccess.createInstanceOfDatabaseAccess('Pandora')


# testing database connection
print("****************************** \n method: get_securityid_from_ticker \n ******************************")

"""def get_securityid_from_ticker(self, ticker, date='', country=''):"""

securityID_EJV = db_pandora.getSecurityIDFromTicker(ticker, db='EJV') # getting secutiry ID

print("\n Security ID EJV for "+ticker+ " is :"+securityID_EJV)

securityID_ORACLE = db_pandora.getSecurityIDFromTicker(ticker, db='ORACLE') # getting secutiry ID

print("\n Security ID ORACLE for "+ticker+ " is :"+securityID_ORACLE)


"""def get_axiomaid_from_ticker(self, ticker, date='', country=''):"""
axiomaID = db_pandora.getAxiomaIdFromTicker(ticker) # getting secutiry ID

print("\n Axioma ID for "+ticker+ " is :"+axiomaID)



# =============================================================================
# 
# 
# print("****************************** \n method: get_ticker_from_securityID \n ******************************")
# 
# """get_ticker_from_securityID(self, securityID, date='', country=''):"""
# 
# tick = db_vendor.get_ticker_from_securityID(securityID) # getting secutiry ID
# 
# print("\n Ticker for "+ securityID + " is : "+tick)
# 
# =============================================================================



print("****************************** \n method: get_exercise_style \n ******************************")

"""get_exercise_style(self, securityID):"""

style = db_pandora.getOptionExerciseStyle(ticker) # getting secutiry ID

securityID_EJV_2 = db_pandora.getSecurityIDFromTicker('SPX', db='EJV') # getting secutiry ID

style_2 = db_pandora.getOptionExerciseStyle('SPX', date)

print("\n Ex. Style for "+ securityID_EJV + " is : "+ style)
print("\n Ex. Style for "+ securityID_EJV_2 + " is : "+ style_2)



print("****************************** \n method: pull_optionprice_database\n ******************************")

"""def pull_optionprice_database(self, str_security, date):"""

option_prices= db_pandora.pullOptionPricesTable(ticker, date)
print("****************************** \n Option price list \n ******************************")
print(option_prices.columns) # get list of columns of the dataframe
print(option_prices.head())

option_prices_2= db_pandora.pullOptionPricesTable('SPX', date)
print("****************************** \n Option price list \n ******************************")
print(option_prices_2.columns) # get list of columns of the dataframe
print(option_prices_2.head())



print("****************************** \n method: pull_optionprice_database_ticker\n ******************************")

"""def pull_optionprice_database_ticker(self, str_ticker, date):"""

option_prices_ticker= db_pandora.pullOptionPricesTable(ticker, date)
print("****************************** \n Option price list \n ******************************")
print(option_prices_ticker.columns) # get list of columns of the dataframe
print(option_prices_ticker.head())




print("****************************** \n method: pull_optionprice_database_ticker\n ******************************")

"""def pull_optionprice_database_ticker(self, str_ticker, date):"""

option_prices_ticker_2= db_pandora.pullOptionPricesTable('SPX', date)
print("****************************** \n Option price list \n ******************************")
print(option_prices_ticker_2.columns) # get list of columns of the dataframe
print(option_prices_ticker_2.head())


print("****************************** \n method: is_index\n ******************************")

"""  def is_index(self, securityID, table = 'SECURITY'):"""

indx = db_pandora.isIndex(ticker)
print("Index flag for security "+ticker+": "+ str(indx))

indx_2 = db_pandora.isIndex('SPX')
print("Index flag for security "+'SPX'+": "+ str(indx_2))



print("****************************** \n method: pull_ZCcurve_database\n ******************************")

"""pull_ZCcurve_database(self, date, curve = '', currency = ''):"""

ZC_curve= db_pandora.pullZCurve(date)
print("****************************** \n ZC_curve\n ******************************")
print(ZC_curve.head())




print("****************************** \n method: get_spot_from_securityID_date\n ******************************")

"""def get_spot_from_securityID_date(self, securityID, date):"""

spot = db_pandora.getUnderlyingSpotPriceFromSecurityID(securityID_ORACLE, date) # getting secutiry ID

print("\n Spot for "+ securityID_ORACLE + " and : "+date + ": "+ str(spot))



print("****************************** \n method: get_spot_from_ticker_date\n ******************************")

"""def get_spot_from_ticker_date(self, ticker, date):"""

spot_tick = db_pandora.getUnderlyingSpotPriceFromTicker(ticker, date) # getting secutiry ID

print("\n Spot for "+ securityID_ORACLE + " and : "+date + ": "+ str(spot_tick))



print("****************************** \n method: get_spot_list_from_securityID\n ******************************")

"""def get_spot_list_from_securityID(self, securityID, numdays, date, index =0):"""

spot_list = db_pandora.pullSpotTableFromTicker(securityID_ORACLE, 20, date)

print(spot_list.head())



print("****************************** \n method: get_dividend_list\n ******************************")

"""def get_dividend_list(self, ticker, date):"""


div_list = db_pandora.pullDividendListFromTicker(ticker, date)

print(div_list)

print("****************************** \n method: get_last_dividend\n ******************************")

"""def get_last_dividend(self, securityID):"""

last_div = db_pandora.getLastDividendFromTicker(ticker, date)

print("Last dividend for ", ticker, "is: ",last_div)


# =============================================================================
# 
# print("****************************** \n method: get_last_ExDate\n ******************************")
# 
# """def get_last_ExDate(self, securityID):"""
# 
# last_ex_date = db_pandora.get_last_ExDate(securityID, date)
# 
# print("Last ExDate for ", ticker, "is: ",last_ex_date)
# 
# =============================================================================

# =============================================================================
# 
# print("****************************** \n method: get_last_option_price_list_from_securityID \n ******************************")
# 
# """get_last_option_price_list_from_securityID(self, numdays, securityID, date): """
# 
# option_prices_list = db_pandora.get_last_option_price_list_from_securityID(5, ticker, date)
# 
# print(option_prices_list.head()) 
# 
# =============================================================================


print("****************************** \n method: get_dividend\n ******************************")

"""    def get_dividend(self, securityID , date , isIndex = 0): """

div = db_pandora.getDividendYieldFromSecurityID(securityID_ORACLE, date)

print("Dividend yield for ", securityID_ORACLE, "is: ",div)

