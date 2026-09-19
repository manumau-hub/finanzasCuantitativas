# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:49:14 2019

"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

class dividend_method_builder:
# =============================================================================
#     Get instance for corresponding method of dividend calculation
# =============================================================================
    
    def get_instance(self,               
                     str_div_method='constant'):
        
        child_dictionary={'linear_approximation' : linear_approximation,
                          'log_linear_approximation' : log_linear_approximation,
                          'constant' : constant,
                          'historical_average' : historical_average}
        
        return child_dictionary[str_div_method]()
    
class dividend_calculation_methods:
        
    def __init__(self):
        pass
        
    def set_valuation_date(self, date):
        self._date = date # evaluation date
        
    def set_security_ID(self, secID):
        self._securityID = secID
    
    def set_parameters(self, args):
        self._args = args
   
    def set_securityID_date(self, securityID, date):        
        self._securityID = securityID #contains the ID code 
        self._date = date # evaluation date
    
    def get_dividend_yield(self):
        return 0.0
            
class constant(dividend_calculation_methods):
            
    def get_dividend_yield(self, securityID, date, args_dict={'dividend_list' : 0.0,
                                                         'spot' : 0}):
        try:
            last_dividend = args_dict['dividend_list'].Amount.values[0]
            spot = args_dict['spot']
            freq = args_dict['dividend_list'].Frequency.values[0]
            return (last_dividend * freq / spot)
        except:
            return 0.0
class historical_average(dividend_calculation_methods):
        
    def get_dividend_yield(self, securityID, date, args_dict={'dividend_list' : 0.0,
                                                         'spot' : 0.0}):
        
        
        try:
            div_list = args_dict['dividend_list']
            spot = args_dict['spot']
        
            return (div_list.Amount.sum() / spot)
        except:
           return 0.0
class linear_approximation(dividend_calculation_methods):
        
    def get_dividend_yield(self, securityID, date, args_dict={'num_days' : 60,
                                                              'database_name': 'Pandora',
                                                              'database': None}):

        
        numdays = args_dict['num_days']
        dba = args_dict['database']
        db_name = args_dict['database_name']
        df = dba.get_last_option_price_list_from_securityID(numdays, securityID, date, 1) #getting last X(=numdays) items in the options price list
        df = df[(df !=-99.98999786376953).all(1)] # pre cleaning of the data frame
        
        regressors = pd.DataFrame(data=None, columns=['CmP','1','S','ST','K','KT','Dba','ValDate','Expiration'])
        
        price_list = dba.get_spot_list_from_securityID(securityID, numdays, date, 1) # getting spot price list
        
       
        if db_name=='Pandora':
            try:
                df['Date']=df['trading_dt']
                df['Expiration']=df['expiration_dt']
                df['CallPut']=df['put_call_indicator']
                df['Strike']=df['unscaled_strike_px']
                df['BestBid']=df['universal_bid_px']
                df['BestOffer']=df['universal_ask_px']
                price_list.Date = pd.to_datetime(price_list.Date)
            except:
                pass
        
       
        for day in df['Date'].value_counts().keys().tolist():
          
            spot = price_list[price_list['Date']==day]['ClosePrice']
            
            ts = pd.to_datetime(str(day)) 
            val_date_str = ts.strftime('%d-%b-%Y')            
            
            expirations = df[(df['CallPut']=='C') & (df['Date'] == day)]['Expiration'].value_counts().keys().tolist()
            
            for expiry in expirations:

                strikes = df[(df.CallPut=='C') & (df.Expiration == expiry) & (df['Date'] == day) ]['Strike'].value_counts().keys().tolist()
                
                ttm = int((expiry-day)/np.timedelta64(1,'D')) / 365.25
                
                if ttm*365.25 > 14:                          
                    call = pd.DataFrame(data=df[(df.CallPut=='C') & (df.Expiration == expiry) & (df['Date']==day)], columns=df.columns)
                    put = pd.DataFrame(data=df[(df.CallPut=='P') & (df.Expiration == expiry) & (df['Date']==day)], columns=df.columns)
                    
                     ##hasta aca va bien!
                    
                    for strike in strikes:
                                     
                    #Case 1
                        try:
                            CmP1 = call[call['Strike']==strike].BestBid.values[0] - put[put['Strike']==strike].BestOffer.values[0]                                                                       
                            
                            if db_name=='Pandora':
                                regressors = regressors.append(pd.DataFrame([[CmP1,1.0, spot, spot*ttm, strike, strike * ttm, 1.0, val_date_str, expiry]], columns=regressors.columns, index=None))
                            else:
                                regressors = regressors.append(pd.DataFrame([[CmP1,1.0, spot, spot*ttm, strike/1000.0, strike/1000.0 * ttm, 1.0, val_date_str, expiry]], columns=regressors.columns, index=None))
                            
                    #Case 2
                            CmP2 = call[call['Strike']==strike].BestOffer.values[0] - put[put['Strike']==strike].BestBid.values[0]                                                    
                            
                            #print("CmP1: ", CmP2)
                            #print("Regressor2", [CmP2,1.0, spot, spot*ttm, strike, strike * ttm, 0.0, val_date_str, expiry])
                            
                            if db_name=='Pandora':
                                regressors = regressors.append(pd.DataFrame([[CmP2,1.0, spot, spot*ttm, strike, strike * ttm, 0.0, val_date_str, expiry]], columns=regressors.columns, index=None))
                            else:
                                regressors = regressors.append(pd.DataFrame([[CmP2,1.0, spot, spot*ttm, strike/1000.0, strike/1000.0 * ttm, 0.0, val_date_str, expiry]], columns=regressors.columns, index=None))
                        except:
                            pass
                                    
                                        
        # make the regression
        Y = regressors["CmP"]
        X = regressors[["1","S","ST","K","KT","Dba"]]
   
        #print('CmP')
        #print(X)
        #print(Y)
        model = sm.OLS(Y, X.astype(float) ).fit()
        
        return -model.params[2] # dividend

