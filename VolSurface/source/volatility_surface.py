# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 13:27:00 2019

@author: dpedroso
"""

import numpy as np
import pandas as pd
from itertools import product
from scipy.interpolate import interp1d
from joblib import Parallel, delayed

class log_normal_vol_surface:

    def __init__(self,
                 daycount = 360): # day count convention
        self._daycount = daycount
        self.define_std_ttm_list_days()
        self.define_std_delta_strike()
        
    @staticmethod
    def get_instance(str_vol_surf_method, daycount = 360):        
        child_dictionary={'Vendor' : from_vendor,
                         'Gaussian_smooth' : gaussian_smooth,
                         'SVI' : stochastic_volatility_inspired,#not implemented
                         'Cubic Spline' : cubic_spline}#not implemented
        return child_dictionary[str_vol_surf_method](daycount)
              
# =============================================================================
#     set / get methods
# =============================================================================
    def set_daycount_convention(self, daycount):
        self._daycount = daycount
    
    def get_daycount_convention(self, daycount):
        return self._daycount
    
    def get_class_name(self):
        return 'log_normal_vol_surface'
    
# =============================================================================
#     Standard definitions
# =============================================================================
    def define_std_ttm_list_days(self, std_ttm=np.array([30, 60, 91, 122, 152, 182, 273, 365, 547, 730])):
        self._std_ttm_days = std_ttm
        self._std_ttm_year_fraction = std_ttm / self._daycount
    
    def define_std_ttm_list_year_fraction(self, std_ttm=np.array([0.08242, 0.16484, 0.25, 0.3352, 0.4176, 0.5, 0.75, 1, 1.5, 2])):        
        self._std_ttm_year_fraction = std_ttm
        self._std_ttm_days = std_ttm * self._daycount
        
    def define_std_delta_strike(self, std_delta=np.arange(0.2,0.8,0.05)):
        self._std_delta = std_delta
        
# =============================================================================
#   Utils:
# =============================================================================
    # protected method:
    def _implied_strike_from_delta(self, r,cp, delta, spot, q, ttm, ivol):        
        return spot * np.exp(-( norm.ppf(delta) * ivol * np.sqrt(ttm/self._daycount) + (r-q + np.power(ivol,2)/2) * ttm/self._daycount))        
        
class cubic_spline(log_normal_vol_surface):
    def get_class_name(self):
        return 'cubic_spline'
    

    def generate_volatility_surface(self, df_raw_IV_data):       
        
        std_ttms = self._std_ttm_days    
        std_deltas=self._std_delta    
        df_vol_surface_1 = pd.DataFrame(list(product(std_ttms, std_deltas, ['C'])), columns = ['TTM', 'Delta', 'CallPut'])
        df_vol_surface_2 = pd.DataFrame(list(product(std_ttms, np.sort(self._std_delta*-1), ['P'])), columns = ['TTM', 'Delta', 'CallPut'])
        df_output = pd.concat([df_vol_surface_1, df_vol_surface_2])
        df_output = df_output.sort_values(['TTM','Delta','CallPut'])
        df_output = df_output.reset_index(drop=True)        
        df_raw_sorted=df_raw_IV_data.sort_values('Delta')        

        for ttm in df_raw_sorted['TTM'].value_counts().keys().tolist():
            delta = np.array(df_raw_sorted[df_raw_sorted['TTM']==ttm]['Delta'], dtype=float)
            IV = np.array(df_raw_sorted[df_raw_sorted['TTM']==ttm]['ImpliedVol'], dtype = float)
            CS = interp1d(delta, IV, kind='cubic')
# =============================================================================
#             TODO: it works, but still needs to test functionality. Some odd behaviours still pops up.
# =============================================================================
            df_output[df_output['TTM']==ttm]['ImpliedVol'] = CS(self._std_delta)
            
        
        return df_output

class from_vendor(log_normal_vol_surface):
    
    def get_class_name(self):
        return 'log_normal_vol_surface_from_vendor'
    
    def generate_volatility_surface(self, securityID, date, database_object):
        vendor_imp_vol = database_object.pullVolatilitySurfaceOfSecurityID(securityID, date)
        # adjustments.....:
        vendor_imp_vol['TTM'] = vendor_imp_vol['Days']/self._daycount
        vendor_imp_vol.rename(columns={'ImpliedVolatility' : 'ImpliedVol'}, inplace=True)
        return vendor_imp_vol

class gaussian_smooth(log_normal_vol_surface):
        
    def get_class_name(self):
        return 'log_normal_vol_surface_gaussian_smooth'
       
    def aux_parallel_function(self, df_vol_surface, df_raw_IV_data, j):
        num = 0
        denom = 0
        dnum = 0
        h1 = 0.05
        h2 = 0.005
        h3 = 0.001
        for i in range(0, len(df_raw_IV_data.index)):
            #Code for x
            x = np.log(df_raw_IV_data.loc[:,"YearFraction"].values[i]/df_vol_surface.loc[:,"YearFraction"].values[j])
            
            #Code for y and z / CALL EQUIVALENT DELTA
            if df_raw_IV_data.loc[:,"CallPut"].values[i] == 'C':
                di = df_raw_IV_data.loc[:,"Delta"].values[i]
                if df_vol_surface.loc[:,"CallPut"].values[j] == 'C':
                    dj = df_vol_surface.loc[:,"Delta"].values[j]
                    z = 0
                else:
                    dj = df_vol_surface.loc[:,"Delta"].values[j]+1
                    z = 1
            else:
                di = df_raw_IV_data.loc[:,"Delta"].values[i]+1
                if df_vol_surface.loc[:,"CallPut"].values[j] == 'C':
                    dj = df_vol_surface.loc[:,"Delta"].values[j]
                    z = 1
                else:
                    dj = df_vol_surface.loc[:,"Delta"].values[j]+1
                    z = 0
            
            y = di - dj
            
            # 1/np.sqrt(2*pi) *
            phi =  np.exp(-x*x/(2*h1) - y*y/(2*h2) - z*z/(2*h3))
        
            
            num = num + df_raw_IV_data.loc[:,"Vega"].values[i] * df_raw_IV_data.loc[:,"ImpliedVol"].values[i] * phi
            dnum = dnum + df_raw_IV_data.loc[:,"Vega"].values[i] * df_raw_IV_data.loc[:,"ImpliedVol"].values[i] * df_raw_IV_data.loc[:,"ImpliedVol"].values[i] * phi
            denom = denom + df_raw_IV_data.loc[:,"Vega"].values[i] * phi
                    
        smooth_ivols = (num/denom)        
        dispersions = (np.sqrt(dnum/denom - np.power(smooth_ivols,2)))
        output_vector = [smooth_ivols, dispersions]
        return output_vector

# =============================================================================
#     Input:
#         df_raw_IV_data:
#             'Date', 'TTM', 'CallPut', 'Strike','ImpliedVol', 'OptionPrice', 'Spot', 'Vega', 'Delta' 
#                TTM = time to maturity in year fraction
#                CallPut = C, P
#     Output:
#         'Date', 'TTM', 'DeltaStrikes', 'CallPut', 'ImpliedVol', 'Dispersion'
# =============================================================================
    def generate_volatility_surface(self, df_raw_IV_data, vega_min = 0.5, ttm_min = 10):       
        #Generate Standarized dataframe 
        std_ttms = self._std_ttm_days    
        std_deltas=self._std_delta    
        df_vol_surface_1 = pd.DataFrame(list(product(std_ttms, std_deltas, ['C'])), columns = ['TTM', 'Delta', 'CallPut'])
        df_vol_surface_2 = pd.DataFrame(list(product(std_ttms, np.sort(self._std_delta*-1), ['P'])), columns = ['TTM', 'Delta', 'CallPut'])
        df_vol_surface = pd.concat([df_vol_surface_1, df_vol_surface_2])
        df_vol_surface = df_vol_surface.sort_values(['TTM','Delta','CallPut'])
        df_vol_surface = df_vol_surface.reset_index(drop=True)
        smooth_ivols = [0]*len(df_vol_surface.index)
        dispersions =[0]*len(df_vol_surface.index)
        
        
        year_fractions = [0.082192, 0.164384, 0.249315, 0.334247, 0.416438, 0.49863, 0.747945, 1.0, 1.49863, 2]
        ttms = [30, 60, 91, 122, 152, 182, 273, 365, 547, 730]
        
        df_vol_surface['YearFraction'] = 0.0

# =============================================================================
#         FILTER vega < 0.5
# =============================================================================
        df_raw_IV_data = df_raw_IV_data[df_raw_IV_data.Vega >= vega_min]
# =============================================================================
#         FILTER TTM < 10
# =============================================================================
        
        df_raw_IV_data = df_raw_IV_data[df_raw_IV_data.TTM > ttm_min]
        
        
        for j in range(0, len(df_vol_surface.index)):#np.size(ivols)):
            temp = df_vol_surface['TTM'].values[j]
            ind = ttms.index(temp)
            df_vol_surface['YearFraction'].values[j] = year_fractions[ind]
                
        output_data = Parallel(n_jobs = 1)(delayed(gaussian_smooth.aux_parallel_function)(self,df_vol_surface,df_raw_IV_data,j) for j in range(0, len(df_vol_surface.index)))
           
                        
        smooth_ivols = [output_data[i][0] for i in np.arange(0, len(output_data))]        
        dispersions = [output_data[i][1] for i in np.arange(0, len(output_data))]

            
        df_vol_surface['Date'] = df_raw_IV_data['Date'].value_counts().keys().tolist()[0] # get evaluation date
        df_vol_surface['ImpliedVol'] = smooth_ivols
        df_vol_surface['Dispersion'] = dispersions
                
        #Standard Delta as in IvyDB
        df_vol_surface['Delta'] = round(df_vol_surface['Delta']*100,0)
        
        # get time to maturity in year fraction
        df_vol_surface['Days'] = df_vol_surface['TTM']
        #df_vol_surface['TTM'] = df_vol_surface['TTM']/self._daycount
        
        #get utils
        df_vol_surface['ExerciseStyle'] = df_raw_IV_data['ExerciseStyle'].value_counts().keys().tolist()[0]
        df_vol_surface['Spot'] = df_raw_IV_data['Spot'].value_counts().keys().tolist()[0]
    
        return df_vol_surface
    
    
    
    def generate_volatility_surface_point(self, df_raw_IV_data, Type = 'C', Days = 30, Delta = 20):       
        
        
# =============================================================================
#         FILTER vega < 0.5
# =============================================================================
        df_raw_IV_data = df_raw_IV_data[df_raw_IV_data.Vega>=0.5]
        
        num = 0
        denom = 0
        dnum = 0
        h1 = 0.05
        h2 = 0.005
        h3 = 0.001
        for i in range(0, len(df_raw_IV_data.index)):
            x = np.log(df_raw_IV_data.loc[:,"TTM"].values[i]/Days)
            #Code for y and z / CALL EQUIVALENT DELTA
            if df_raw_IV_data.loc[:,"CallPut"].values[i] == 'C':
                di = df_raw_IV_data.loc[:,"Delta"].values[i]
                if Type == 'C':
                    dj = Delta/100.0
                    z = 0
                else:
                    dj = Delta/100.0+1
                    z = 1
            else:
                di = df_raw_IV_data.loc[:,"Delta"].values[i]+1
                if Type == 'C':
                    dj = Delta/100.0
                    z = 1
                else:
                    dj = Delta/100.0+1
                    z = 0
            
            y = di - dj
            
            phi =  np.exp(-x*x/(2*h1) - y*y/(2*h2) - z*z/(2*h3))
            
            num = num + df_raw_IV_data.loc[:,"Vega"].values[i] * df_raw_IV_data.loc[:,"ImpliedVol"].values[i] * phi
            dnum = dnum + df_raw_IV_data.loc[:,"Vega"].values[i] * df_raw_IV_data.loc[:,"ImpliedVol"].values[i] * df_raw_IV_data.loc[:,"ImpliedVol"].values[i] * phi
            denom = denom + df_raw_IV_data.loc[:,"Vega"].values[i] * phi
                    
        impl_vol = (num/denom)        
        
              
        return impl_vol
    
    
    
class stochastic_volatility_inspired(log_normal_vol_surface):
    def get_class_name(self):
        return 'SVI'
    

    def generate_volatility_surface(self, df_raw_IV_data):       
           
        return df_raw_IV_data
