# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 17:05:13 2019

@author: dpedroso
"""

import sys
sys.path.append('..')    
import axioma_vol_surface as ax_vol_surf
import pandas as pd
import numpy as np
import itertools # tool for efficient nested for loop

ticker = 'AAPL' # security to evaluate
date = '2019-04-04' #evaluation date
str_vendor_database = 'Vendor'
server = 'PROD-VNDR-DB'
database = 'IvyDBUS'
username = 'tqa_user'
password = 'tqa_user'


# =============================================================================
# ## initiate Axioma volatility surface module
# =============================================================================

ax_vol_surface_vendor = ax_vol_surf.axioma_volatility_surface(database= str_vendor_database,
                                                       pricer_max_iterations = 1500,       # number of iterations when using tree calculation
                                                       root_finder_max_iterations = 100,    # maximum iterations for the root finder method                    
                                                       pricing_model_name = 'CRR',       # BlackSholes, Trinomial, LR, CRR...  
                                                       root_finder_method = 'bisection',  # bissection, jakel, newton, ...
                                                       dividend_calculation_method = 'constant') # method for calculation of dividends
                                                       



# =============================================================================
#     Database bridge
# =============================================================================

ax_vol_surface_vendor.set_source_database(str_vendor_database, server, database, username, password)

# =============================================================================
#     NOTE: Other parameters can be set for the object: ax_vol_surface
# =============================================================================

# =============================================================================
# These dataframes contain data of all considered dates and tickers:
# =============================================================================



vol_surface_axioma_IV= ax_vol_surface_vendor.get_volatility_surface(ticker, date)


ZC_curve_axioma_IV = ax_vol_surface_vendor.get_discount_factor()
option_prices_axioma_IV = ax_vol_surface_vendor.get_market_price_list()
model_prices_axioma_IV = ax_vol_surface_vendor.get_implied_vol_list()