# =================================================================================================================================
#         Calculation from CHAPTER 13 BUILDING AN EQUITY VOLATILITY SURFACE (pdf in references) - gives both r and d for each TTM
# =================================================================================================================================
class log_linear_approximation(dividend_calculation_methods):
    
    def get_dividend_yield(self, securityID=None, date=None, args_dict={'market_dataframe' : None}):
                        
        df = args_dict['market_dataframe']
        
        ttms = list(set(df[(df.CallPut=='C')].TTM.values))
        
        df_output = pd.DataFrame(index=None, data=None, columns=['TTM','r','d'])
        
        for ttm in ttms:
        
            regressors = pd.DataFrame(index=None, data=None, columns=['CmP','1','K','TTM'])
                    
            strikes = df[(df.CallPut=='C') & (df.TTM == ttm)].Strike.values
                                    
            for i,strike in enumerate(strikes):
                
                spot = df['Spot'][i] # get spot price
                
                if len(df[(df.CallPut == 'P') & (df.Strike == strike) & (df.TTM == ttm)]) == 1:
                            
                    #Case 1
                                
                    C = (df[(df.CallPut=='C') & (df.Strike== strike) & (df.TTM == ttm)].Bid.values[0] + df[(df.CallPut=='C') & (df.Strike== strike) & (df.TTM == ttm)].Ask.values[0])/2
                    P = (df[(df.CallPut=='P') & (df.Strike== strike) & (df.TTM == ttm)].Bid.values[0] + df[(df.CallPut=='P') & (df.Strike== strike) & (df.TTM == ttm)].Ask.values[0])/2
                                
                    CmP = C - P
                                
                    newDF = pd.DataFrame(columns = regressors.columns, index=None)
                    newDF.loc[0]=[CmP,1.0, strike, ttm]
                    regressors = regressors.append(newDF)
                            
                                            
            # make the regression
            Y = regressors["CmP"]
            X = regressors[["1","K"]]
            
            try:
                model = sm.OLS(Y, X ).fit()
                r = -1/(ttm/365.25) * np.log(-model.params[1])
                d = 1/(ttm/365.25) * np.log(spot/model.params[0])
            except:    
                r = 'NaN'
                d = 'NaN'
            
            
            newDFOutput = pd.DataFrame(columns = df_output.columns, index=None)
            newDFOutput.loc[0]=[ttm,r, d]
            df_output = df_output.append(newDFOutput)
#            print(df_output)
        
        return df_output 

