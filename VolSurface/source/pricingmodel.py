# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:32:20 2019

@author: dpedroso
"""

from scipy.stats import norm
import numpy as np
import QuantLib as ql
import math
import warnings
from enum import Enum

class PricingArguments:
    def __init__(self,*args,**kwargs):
        propertyMembers = [p for p in dir(PricingArguments) if isinstance(getattr(PricingArguments, p), property)]
        # Empty initialization first
        for propMember in propertyMembers:
            setattr(self, propMember, None)

        if args:
            for i,arg in enumerate(args):
                setattr(self,propertyMembers[i],arg)    #This kind of initialization doesn't make much sense
        elif kwargs:
            for kwarg,value in kwargs.items():
                setattr(self, kwarg, value)

    class OptionType(Enum):
        CALL=1
        PUT=2

    def __str__(self):
        propertyMembers = [p for p in dir(PricingArguments) if isinstance(getattr(PricingArguments, p), property)]
        propDict={propName:getattr(self,propName) for propName in propertyMembers}
        return str(propDict)

    @property
    def putCall(self):
        return self._putCall

    @putCall.setter
    def putCall(self,x):
        self._putCall=x

    @property
    def underlyingPrice(self):
        return self._underlyingPrice

    @underlyingPrice.setter
    def underlyingPrice(self, x):
        self._underlyingPrice = x

    @property
    def strike(self):
        return self._strike

    @strike.setter
    def strike(self, x):
        self._strike = x

    @property
    def riskFreeRate(self):
        return self._riskFreeRate

    @riskFreeRate.setter
    def riskFreeRate(self, x):
        self._riskFreeRate = x

    @property
    def dividendRate(self):
        return self._dividendRate

    @dividendRate.setter
    def dividendRate(self, x):
        self._dividendRate = x

    @property
    def timeToExpiry(self):
        return self._timeToExpiry

    @timeToExpiry.setter
    def timeToExpiry(self, x):
        self._timeToExpiry = x

    @property
    def volatility(self):
        return self._volatility

    @volatility.setter
    def volatility(self, x):
        self._volatility = x

    @property
    def nIterations(self):
        return self._nIterations

    @nIterations.setter
    def nIterations(self, x):
        self._nIterations = x

    @property
    def QLStartDate(self):
        return self._QLStartDate

    @QLStartDate.setter
    def QLStartDate(self, x):
        self._QLStartDate = x

    @property
    def QLEndDate(self):
        return self._QLEndDate

    @QLEndDate.setter
    def QLEndDate(self, x):
        self._QLEndDate = x

    @property
    def daysPerYear(self):
        return self._daysPerYear

    @daysPerYear.setter
    def daysPerYear(self, x):
        self._daysPerYear = x

# =============================================================================
# This class abstracts the creation of pricing models. Models such as Black-Scholes
# binomial tree and any other are derived from this class
# =============================================================================
class PricingModel:
    @staticmethod
    def model_factory(str_model, args=None):
        model_dictionary={
                        'BlackScholes' : BSMerton,
                        'LR' : LR,
                        'CRR': CRR,
                        'QL_Eur': QL_Eur,
                        'QL_Ame': QL_Ame,
                        'Trinomial':TrinomialTree
        }
        return model_dictionary[str_model](args)

    def __init__(self, args):
        self.set_variables(args)

    # this function should be overriden by the derived classes
    def set_variables(self, args):
        pass

    @property
    def intrinsicValue(self):
        if self.Type==PricingArguments.OptionType.CALL:
            return self.S - self.K
        elif self.Type==PricingArguments.OptionType.PUT:
            return self.K -self.S
        return 0

    @property
    def signForOptionType(self):
        if self.Type==PricingArguments.OptionType.CALL:
            return 1
        elif self.Type==PricingArguments.OptionType.PUT:
            return -1
        return 0

    @property
    def d1(self):
        return (np.log(self.S / self.K) + (self.r - self.q + 0.5 * (self.sigma ** 2)) * self.T) / self.sigmaT

    @property
    def d2(self):
        return self.d1 - self.sigma * (self.T ** 0.5)

    # this function creates a switchacse-like structure to get the return from 
    # different methods available in the class to handle premium and greek calculation
    def get_calc(self, args, str_result='Premium', sigma=None):
        if sigma:
            args.volatility=sigma
        
        self.set_variables(args)
        self.get_results= {
                            'Premium' : self.premium,
                            'Delta' : self.delta,
                            'Theta' : self.theta,
                            'Rho' : self.rho,
                            'Vega' : self.vega,
                            'Gamma' : self.gamma,
                            'Phi' : self.phi,
                            'Charm' : self.charm,
                            'Vanna' : self.vanna
                            }
        methodRequested=self.get_results[str_result]
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                result=methodRequested()
            except Exception as e:
                print("\nException calculating {0}. Current variables:\n".format(str_result))
                print(str(args))
                print(str(e))
                result=np.nan
        return result
            
    # generic empty functions to be overriden by the derived classes
    def premium(self, S=None, sigma=None):
        return 0.0
    
    # vega will be finite difference unless it is overriden by a derived class
    def vega(self, sigma=None):
        sigma=sigma or self.sigma
        sigma_iii = sigma + 0.01
        sigma_i = sigma - 0.01
        
        C_i = self.premium(sigma=sigma_i)
        C_iii = self.premium(sigma=sigma_iii)
        
        return (C_iii - C_i)/(0.02)
    
    # delta will be finite difference unless it is overriden by a derived class
    def delta(self):
        S_iii = self.S + 0.01
        S_i = self.S - 0.01
        
        C_i = self.premium(S=S_i)
        C_iii = self.premium(S=S_iii)
        
        return (C_iii - C_i)/(0.02)
    
    def theta(self):
        return 0.0
    
    def rho(self):
        return 0.0
    
    def gamma(self):
        S_ii = self.S
        S_iii = self.S + 0.01
        S_i = self.S - 0.01
        
        C_i = self.premium(S=S_i)
        C_ii = self.premium(S=S_ii)
        C_iii = self.premium(S=S_iii)
        
        return (C_iii -2 * C_ii + C_i)/(0.01*0.01)
    
    def phi(self):
        return 0.0
        
    def charm(self):
        return 0.0
    
    def vanna(self):
        return 0.0
    
# =============================================================================
# Class with the calculation of premium and greeks using Black Scholes model
# =============================================================================
class BSMerton(PricingModel):
    def set_variables(self, args):
        try:
            self.Type = args.putCall                # Call or Put
            self.S = args.underlyingPrice           # Underlying asset price
            self.K = args.strike                    # Option strike K
            self.r = args.riskFreeRate              # Continuous risk fee rate
            self.q = args.dividendRate              # Dividend continuous rate
            self.T = args.timeToExpiry              # Time to expiry
            self.sigma = args.volatility            # Underlying volatility
            self.daycount = getattr(args,'daysPerYear',365.25)
        except:
            self.Type = 0  # 1 for a Call, - 1 for a put
            self.S = -99  # Underlying asset price
            self.K = -99  # Option strike K
            self.r = -99  # Continuous risk fee rate
            self.q = -99  # Dividend continuous rate
            self.T = 1  # Time to expiry
            self.sigma = -99  # Underlying volatility
            self.daycount = 365.25

        self.sigmaT = self.sigma * (self.T ** 0.5)    # sigma*T for reusability

    def calculateDcoefficients(self, S=None, sigma=None):
        if not(S or sigma):
            return (self.d1,self.d2)
        S=S or self.S
        sigma=sigma or self.sigma
        sigmaT = sigma * (self.T ** 0.5)    # sigma*T for reusability
        d1 = (np.log(S / self.K) +  (self.r - self.q + 0.5 * (sigma ** 2))* self.T) / sigmaT
        d2 = d1 - sigmaT
        return (d1,d2)

    def premium(self, S=None, sigma=None):
        S=S or self.S
        sigma=sigma or self.sigma
        d1,d2 = self.calculateDcoefficients(S,sigma)

        tmpprem = self.signForOptionType * (self.S * np.exp(-self.q * self.T) * norm.cdf(self.signForOptionType * d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(self.signForOptionType * d2))
        return tmpprem
 
    ############################################
    ############ 1st order greeks ##############
    ############################################
 
    def delta(self, sigma = None):
        sigma=sigma or self.sigma
        d1,d2 = self.calculateDcoefficients(sigma=sigma)

        dfq = np.exp(-self.q * self.T)
        if self.Type == PricingArguments.OptionType.CALL:
            return dfq * norm.cdf(d1)
        elif self.Type == PricingArguments.OptionType.PUT:
            return dfq * (norm.cdf(d1) - 1)
 
    # Vega for 1% change in vol
    def vega(self, sigma = None):
        sigma=sigma or self.sigma
        d1,d2 = self.calculateDcoefficients(sigma=sigma)
        return 0.01 * self.S * np.exp(-self.q * self.T) *norm.pdf(d1) * self.T ** 0.5
 
    # Theta for 1 day change  ## 365.0
    def theta(self):
        df = np.exp(-self.r * self.T)
        dfq = np.exp(-self.q * self.T)
        aux1 = -0.5 * self.S * dfq * norm.pdf(self.d1) *self.sigma / (self.T ** 0.5)
        aux2 = self.signForOptionType * self.q * self.S * dfq * norm.cdf(self.signForOptionType * self.d1)
        aux3 = -self.signForOptionType * self.r * self.K * df * norm.cdf(self.signForOptionType * self.d2)
        tmptheta = aux1+aux2+aux3
        
        return tmptheta
 
    def rho(self):
        df = np.exp(-self.r * self.T)
        return self.signForOptionType * self.K * self.T * df * 0.01 * norm.cdf(self.signForOptionType * self.d2)

    def phi(self):
        return 0.01* -self.signForOptionType * self.T * self.S *np.exp(-self.q * self.T) * norm.cdf(self.signForOptionType * self.d1)

    ############################################
    ############ 2nd order greeks ##############
    ############################################
 
    def gamma(self):
        return np.exp(-self.q * self.T) * norm.pdf(self.d1) / (self.S * self.sigmaT)

    # Charm for 1 day change
    def charm(self):
        dfq = np.exp(-self.q * self.T)
        return (1.0 / 365.25) * -dfq * (norm.pdf(self.d1) * ((self.r - self.q) / (self.sigmaT) - self.d2 / (2 * self.T)) + (-1*self.signForOptionType*self.q) * norm.cdf(self.signForOptionType*self.d1))

    # Vanna for 1% change in vol
    def vanna(self):
        return 0.01 * -np.exp(-self.q * self.T) * self.d2 / self.sigma * norm.pdf(self.d1)
 
    # Vomma
    def dVegadVol(self):
        return 0.01 * -np.exp(-self.q * self.T) * self.d2 / self.sigma * norm.pdf(self.d1)
    
# =============================================================================
# This class abstracts the use of binomial tree
# =============================================================================
class BinomialTree(PricingModel):
    def calculateDcoefficients(self, S=None, sigma=None):
        if not(S or sigma):
            return (self.d1,self.d2)
        S=S or self.S
        sigma=sigma or self.sigma
        sigmaT = sigma * (self.T ** 0.5)    # sigma*T for reusability
        d1 = (np.log(S / self.K) +  (self.r - self.q + 0.5 * (sigma ** 2))* self.T) / sigmaT
        d2 = d1 - sigmaT
        return (d1,d2)

    def set_variables(self, args):
        try:
            self.Type = args.putCall                # Call or Put
            self.S = args.underlyingPrice           # Underlying asset price
            self.K = args.strike                    # Option strike K
            self.r = args.riskFreeRate              # Continuous risk fee rate
            self.q = args.dividendRate              # Dividend continuous rate
            self.T = args.timeToExpiry              # Time to expiry
            self.sigma = args.volatility            # Underlying volatility
            self.num_iter = args.nIterations          #tree steps
        except:
            self.Type = 0                # 1 for a Call, - 1 for a put
            self.S = -99                 # Underlying asset price
            self.K = -99                 # Option strike K
            self.r = -99                 # Continuous risk fee rate
            self.q = -99                 # Dividend continuous rate
            self.T = 1                    # Time to expiry
            self.sigma = -99             # Underlying volatility            
            self.num_iter = 0             # tree steps
            
            
# =============================================================================
# Class with Leisen-Reimer binomial tree
# =============================================================================


class CRR(BinomialTree):
    
    def premium(self, S=None, sigma=None):
        S = S or self.S
        sigma = sigma or self.sigma

        dt = self.T / self.num_iter
        u = math.exp(sigma * math.sqrt(dt) )
        d = math.exp(-sigma * math.sqrt(dt) )
        p = ( math.exp( (self.r - self.q) * dt ) - d ) / ( u - d )
        qu = p
        qd = 1 - p
        STs = [np.array([S])]

        # Simulate the possible stock prices path
        for i in range(self.num_iter):
            prev_branches = STs[-1]
            st = np.concatenate((prev_branches * u, [prev_branches[-1] * d]))
            STs.append(st)  # Add nodes at each time step
 
        #Initialize payoff tree
        payoffs = np.maximum(0,(STs[self.num_iter]-self.K)*self.signForOptionType)

        #Begin tree traversal
        for i in reversed(range(self.num_iter)):
            # The payoffs from NOT exercising the option
            payoffs = (payoffs[:-1] * qu + payoffs[1:] * qd) * np.exp(-self.r*dt)#df
            # Payoffs from exercising, for American options
            early_ex_payoff = (STs[i] - self.K) * self.signForOptionType
            payoffs = np.maximum(payoffs, early_ex_payoff)

        return payoffs[0]

# =============================================================================
# Class with Leisen-Reimer binomial tree
# =============================================================================
class LR(BinomialTree):
    
    def premium(self, S=None, sigma=None):
        S=S or self.S
        sigma=sigma or self.sigma
        d1, d2 = self.calculateDcoefficients(S,sigma)
            
        odd_N = self.num_iter if (self.num_iter % 2 == 1) else (self.num_iter + 1)
        dt = self.T / odd_N
        r_n = np.exp((self.r - self.q) * dt)
        method = 2.
        Term1 = np.power((d1 / (odd_N + 1.0 / 3.0 - (1 - method) * 0.1 / (odd_N + 1))), 2) * (odd_N + 1.0 / 6.0)
        pp = 0.5 + np.copysign(1, d1) * 0.5 * np.sqrt(1 - np.exp(-Term1))
        Term2 = np.power((d2 / (odd_N + 1.0 / 3.0 - (1 - method) * 0.1 / (odd_N + 1))), 2) * (odd_N + 1.0 / 6.0)
        p = 0.5 + math.copysign(1, d2) * 0.5 * np.sqrt(1 - np.exp(-Term2))
 
        u = r_n * pp / p
        if (np.isnan(u)):
            u = r_n
        d = (r_n - p * u) / (1 - p)
        if (np.isnan(d)):
            d = (r_n - p * u) / (1E-6)
 
        qu = p
        qd = 1 - p
 
        STs = [np.array([S])]
        # Simulate the possible stock prices path
        for i in range(self.num_iter):
            prev_branches = STs[-1]
            st = np.concatenate((prev_branches * u, [prev_branches[-1] * d]))
            STs.append(st)  # Add nodes at each time step
 
        #Initialize payoff tree
        payoffs = np.maximum(0, (STs[odd_N-1]-self.K)*self.signForOptionType)
 
        #def check_early_exercise(payoffs, node):
        #    early_ex_payoff = (STs[node] - self.K) if is_call else (self.K - STs[node])
        #    return np.maximum(payoffs, early_ex_payoff)
 
    #Begin tree traversal
        for i in reversed(range(odd_N-1)):
            # The payoffs from NOT exercising the option
            payoffs = (payoffs[:-1] * qu + payoffs[1:] * qd) * np.exp(-self.r*dt)#df
            # Payoffs from exercising, for American options
            early_ex_payoff = (STs[i] - self.K)*self.signForOptionType
            payoffs = np.maximum(payoffs, early_ex_payoff)
        
        
        return payoffs[0]


# =============================================================================
# This class abstracts the quantLib librariesw tree for pricing
# =============================================================================
class QLPricingModel(PricingModel):
    def set_variables(self, args):
        try:
            self.Type = args.putCall                # Call or Put
            self.S = args.underlyingPrice           # Underlying asset price
            self.K = args.strike                    # Option strike K
            self.r = args.riskFreeRate              # Continuous risk fee rate
            self.q = args.dividendRate              # Dividend continuous rate
            self.T = args.timeToExpiry              # Time to expiry
            self.sigma = args.volatility            # Underlying volatility
            self.num_iter = args.nIterations
            self.eval_date = ql.DateParser.parseFormatted(args.QLStartDate, '%Y-%m-%d')
            self.maturity_date = ql.DateParser.parseFormatted(args.QLEndDate, '%Y-%m-%d')
        except:
            self.Type = 0
            self.S = -99
            self.K = -99
            self.r = -99
            self.q = -99
            self.T = 1
            self.sigma = -99
            self.num_iter = 0


class QL_Eur(QLPricingModel):
    def premium(self, S=None, sigma=None):
        S=S or self.S
        sigma=sigma or self.sigma

        maturityDate = self.maturity_date
        spotPrice = S
        strikePrice = self.K
        volatility = sigma # the historical vols or implied vols
        dividendRate =  self.q# 0.0163
        optionType = ql.Option.Call if self.Type==PricingArguments.OptionType.CALL else ql.Option.Put

        risk_free_rate = self.r
       
        day_count = ql.Actual365Fixed()
        calendar = ql.UnitedStates()
        calculation_date = self.eval_date
        ql.Settings.instance().evaluationDate = calculation_date 
 
        payoff = ql.PlainVanillaPayoff(optionType, strikePrice)
        settlement = calculation_date
 
        eu_exercise = ql.EuropeanExercise(maturityDate)
        european_option = ql.VanillaOption(payoff, eu_exercise)
    
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(spotPrice))
        flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate, day_count))
        dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, dividendRate, day_count))
        flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))
        bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts)
        european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
        
        return european_option.NPV()



class QL_Ame(QLPricingModel):
    def premium(self, S=None,sigma=None):
        S=S or self.S
        sigma=sigma or self.sigma

        maturity_date = self.maturity_date
        spot_price = S
        strike_price = self.K
        volatility = sigma # the historical vols or implied vols
        dividend_rate =  self.q# 0.0163
        option_type = ql.Option.Call if (self.Type==PricingArguments.OptionType.CALL) else ql.Option.Put
        risk_free_rate = self.r
       
        day_count = ql.Actual365Fixed()
        calendar = ql.UnitedStates()
        calculation_date = self.eval_date
        ql.Settings.instance().evaluationDate = calculation_date 
 
        payoff = ql.PlainVanillaPayoff(option_type, strike_price)
        settlement = calculation_date
 
        am_exercise = ql.AmericanExercise(settlement, maturity_date)
        american_option = ql.VanillaOption(payoff, am_exercise)
    
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
        flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate, day_count))
        dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, dividend_rate, day_count))
        flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, volatility, day_count))
        
        bsm_process = ql.BlackScholesMertonProcess(spot_handle, 
                                           dividend_yield, 
                                           flat_ts, 
                                           flat_vol_ts)
        
        binomial_engine = ql.BinomialVanillaEngine(bsm_process, "lr", self.num_iter)   
        american_option.setPricingEngine(binomial_engine)
        
        try:
            price = american_option.NPV()
        except:
            price = -99.99

        return price


class TrinomialTree(PricingModel):
    def set_variables(self, args):
        try:
            self.Type = args.putCall                # Call or Put
            self.S = args.underlyingPrice           # Underlying asset price
            self.K = args.strike                    # Option strike K
            self.r = args.riskFreeRate              # Continuous risk fee rate
            self.q = args.dividendRate              # Dividend continuous rate
            self.T = args.timeToExpiry              # Time to expiry
            self.sigma = args.volatility            # Underlying volatility
            self.num_iter = args.nIterations
        except:
            self.Type = 0
            self.S = -99
            self.K = -99
            self.r = -99
            self.q = -99
            self.T = 1
            self.sigma = -99
            self.num_iter = 0

    def premium(self, S=None, sigma=None):
        S=S or self.S
        sigma=sigma or self.sigma

        if self.T==0:
            payoffs=[0.0]
        else:
            dt = self.T/self.num_iter            
            u = math.exp(sigma*math.sqrt(2*dt))
            d = math.exp(-sigma*math.sqrt(2*dt))
            p_u = math.pow((math.exp((self.r - self.q) * dt/2) - math.exp(-sigma*math.sqrt(dt/2))) /
                           ( math.exp(sigma*math.sqrt(dt/2)) - math.exp(-sigma*math.sqrt(dt/2))),2)
            p_d = math.pow(( - math.exp((self.r - self.q) * dt/2) + math.exp(sigma*math.sqrt(dt/2))) /
                           ( math.exp(sigma*math.sqrt(dt/2)) - math.exp(-sigma*math.sqrt(dt/2))),2)
            p_m = 1 - p_u - p_d
            STs = [np.array([S])]
            
            # Simulate the possible stock prices path
            for i in range(self.num_iter):
                prev_branches = STs[-1]
                st = np.concatenate(([prev_branches[0]*u], prev_branches, [prev_branches[-1] * d]))
                STs.append(st)  # Add nodes at each time step
            
            #Initialize payoff tree
            #For put option clip intrinsic values below 0
            payoffs = np.maximum(0, (STs[self.num_iter]-self.K)*self.signForOptionType)

        #Begin tree traversal

            for i in reversed(range(self.num_iter)):
                # The payoffs from NOT exercising the option
                payoffs = (payoffs[:-2] * p_u + payoffs[2:] * p_d + payoffs[1:-1]*p_m ) * np.exp(-self.r*dt)
                
                # Payoffs from exercising, for American options
                early_ex_payoff = (STs[i] - self.K)*self.signForOptionType
                
                payoffs = np.maximum(payoffs, early_ex_payoff)
        return payoffs[0]