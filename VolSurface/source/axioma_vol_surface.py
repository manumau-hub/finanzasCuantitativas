# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 16:30:13 2019

@author: dpedroso
"""


from DataBaseAccess import DatabaseAccess # database class
from implied_vol_calculator import *      # implied volatility for each available option in the database
import Dividend_calculation_methods   # method for calculation of dividends
from implied_vol_calculator import ImpliedVolatilityCalculator     # calculate implied volatility for each option in the market data
import volatility_surface as vol_surf
import scipy.optimize
from scipy.interpolate import interp1d # interpolation method
from pricingmodel import PricingModel
import numpy as np

class axioma_volatility_surface:
    
# =============================================================================
#     constructor method:
# =============================================================================
    def __init__(self,
                    database = 'Vendor',                # Vendor, Pandora
                    daycount = 360,                     # [days] day count convention
                    min_ttm = 0,                   # [year fraction] minimum time to maturity included in the calculation
                    pricer_max_iterations = 500,       # number of iterations when using tree calculation
                    root_finder_max_iterations = 50,    # maximum iterations for the root finder method                    
                    pricing_model_name = 'Trinomial',       # BlackSholes, Trinomial, LR, CRR...  
                    root_finder_method = 'bisection',  # bissection, jakel, newton, ...
                    dividend_calculation_method = 'constant', # method for calculation of dividends
                    from_vendor = False):               # get implied volatility surface from vendor database
                
        self._database = database
        self._daycount = daycount
        self._min_ttm = min_ttm
        self._pricer_max_iterations = pricer_max_iterations
        self._root_finder_max_iteration = root_finder_max_iterations
        self._root_finder_method = root_finder_method
        self._pricing_model_name = pricing_model_name
        self._from_vendor = from_vendor
        self._DiscFactor = None
        self._dividend_calculation_method = dividend_calculation_method
        #print('Object Axioma_volatility_surface initiated with standard parameters')
    
# =============================================================================
# set methods:        
# =============================================================================    
    def set_discount_factor(self, eval_date, DiscFactor=None):    
        print("****************************** \n Zero coupon rate \n ******************************")
        if(DiscFactor == None): # in case no discount factor is exogeneously determined
            # get zero rate curve
            try:
                self._DiscFactor = self._database_object.pullZCurve(eval_date)
            except:
                print('ERROR: discount factor not found.')
            self._DiscFactor['TTM']=self._DiscFactor['TTM']/self._daycount    # obtain the time to maturity in year fraction
        else:
            self._DiscFactor = DiscFactor # in case the discount factor comes from outside
        
    def set_dividend_calc_method(self, str_method):
        self._dividend_calculation_method = str_method
    
    def set_daycount(self, daycount):
        self._daycount = daycount    
    
    def set_root_finder_parameters(self, min_ttm = 0.0389, 
                                   pricer_max_iterations = 1000, 
                                   root_finder_max_iterations = 50, 
                                   root_finder_method = 'bissection'):
        self._pricer_max_iterations = pricer_max_iterations
        self._root_finder_max_iteration = root_finder_max_iterations
        self._root_finder_method = root_finder_method
        self._min_ttm = min_ttm

    def set_source_database(self, str_vendor_database, server, database, username='', password=''):
        if self._database == 'Vendor':
            self._database_object = DatabaseAccess.createInstanceOfDatabaseAccess(str_vendor_database,
                                                                                  server,
                                                                                  database,
                                                                                  username,
                                                                                  password)
        elif self._database == 'Pandora':
            self._database_object = DatabaseAccess.createInstanceOfDatabaseAccess(str_vendor_database,
                                                                                  server,
                                                                                  database)
        
    def set_dividend_calc_method_parameters(self, args_dict):
        self._args_dividend_parameters = args_dict
        self._args_dividend_parameters['database_object'] = self._database_object
    
    def set_securityID(self, ticker):
        try:        
            print("****************************** \n checking security ID... \n ******************************")
            self._securityID = self._database_object.getSecurityIDFromTicker(ticker) # getting secutiry ID
        except:
            print("For ticker "+str(ticker)+", securityID has not been found")
#            raise market_data_error()
    
    def set_dividends(self, securityID, eval_date, str_dividend_method=''):
        print("****************************** \n Dividend calculation... \n ******************************")
                       
        if str_dividend_method == '':
            str_dividend_method = self._dividend_calculation_method
        
        self._dividend_value = Dividend_calculation_methods.dividend_method_builder.get_instance(str_dividend_method).get_dividend_yield(securityID, eval_date, self._args_dividend_parameters)
    
    def set_market_price_list(self, securityID, eval_date):
        try:
            print("****************************** \n Security price list \n ******************************")
            self._market_price_list = self._database_object.pullOptionPricesTable(securityID, eval_date)
            # small adaptions...
#            self._market_price_list['TTM']=self._market_price_list['TTM']/self._daycount # calculate time to maturity in year fraction
            self._market_price_list['CallPutIndex'] = [1 if self._market_price_list.loc[i]['CallPut']=='C' else -1 for i in self._market_price_list.index] # create index for calls and puts
        except:
#            raise market_data_error()
            print('ERROR: market data not found')
# =============================================================================
# END: set methods:        
# ============================================================================= 
    
# =============================================================================
#     Get methods:
# =============================================================================
    def get_discount_factor(self):
        return self._DiscFactor        

    def get_dividend_calc_method(self):
        return self._dividend_calculation_method
    
    def get_dividend_value(self):
        return self._dividend_value
    
    def get_daycount(self):
        return self._daycount
    
    def get_market_price_list(self):
        return self._market_price_list            
    
    def get_implied_vol_list(self):
        return self._implied_vol_market_list   
    
    def get_implied_vol_surface(self):
        return self._implied_vol_surface
    
    def get_securityID(self):
        return self._securityID
    
    def get_pricing_model_obj(self):
        return self._pricing_model
    
    # =============================================================================
    #     ### all other information are made available once this method is run.    
    def get_volatility_surface(self, 
                               ticker, 
                               eval_date, 
                               market_data=[],
                               DiscFactor=None, 
                               IV_listed_from_vendor=False, 
                               IV_surface_from_vendor=False,
                               dividend_calculation_method = '',
                               dividend_parameters={'dividend_list' : 0,
                                                    'spot' : 0}):        
        self._IV_listed_from_vendor = IV_listed_from_vendor # get implied volatility listed from vendor database 
        
        if (self.check_requisites()): 
#            try:
            self.set_discount_factor(eval_date, DiscFactor)
            self.set_securityID(ticker)
            self.set_dividend_calc_method_parameters(dividend_parameters)            
            if (len(market_data) > 0):
#                print('use of provided market data')
                self._market_price_list = market_data                
            else:
                self.set_market_price_list(self._securityID, eval_date)
                
            self.set_dividends(self._securityID, eval_date, dividend_calculation_method)

            self._implied_vol_surface = pd.DataFrame(columns = ['TTM', 'Delta', 'CallPut'])
            # =============================================================================
            ## if we use volatility surface directly from vendor
            # =============================================================================
            if (IV_surface_from_vendor): 
                
                print("****************************** \n Volatility surface fitting \n ******************************")
                # data preparation:
                implied_vol_surface_obj = vol_surf.log_normal_vol_surface.get_instance('Vendor', daycount = 360)
                self._implied_vol_surface = implied_vol_surface_obj.generate_volatility_surface(self._securityID, eval_date, self._database_object)
            
            # =============================================================================
            ## if we should extract data and perform vol surface fitting
            # =============================================================================
            else: # 
                print("****************************** \n Calculate implied volatility \n ******************************")
                iVol_obj = ImpliedVolatilityCalculator(self._root_finder_method,
                                                       self._pricing_model_name,
                                                       self._DiscFactor,
                                                       self._dividend_value,
                                                       self._market_price_list,
                                                       eval_date,
                                                       self._min_ttm,
                                                       self._pricer_max_iterations,
                                                       self._root_finder_max_iteration)
                self._implied_vol_market_list = iVol_obj.calculateImpliedVol(from_vendor=self._IV_listed_from_vendor)

                print("****************************** \n Volatility surface fitting \n ******************************")
                # data preparation:
#                implied_vol_surface_obj = vol_surf.log_normal_vol_surface.get_instance('Gaussian_smooth', daycount = 360)
#                try:
                
                
                implied_vol_surface_obj = vol_surf.log_normal_vol_surface.get_instance('Gaussian_smooth', daycount = 360)
                self._implied_vol_surface = implied_vol_surface_obj.generate_volatility_surface(self._implied_vol_market_list)

            # add useful information
            self._implied_vol_surface['Ticker']=ticker
            self._implied_vol_surface['SecurityID']=self._securityID
            self.aggregate_implied_strike()
            
            # returning volatility surface results
            return self._implied_vol_surface

        else:
            return False
        # =============================================================================
        
# =============================================================================
#     END: Get methods
# =============================================================================
# =============================================================================
#     standard for basic argument array:
#     args[0] =                # 1 for a Call, - 1 for a put
#     args[1] =                 # Underlying asset price
#     args[2] =                 # Option strike K
#     args[3] =                 # Continuous risk fee rate
#     args[4] =                 # Dividend continuous rate
#     args[5] =                 # time to expiry
#     args[6] =             # Underlying volatility
#     args[7] =             # number of steps binomial tree
# =============================================================================
    def auxiliar_extract_implied_strike(self, strike, args, model, delta):        
        args[2] = strike

        value = (model.get_calc(args, str_result='Delta'))# - delta)
        if (np.isnan(value)):
            value = 10
        return (value - delta)#**2
        
    
    def aggregate_implied_strike(self):

        
        self._pricing_model = PricingModel.model_factory(self._pricing_model_name)
        
        ZC_curve = interp1d(self._DiscFactor['TTM'], self._DiscFactor['Rate'], kind='linear', fill_value='extrapolate')
        
        self._implied_vol_surface['ImpliedStrike']=0.0
        

        for i in self._implied_vol_surface.index:


            if self._implied_vol_surface.loc[i]['CallPut']=='C':
                CallPutIndex = 1
            else:
                CallPutIndex = -1
            args = [CallPutIndex, 
                    self._implied_vol_surface.loc[i]['Spot'], 
                    0.0, 
                    ZC_curve(self._implied_vol_surface.loc[i]['TTM']),
                    self._dividend_value, 
                    self._implied_vol_surface.loc[i]['TTM']/self._daycount, 
                    self._implied_vol_surface.loc[i]['ImpliedVol']]
            
            
            #try:
            #a=1
            #b=np.max(self._market_price_list['Strike'])
            #ImpliedStrike = scipy.optimize.ridder(f = self.auxiliar_extract_implied_strike,
            #                                      a=a,
            #                                      b=b,
            #                                      args=(args, self._pricing_model, 
            #                                            self._implied_vol_surface.loc[i]['Delta']/100))
            #except:
             #   ImpliedStrike = 0.0
#            print('ImpliedStrike: '+str(ImpliedStrike))
#            print('fval: '+str(fval))
#            print('iterations: '+str(iterations))
#            print('funcalls: '+str(funcalls))
            #self._implied_vol_surface.loc[i, 'ImpliedStrike'] = ImpliedStrike

    def check_requisites(self):
        '''Before calculation, check requisites'''
        if (self._database_object.isConnected):
            if(implied_vol_root_finder.check_method(self._root_finder_method) or (self._IV_listed_from_vendor)): # check if root finder method exists
                pass
                # if....    #ToDo?
        else:
            return False
        return True
