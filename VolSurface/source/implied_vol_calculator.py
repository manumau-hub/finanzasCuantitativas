# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 11:46:25 2019

@author: dpedroso
"""

# lets be rational code
# Documentation: http://www.vollib.org/documentation/python/1.0.2/apidoc/py_vollib.black_scholes_merton.html
import py_vollib.black_scholes_merton.implied_volatility as jakel

from scipy.interpolate import interp1d # interpolation method
from pricingmodel import PricingModel,PricingArguments
import numpy as np
import pandas as pd
import scipy.optimize
from collections import namedtuple

from benchmarking import timeit
from joblib import Parallel, delayed


class ImpliedVolatilityCalculator:
    def __init__(self, method_name, # root finder method,
                 model_name, # pricing model
                 df_ZC, # zero coupon rate curve. It must contain at least: ['Days'] ['Rate']
                 div, # dividend yield
                 option_price_list, # option market data (dataframe)
                 date, # evaluation date
                 min_ttm = 0, # minimum time to maturity [year fraction]
                 root_finder_max_iter = 50,             # maximum iterations for bisection or newton
                 pricing_model_max_iter = 500):   # maximum iterations for pricing models
    
        self.eval_date=pd.Timestamp(date)
        self._root_finder=implied_vol_root_finder() # composition with class implied_vol_root_finder
        self.set_root_finder(method_name)
        self.set_pricing_model(model_name)
        
        self.set_ZC_curve(df_ZC)
        self.set_dividend_curve(div)
        self.set_market_option_dataframe(option_price_list)
        self.set_min_time2maturity(min_ttm)
        self.set_pricing_model_max_iterations(pricing_model_max_iter)
        self.set_root_finder_max_iterations(root_finder_max_iter)
        
    
# =============================================================================
#     set / get methods
# =============================================================================    
    def set_pricing_model_max_iterations(self, num_iteration_model):
        self._pricing_model_max_iter = num_iteration_model
        
    def set_root_finder_max_iterations(self, num_iteration_root_finder):
        self._root_finder_max_iter = num_iteration_root_finder
    
    def set_min_time2maturity(self, min_ttm=0):
        self._min_ttm = min_ttm
        
    def set_root_finder(self, method_name):
        self._root_finder_method = method_name #[jakel, newton, bisection]
    
    def set_pricing_model(self,model_name):
        self._pricing_model = model_name #[BS, LR, CRR, Trinomial, QL_Ame, QL_Eur]
    
    def set_ZC_curve(self, df_ZC, fitting='linear', fill_value="extrapolate"):
        df_ZC.sort_values(['Inyears'], inplace=True)
        self._ZC_curve = interp1d(df_ZC['Inyears'], df_ZC['Quote'], kind='linear', fill_value='extrapolate')
        
    def set_dividend_curve(self, div):
        self._dividend = div
    
    def set_market_option_dataframe(self, option_price_list):
        self._market_data = option_price_list
        self._market_data['CallPutIndex'] = [1 if self._market_data.loc[i]['CallPut']=='C' else -1 for i in self._market_data.index]        
       
# =============================================================================
        
    def functionForParallel(self, i):
        MarketdataRow = namedtuple('MarketdataRow', self._market_data.columns)
        data=MarketdataRow(*self._market_data.loc[i].values)

        #Treated as American ONLY if Put and dividens>0!!
        #           if (df['CallPut'].values[i]=='P') and (df['ExerciseStyle'].values[i]=='A'): # in case of american....
        #            self._pricing_model = 'LR' # ... we will use LR binomial tree
        #            self._pricing_model = 'QL_Ame' # ... we will use LR binomial tree
        #            self._pricing_model = 'Trinomial' # ... we will use LR binomial tree
        #
        #            self.set_root_finder('bisection')
        #        else:
        #            self._pricing_model = 'BlackScholes' # for European only or american  with div=0
        #            self.set_root_finder('jakel')
        #       self.set_root_finder(method_name)

        #       self.set_pricing_model(model_name)

        self._model = PricingModel.model_factory(self._pricing_model)  # getting price model instance
        pricing_max_iteration_temp = self._pricing_model_max_iter

        # #If abs(moneyness)>>1 increase the max_iterations of pricing model
        # if ((df.loc[i]['Spot'] / df.loc[i]['Strike'] > 1.3) or (df.loc[i]['Spot'] / df.loc[i]['Strike'] < 0.7)):
        #     pricing_max_iteration_temp = self._pricing_max_iteration * 10 #FACTOR
        # else:
        #     pricing_max_iteration_temp = self._pricing_max_iteration #FACTOR

        zRate = self._ZC_curve(data.YearFraction)
        # checking if price is below intrinsic value
        correctedPrice = data.AveragePrice*np.exp(zRate*data.YearFraction)

        intrinsicValue = self._model.intrinsicValue
        isbelowintrinsic=correctedPrice < intrinsicValue

        args=PricingArguments(
            putCall =PricingArguments.OptionType.CALL if data.CallPutIndex==1 else PricingArguments.OptionType.PUT,
            underlyingPrice =data.Spot,
            strike =data.Strike,
            riskFreeRate =zRate,
            dividendRate =self._dividend,
            timeToExpiry =data.YearFraction,
            volatility =0.5,    #Just for the initial guess
            )

        #check if below intrinsic and time to maturity above minimum
        #ToDo: Does it make sense to filter out based on minimum maturity?
        if ((not isbelowintrinsic) and (data.YearFraction >= self._min_ttm)):
            # first guess of IV is obtained using calculations assuming european exercise
            IV_init = self._root_finder.get_implied_vol(args, data.AveragePrice, 'jakel', self._model)
            if data.ExerciseStyle=='A': # if american, the number of iterations should be provided...
                if self._pricing_model in ['LR', 'CRR', 'Trinomial']:
                    args.volatility=IV_init
                    args.nIterations=pricing_max_iteration_temp
                elif self._pricing_model == 'QL_Ame':
                    try:
                        start_date = data.Date.strftime("%Y-%m-%d")
                    except:
                        start_date = data.Date

                    try:
                        maturity_date = data.Expiration.strftime("%Y-%m-%d")
                    except:
                        maturity_date = data.Expiration
                    args.QLStartDate=start_date
                    args.QLEndDate=maturity_date

            # here get the implied volatility...
            IV = self._root_finder.get_implied_vol(args, data.AveragePrice, self._root_finder_method, self._model, max_iter=self._root_finder_max_iter)
            args.volatility=IV

            # vega:
            vega = self._model.get_calc(args, 'Vega') if IV!=0 else -99.99
            if self._pricing_model == 'BlackScholes':
                vega *= 100

            delta = self._model.get_calc(args,'Delta') if IV!=0 else -99.99
            # ... and fill the dataframe row
            output_vector = (data.Date, data.Expiration, data.TTM, data.YearFraction,
                             data.CallPut, data.ExerciseStyle, data.Strike, IV, data.AveragePrice,
                             data.Spot, vega, delta)
            return output_vector
        
    
    def calculateImpliedVol(self, from_vendor=False):
        #ToDo:This should be polymorphic, infering if from_vendor or not
        if (from_vendor):
            return self.getImpliedVolTableFromVendor()
        else:
            return self.getImpliedVolTable()

    def getImpliedVolTable(self):
        df = self._market_data # simplifying....

        output_data = Parallel(n_jobs = -1)(delayed(ImpliedVolatilityCalculator.functionForParallel)(self, i) for i in df.index)
        IVTable=pd.DataFrame([x for x in output_data if x], columns=(
        'Date', 'Expiration', 'TTM', 'YearFraction', 'CallPut', 'ExerciseStyle', 'Strike', 'ImpliedVol', 'OptionPrice',
        'Spot', 'Vega', 'Delta'))
        #IVTable = pd.DataFrame(index=np.arange(0, len(df.index)), columns=('Date', 'Expiration','TTM', 'YearFraction','CallPut', 'ExerciseStyle', 'Strike','ImpliedVol', 'OptionPrice', 'Spot', 'Vega','Delta')) # empty dataframe
        # for i in np.arange(0, len(df.index)):
        #     IVTable.loc[i] = output_data[i]
        
        # IVTable = IVTable.dropna() # drop errors...........
        # IVTable = IVTable.drop(IVTable[IVTable['ImpliedVol'] == 0.0].index) # drop zero values as well.
        # IVTable['Date'] = df['Date'].value_counts().keys().tolist()[0]
        # IVTable['YearFraction'] = df['YearFraction']
        #IVTable = IVTable.drop_duplicates(['TTM', 'CallPut', 'Strike', 'OptionPrice'])
        
        return IVTable
    
    def getImpliedVolTableFromVendor(self):
        
        df = self._market_data # simplifying....
        IVTable = pd.DataFrame(index=np.arange(0, len(df.index)), columns=('Date','Expiration','TTM', 'CallPut', 'Strike','ImpliedVol', 'OptionPrice', 'Spot', 'Vega','Delta')) # empty dataframe

        IVTable['TTM'] = df['TTM']
        IVTable['CallPut'] = df['CallPut']
        IVTable['Strike'] = df['Strike']
        IVTable['ImpliedVol'] = df['DBImpVol']
        IVTable['OptionPrice'] = df['AveragePrice']
        IVTable['Spot'] = df['Spot']
        IVTable['Vega'] = df['DBVega']
        IVTable['Delta'] = df['DBDelta']
                
        #IVTable = IVTable.dropna() # drop errors...........
        #IVTable = IVTable.drop(IVTable[IVTable['ImpliedVol'] == 0.0].index) # drop zero values as well.
        
        IVTable['Date'] = df['Date'].value_counts().keys().tolist()[0]
        IVTable['Expiration'] = df['Expiration']
                        
        #Not necessary to remove for debugging
        #IVTable = IVTable[(IVTable !=-99.98999786376953).all(1)]      #ToDo: Filter out failed values???
        #removed index duplicates. Check OptionPrice filter
        IVTable = IVTable.drop_duplicates(['TTM', 'CallPut', 'Strike', 'OptionPrice'])
        
        
        return IVTable
    
class implied_vol_root_finder:
    method_list = ['bisection', 'newton', 'jakel', 'brent', 'brentq', 'toms748', 'ridder']
    @staticmethod
    def check_method(str_method):       
        for method in implied_vol_root_finder.method_list:
             if (str_method == method):
                 return True

    def methodName(self):
        raise Exception("root finder name not implemented")

# =============================================================================
#     args for pricing models
#     standard for basic argument array:
#     args[0] =                # 1 for a Call, - 1 for a put
#     args[1] =                 # Underlying asset price
#     args[2] =                 # Option strike K
#     args[3] =                 # Continuous risk fee rate
#     args[4] =                 # Dividend continuous rate
#     args[5] =                 # time to expiry
#     args[6] =                 # Underlying volatility
# =============================================================================
    def get_implied_vol(self,args,      #model arguments vector
                        market_price,        # market optin price
                        method='', # root finder method
                        model='',             # an instance of class derived from PricingModel class
                        init_sigma=0.5,      # initial implied vol guess (newton method)
                        higher_limit=5,      # inner max implied vol (bisection method)
                        lower_limit=1E-4,       # inner min implied vol (bisection method)
                        price_tolerance = 1E-6,    #  absolute price tolerance
                        vol_tolerance = 1E-6,    # absolute volatility tolerance
                        max_iter = 500): # maximum iterations with bisection and newton
        if method=='bisection':
            return bisection_method().calc(model, args,market_price,higher_limit,lower_limit,price_tolerance,vol_tolerance,max_iter)
        elif method=='newton':
            return newton_method().calc(model,args,market_price,init_sigma,vol_tolerance,max_iter)
        elif method=='jakel':
            return jakel_method().calc(args, market_price)
        elif method=='brent':
            return brent_method().calc(model, args, market_price, vol_tolerance, max_iter)
        elif method=='brentq':
            return brentq_method().calc(model, args, market_price, lower_limit, higher_limit, vol_tolerance, max_iter)
        elif method=='toms748':
            return toms748_method().calc(model, args, market_price, lower_limit, higher_limit,vol_tolerance, max_iter)
        elif method=='ridder':
            return ridder_method().calc(model, args, market_price, lower_limit, higher_limit,vol_tolerance, max_iter)
        
class bisection_method(implied_vol_root_finder):

    def methodName(self):
        return 'bisection'

    def calc(self, model,             # an instance of class derived from PricingModel class
                   args,                #model arguments vector
                   market_price,        # market optin price
                   higher_limit=8,      # inner max implied vol
                   lower_limit=1E-8,       # inner min implied vol
                   price_tolerance = 1E-5,    #  absolute price tolerance
                   vol_tolerance = 1E-6,    # absolute volatility tolerance
                   max_iter = 50):   # max method iterations
        H = higher_limit
        L = lower_limit
        model_premium = 2*market_price
        iterationCount = 0

        while ((np.abs(model_premium - market_price) > price_tolerance) and (np.abs(H-L) > vol_tolerance) and (iterationCount <= max_iter)):
            sigma=(H+L)/2
            model_premium = model.get_calc(args, sigma=sigma)
# =============================================================================
#           # Handle case where model pricing throws NaN
            if np.isnan(model_premium):
                maxRetriesBeforeThrowingNaN=1
                inner_count = 0
                while(np.isnan(model_premium) and inner_count <= maxRetriesBeforeThrowingNaN):
                    possibleSigma=sigma+np.random.uniform(-1,1)*(H-L)/2
                    model_premium = model.get_calc(args, sigma=possibleSigma)
                    inner_count = inner_count+1

                if (possibleSigma > sigma):
                    L = sigma
                else:
                    H = sigma
                if inner_count > maxRetriesBeforeThrowingNaN:
                    return 0.0      #ToDo: This is one of the cases to mark: Failed to converge
# =============================================================================
            if model_premium > market_price:
                H = (H + L) / 2
            else:
                L = (H + L) / 2
            iterationCount = iterationCount + 1

        #If out of main while loop then it converged or reached max iterations
        if iterationCount < max_iter:
            sigma = (H + L) / 2
            if ((sigma>=(lower_limit+vol_tolerance)) and (sigma <= (higher_limit-vol_tolerance))):
                return sigma
            else:
                return 0.0  #ToDo: This is one of the cases to mark: Exceeded volatility thresholds
        else:
            return 0.0  #ToDo: This is one of the cases to mark: Max iterations reached

class newton_method(implied_vol_root_finder):
    
    def methodName(self):
        return 'newton'
        
    def function_to_optimize(self, sigma, args, model, market_price):                
        return (model.get_calc(args, sigma=sigma) - market_price)**2
        
    
    def calc(self, model, args, market_price, sigma_init, tol=1.48e-08, maxiter=500):          
        try:
            IV = scipy.optimize.newton(func = self.function_to_optimize, x0 = sigma_init, args=(args, model, market_price),full_output=True, tol=tol, maxiter=maxiter)[0]
        except:
            IV = 0.0

        return IV
    

class jakel_method(implied_vol_root_finder):
    
    def methodName(self):
        return 'jakel'
    
    def calc(self, args, market_price):
        try:
            IV=jakel.implied_volatility(market_price, args.underlyingPrice,args.strike,
                                        args.timeToExpiry, args.riskFreeRate,args.dividendRate,
                                        'c' if args.putCall==PricingArguments.OptionType.CALL else 'p')
        except:
            IV=0.0
        return IV
        
# =============================================================================
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brent.html
# =============================================================================
class brent_method(implied_vol_root_finder):
    def methodName(self):
        return 'brent'
        
    def function_to_optimize(self, sigma, args, model, market_price):                
        return (model.get_calc(args, sigma=sigma) - market_price)**2

    def calc(self, model, args, market_price, tol=1.48e-08, maxiter=500):          
        try:
            IV, fval, iterations, funcalls = scipy.optimize.brent(func = self.function_to_optimize, args=(args, model, market_price),full_output=True, tol=tol, maxiter=maxiter)            
        except:
            IV = 0.0
        return IV


class brentq_method(implied_vol_root_finder):
    def methodName(self):
        return 'brentq'
        
    def function_to_optimize(self, sigma, args, model, market_price):                
        return (model.get_calc(args, sigma=sigma) - market_price)**2
        
    
    def calc(self, model, args, market_price, lower_limit, higher_limit, tol=1.48e-08, maxiter=500): 
        try:
            IV, r = scipy.optimize.brentq(f = self.function_to_optimize, a = lower_limit, b = higher_limit, args=(args, model, market_price), xtol=tol, maxiter=maxiter)            
        except:
            IV = 0.0
        return IV


# =============================================================================
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.toms748.html#scipy.optimize.toms748
# =============================================================================
class toms748_method(implied_vol_root_finder):
    def methodName(self):
        return 'toms748'
        
    def function_to_optimize(self, sigma, args, model, market_price):                
        return (market_price - model.get_calc(args, sigma=sigma))#**2
    
    def calc(self, model, args, market_price, lower_limit, higher_limit,tol=1.48e-08, max_iter=100):
        try:
            IV = scipy.optimize.toms748(f = self.function_to_optimize,a=lower_limit, b=higher_limit, args=(args, model, market_price), maxiter=max_iter,xtol=tol, full_output=False)
        except:
            IV = 0.0
        return IV


# =============================================================================
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.ridder.html#scipy.optimize.ridder
# =============================================================================
class ridder_method(implied_vol_root_finder):
    
    def methodName(self):
        return 'ridder'
        
    def function_to_optimize(self, sigma, args, model, market_price):  
        return (market_price - model.get_calc(args, sigma=sigma))#**2
    
    def calc(self, model, args, market_price, lower_limit, higher_limit,tol=1.48e-08, max_iter=100):
        try:                        
            IV = scipy.optimize.ridder(f = self.function_to_optimize,a=lower_limit, b=higher_limit, args=(args, model, market_price), maxiter=max_iter, xtol=tol, full_output=False)
        except:
            IV = 0.0
        return IV