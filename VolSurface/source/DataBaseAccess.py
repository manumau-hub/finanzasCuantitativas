# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 11:37:53 2019

"""
from abc import ABC, abstractmethod
import pyodbc
import pandas as pd
import numpy as np
import sys, inspect
from functools import lru_cache
from datetime import datetime
import re


class DatabaseAccess(ABC):
    TICKER_MAPPING_DICT={
                'SPX': ('.SPX', '200847957', 'IC_EquityIndexAxiomaTS'),
                'NDX': ('.NDX', '202619978', 'IC_EquityIndexIDCTS'),
                'RUT': ('.RUT', '200903680', 'IC_EquityIndexAxiomaTS'),
                'DJX': ('.DJX', '202619952', 'IC_EquityIndexIDCTS')
                }
    SECID_MAPPING_DICT={v[0]:(v[1],v[2]) for v in TICKER_MAPPING_DICT.values()}

    @classmethod
    def availableVendorAccesses(cls):
        result={}
        callers_module = sys._getframe(1).f_globals['__name__']
        classes = inspect.getmembers(sys.modules[callers_module], inspect.isclass)
        for name, obj in classes:
            if (obj is not DatabaseAccess) and (DatabaseAccess in inspect.getmro(obj)):
                result[obj.vendorName()]=obj
        return result

    @classmethod
    def createInstanceOfDatabaseAccess(cls, vendorName, server='', database=None, username=None, password=None):
        '''Returns an instance of the child database class using a builder'''
        return cls.availableVendorAccesses()[vendorName](server, database, username, password)

    def __init__(self,server,database,username,password):
        self.connect(server, database, username, password)
        
    def __exit__(self):
        self.disconnect()
        
    def disconnect(self):
        try:
            self._cursor.close()
            self._cnxn.close() #Close connection to the server
        except Exception as e:
            print('Attempt to use a closed cursor.')
            print(e.msg)
        
    def connect(self,server,database,username,password):
        self._serverName = server
        self._databaseName = database
        self._username = username
        self._password = password
        try:
            if (not(username or password)):
                self._cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';Trusted_Connection = yes', autocommit = True)
            else:
                self._cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password, autocommit = True)
            self._cursor = self._cnxn.cursor()
        except Exception as e:
            raise e
            
    @property
    def isConnected(self):
        try:
            cursor = self._cnxn.cursor()
        except pyodbc.ProgrammingError:
            return False
        return True
    
# =============================================================================
#     Methods to pull database information
# =============================================================================        
    @abstractmethod
    def getSecurityIDFromTicker(self, ticker, date='', country=''):
        pass

    @abstractmethod
    def pullOptionPricesTable(self, str_security, date, isIndex = 0):
        '''
        Option price dataframe fields:
        Date, Spot, IsIndex, Strike, TTM, CallPut, ExerciseStyle, Bid, Ask, AveragePrice, Volume, OpenInterest, DBImpVol, DBDelta, DBGamma, DBVega, DBTheta
        '''
        pass

    @abstractmethod
    def pullZCurve(self, date, curve ='', currency =''):
        '''
        Zero coupon dataframe fields:
        Date, TTM, Rate        (Rate must be in %()
        '''
        pass

    @abstractmethod
    def getUnderlyingSpotPriceFromSecurityID(self, securityID, date):
        pass

    @abstractmethod
    def getUnderlyingSpotPriceFromTicker(self, ticker, date, inIndex=0):
        pass

    @abstractmethod
    def getDividendYieldFromSecurityID(self, securityID, date, isIndex = 0):
        pass

    @abstractmethod
    def getOptionExerciseStyle(self, securityID, date, isIndex = 0):
        pass

    @abstractmethod
    def isIndex(self,*args,**kwargs):
        pass
    
    
# =============================================================================
#     Child classes
# =============================================================================
class VendorDBAccess(DatabaseAccess):
    '''
    This class is responsible for the database connection and data extraction
    '''
    @classmethod
    def vendorName(cls):
        return 'Vendor'

    def __init__(self,server=None,database=None,username = None,password = None):
        server = server or 'PROD-VNDR-DB'
        database = database or 'IvyDBUS'
        username=username or 'tqa_user'
        password=password or 'tqa_user'

        super().__init__(server, database, username, password)

    def getSecurityIDFromTicker(self, ticker, date='', country=''):
        """
        Given a security Ticker this methods gets the securityID in the database
        Inputs:
            ticker: string
            table: string
        Output:
            securityID: string
        """
        table = 'SECURITY'
        query = "select securityID from " + self._databaseName + ".dbo." + table + " where Ticker='" + ticker + "'"
        securityid = pd.read_sql(query, self._cnxn).values[0][0]
        return str(securityid)

    def getTickerFromSecurityID(self, securityID, date='', country=''):
        """
        Given a security Ticker this methods gets the securityID in the database
        Inputs:
            securityID: string
            table: string
        Output:
            ticker: string
        """
        table = 'SECURITY'
        query = "select Ticker from " + self._databaseName + ".dbo." + table + " where SecurityID = '" + securityID + "'"
        ticker = pd.read_sql(query, self._cnxn).values[0][0]
        return ticker

    def getOptionExerciseStyle(self, securityID, date=None):
        table = 'OPTION_INFO'
        query = "select ExerciseStyle from " + self._databaseName + ".dbo." + table + " where securityid=" + securityID
        return pd.read_sql(query, self._cnxn).values[0][0]
        
    def pullOptionPricesTable(self, securityID, date):
        """
        Given a security Id and a date, this methods pulls the raw Option Price database from IvyDBUS into a pandas dataframe
        Inputs:
            securityID: security ID string - Check IvyDB
            date = string date fomrat "04-Apr-2019"            
        Output:
            df: dataframe
        """
        #1) Extraction
        table = 'OPTION_PRICE_VIEW'
        query = "select * from " + self._databaseName + ".dbo." + table + " where securityid=" + securityID + " and date='" + date + "'";
        df_clean = pd.read_sql(query, self._cnxn)

        #Some validation
        try:
            _=str(df_clean['Date'].values[0])[0:10]
        except:
            raise(Exception("Invalid data for {0} at {1}".format(securityID, str(date))))

        securityID =str(df_clean['SecurityID'].values[0])
        spot = self.getUnderlyingSpotPriceFromSecurityID(securityID, date)
        isIndex = self.isIndex(securityID)
        val_date = df_clean['Date'].values[0]
        
        #2)remove some columns and rows
        df_clean=df_clean.drop(df_clean[df_clean['SpecialSettlement'] == 1].index)
        df_clean=df_clean.drop(['SecurityID','SymbolFlag','LastTradeDate','OptionID','AdjustmentFactor'],axis=1)
        
        #3-4) Generate Time to maturity and Rate
        TTMs = np.array([ int((ttm-val_date)/np.timedelta64(1,'D')) for ttm in df_clean["Expiration"].values ])
        df_clean['TTM'] = TTMs
        df_clean['YearFraction'] = TTMs/365.0

        #5)Divide by 1000 the strikes
        df_clean['Strike'] = df_clean['Strike']/1000

        #adding a spot column (constant)
        df_clean['Spot'] = spot
        df_clean['IsIndex'] = int(isIndex)
            
        #6)renaming and reordering some columns
        df_clean.rename(columns={'BestBid':'Bid','BestOffer':'Ask','ImpliedVolatility':'DBImpVol','Delta':'DBDelta','Gamma':'DBGamma','Vega':'DBVega','Theta':'DBTheta'}, inplace = True)
        df_clean['AveragePrice']=(df_clean['Ask']+df_clean['Bid'])/2 #...calculating average price
        df_clean['ExerciseStyle'] = self.getOptionExerciseStyle(securityID)
        df_clean = df_clean[['Symbol', 'Date','Spot','IsIndex','Strike','TTM','YearFraction','CallPut', 'Expiration','ExerciseStyle','Bid','Ask', 'AveragePrice','Volume','OpenInterest','DBImpVol','DBDelta','DBGamma','DBVega','DBTheta']]
           
        #7) Sort and reindex
        df_clean = df_clean.sort_values(['TTM','CallPut','Strike'])
        df_clean = df_clean.reset_index(drop=True)
    
        return df_clean
    
    def pullOptionPricesOfTicker(self, ticker, date):
        securityID = self.getSecurityIDFromTicker(ticker, date)
        return self.pullOptionPricesTable(securityID, date)

    def pullZCurve(self, date, curve =None, currency=None):
        """
        Given a datethis methods gets the ZC curve
        Inputs:
            date: string / date fomrat "04-Apr-2019"
        Output:
            df_ZC: dataframe
        """
        table = 'Zero_CURVE'
        query = "select * from " + self._databaseName + ".dbo." + table + " where date='" + date + "'"
        ZC_curve = pd.read_sql(query, self._cnxn)
        ZC_curve['Quote']=ZC_curve['Rate']/100   #Change rate to percentage
        ZC_curve=ZC_curve.rename(columns={"Days": "TTM"})
        ZC_curve['Inyears'] = ZC_curve['TTM'] / 365.0
        return ZC_curve

    def pullVolatilitySurfaceOfSecurityID(self, securityID, date):
        """
        Given a security Id and a date, this methods pulls the derived Volatility Surface database from IvyDBUS into a pandas dataframe
        Inputs:
            securityID: The db securityID - Check IvyDB
        Output:
            df: dataframe
        """
        table = 'volatility_surface_view'
        query = "select * from " + self._databaseName + ".dbo." + table + " where securityid=" + securityID + " and date='" + date + "'";
        return pd.read_sql(query, self._cnxn)

    def pullVolatilitySurfaceOfTicker(self, ticker, date):
        securityID = self.getSecurityIDFromTicker(ticker)
        return self.pullVolatilitySurfaceOfSecurityID(securityID, date)

    @lru_cache()
    def isIndex(self, securityID):
        """
        Given a security Ticker this methods gets the securityID in the database
        Inputs:
            securityID: string
        Output:
            isIndex: boolean
        """
        table = 'SECURITY'
        query = "select IndexFlag from IvyDBUS.dbo."+table+" where securityid='"+securityID+"'";
        return pd.read_sql(query, self._cnxn).values[0][0]=='1'
              
    def getSecurityIDFromCUSIP(self, cusip, table ='SECURITY'):
        
        """
        Given a security CUSIP this methods gets the securityID in the database
        Inputs:
            cusip: string
        Output:
            securityID: string 
        """
        query = "select securityID from IvyDBUS.dbo."+table+" where CUSIP='"+cusip+"'";
        return str(pd.read_sql(query, self._cnxn).values[0][0])

    def getOptionInfo(self, securityID):
        """
        Given a securityID this methods gets the option info 
        Inputs:
            securityID: string
        Output: list:
            Dividend Convention: 
            Dividend Convention: 
            Exercise Style: string 'A'-'E'
            AMSettlementFlag: int / 0-1
        """
        table='OPTION_INFO'
        query = "select * from IvyDBUS.dbo."+table+" where securityid='"+securityID+"'";
        option_info = pd.read_sql(query, self._cnxn).values
        return option_info.tolist()[0]

    def getUnderlyingSpotPriceFromSecurityID(self, securityID, date):
        """
        Given a security securityID and a date this methods gets the spot price
        Inputs:
            securityID: string
            date: string
        Output:
            spot: double
        """
        table = 'SECURITY_PRICE'
        query = "select ClosePrice from IvyDBUS.dbo."+table+" where securityid="+str(securityID)+" and date='"+ str(date)+"'";
        return pd.read_sql(query, self._cnxn).values[0][0]

    def getUnderlyingSpotPriceFromTicker(self, ticker, date):
        """
        Given a security ticker and a date this methods gets the spot price
        Inputs:
            ticker: string
            date: string
        Output:
            spot: double
        """
        securityID = self.getSecurityIDFromTicker(ticker)
        return self.getUnderlyingSpotPriceFromSecurityID(securityID, date)

    def pullSpotListFromSecurityId(self, securityID, numdays, date):
        query = "select TOP "+str(numdays)+" Date, ClosePrice from IvyDBUS.dbo.SECURITY_PRICE where securityid="+str(securityID)+" and date<= '"+ str(date)+"' order by Date desc"
        return pd.read_sql(query, self._cnxn)

    def pull_securityids_database(self):
        """
        Pull the list of securityIDs, CUSIPS and Ticker into a pandas dataframe
        Inputs:
            void
        Output:
            df: dataframe
        """
        query = "select * from IvyDBUS.dbo.SECURITY;"
        return pd.read_sql(query, self._cnxn)
        
    def pullDividendListFromTicker(self, ticker, date):
        try:
            securityID = self.getSecurityIDFromTicker(ticker)
        except:
            securityID = ticker

        possibleDataFormats=("%d-%b-%Y","%d-%m-%Y","%Y-%m-%d")

        div_list=0
        for format in possibleDataFormats:
            try:
                dt = datetime.strptime(date,format)
                date_prev=datetime(dt.year-1,dt.month,dt.day).strftime(format)
                query = "select * from " + self._databaseName + ".dbo.DISTRIBUTION where securityid=" + securityID + " and ExDate<='" + date + "' and ExDate> '" + date_prev + "'"
                div_list = pd.read_sql(query, self._cnxn)
                break
            except:
                continue

        freqDictionary={
                        '0' :   0,
                        '1' :   1,
                        '2' :   2,
                        '3' :   4,
                        '4' :   12,}
        try:
            freq = freqDictionary.get(div_list.Frequency.values[0],0)
            div_list.Frequency = freq
            output = div_list[['RecordDate', 'ExDate', 'Amount', 'PaymentDate', 'Frequency']]
        except Exception as e:
            raise(Exception("Could not get dividend list for {0}@{1}\n".format(ticker,date)+str(e)))
        return output

    def getLastDividend(self, securityID, date):
        query = "select Top 1 Amount from " + self._databaseName + ".dbo.DISTRIBUTION where securityid=" + securityID + " and ExDate < '" + date + "' order by ExDate desc;"
        try:
            last_div = pd.read_sql(query, self._cnxn).Amount.values[0]
        except:
            print("Could not find last dividend for secId {0}".format(securityID))
            last_div=0
        return last_div

    def getLastExerciseDate(self, securityID, date):
        query = "select Top 1 ExDate from " + self._databaseName + ".dbo.DISTRIBUTION where securityid=" + securityID + " and ExDate < '" + date + "' order by ExDate desc;"
        return pd.read_sql(query, self._cnxn).ExDate.values[0]
    
    def pullLastNDaysOptionPriceFromSecurityId(self, securityID, numdays, date):
        #using a nested query
        query = "SELECT * FROM IvyDBUS.dbo.OPTION_PRICE_VIEW where securityid = " + str(securityID) + " and date in (SELECT TOP "+ str(numdays)+" date FROM IvyDBUS.dbo.SECURITY_PRICE where securityid = " + str(securityID) + " and date<= '" + date + "') ORDER BY Date DESC;"
        return pd.read_sql(query, self._cnxn)
    
    def getDividendYieldFromSecurityID(self, securityID, date):
        isIndex=self.isIndex(securityID)
        if isIndex:
            query = "select * from " + self._databaseName + ".dbo." + 'Index_Dividend' + " where securityid=" + securityID + " and date='" + date + "'";
            div = (pd.read_sql(query, self._cnxn).Rate[0])/100.0
        else:
            print('No div method for stock in Vendor DB')
            div = 0
        return div
    
    def pullNDaysOfVolatilitySurfaceFromSecurityId(self, securityID, numdays, date):
        #using a nested query
        query = "SELECT * FROM IvyDBUS.dbo.OPTION_PRICE_VIEW where securityid = " + str(securityID) + " and date in (SELECT TOP "+ str(numdays)+" date FROM IvyDBUS.dbo.SECURITY_PRICE where securityid = " + str(securityID) + " and date<= '" + date + "') ORDER BY Date DESC;"
        return pd.read_sql(query, self._cnxn)#.values


class PandoraDBAccess(DatabaseAccess):
    @classmethod
    def vendorName(cls):
        return 'Pandora'
    
    def __init__(self, server=None, database=None, username=None, password=None):
        server = server or 'pandora'
        database = database or 'EJV_Derivs'
        username = username or ''
        password = password or ''
        super().__init__(server, database, username, password)

    def dateStringToDatetime(self,dateString):
        possibleDataFormats = ("%d-%b-%Y", "%d-%m-%Y", "%Y-%m-%d")
        dt=None
        for format in possibleDataFormats:
            try:
                dt = datetime.strptime(dateString, format)
            except:
                continue
        if not dt:
            print("Could not convert dateString {0}".format(dateString))
            return
        return dt

    DATE_STANDARD_FORMAT = "%Y-%m-%d"

    def getSecurityIDFromTicker(self, ticker, date ='2019-04-04', country ='US', db=None):
        """
        Given a security Ticker this methods gets the securityID in the database
        Inputs:
            ticker: string
            table: string
        Output:
            securityID: string
        """
        if not db:
            db='EJV' if self.isIndex(ticker, date) else 'ORACLE'

        if db == 'ORACLE':
            date=self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)

            query = """select * from openquery([ORA-GLPROD-marketdb_global],
                                 'select sub_id from modeldb_global.sub_issue a, modeldb_global.issue_map b,
                                 asset_dim_ticker_active_int c, asset_dim_ctry_exch_int d
                                 where c.id= ''""" + ticker + """'' and c.axioma_id=d.axioma_id
                                 and c.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and c.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                                 and d.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and d.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                                 and a.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and a.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                                 and b.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and b.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                                 and c.axioma_id=b.marketdb_id
                                 and b.modeldb_id=a.issue_id
                                 and d.country= ''""" + country + """'' ')"""
            try:
                securityid = str(pd.read_sql(query, self._cnxn).values[0][0])
            except:
                securityid = ''
                print("No Security ID for {0}".format(ticker))
        
        else:
            """"
                ToDo: Need to add case to look for ric given the ticker. Nattu's suggested path is:
                ticker -> sedol (using InstrumentXRef with AsOfDate) -> quote_id (using EJV_Equity quote_xref table using sedol)
                -> options (EJV_Derivs quote_xref table with quote_id as underlying_quote_id)
                
                OR
                
                ticker -> sedol (using InstrumentXRef with AsOfDate) -> RIC (using EJV_Equity quote_xref table using sedol)
                -> options (EJV_Derivs quote_xref table with ric as underlying_ric)
            """
            securityid={
                         'SPX':'.SPX',
                         'NDX':'.NDX',
                         'RUT':'.RUT',
                         'DJX':'.DJX'}.get(ticker,ticker + '.U')
        return securityid

    def getAxiomaIdFromTicker(self, ticker, date ='2019-04-04', country ='US'):
        """
        Given a security Ticker this methods gets the axiomaID in the database
        Inputs:
            ticker: string
            table: string
        Output:
            securityID: string
        """
        #ToDo: Only option is ORACLE? Should be able to retrieve stocks info from EJV
        date=self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)

        query = """select * from openquery([ORA-GLPROD-marketdb_global],
                             'select c.axioma_id from modeldb_global.sub_issue a, modeldb_global.issue_map b,
                             asset_dim_ticker_active_int c, asset_dim_ctry_exch_int d
                             where c.id= ''""" + ticker + """'' and c.axioma_id=d.axioma_id
                             and c.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and c.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                             and d.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and d.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                             and a.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and a.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                             and b.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and b.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                             and c.axioma_id=b.marketdb_id
                             and b.modeldb_id=a.issue_id
                             and d.country= ''""" + country + """'' ')"""
        try:
            axioma_id = pd.read_sql(query, self._cnxn).values[0][0]
        except:
            axioma_id=''
            print("No Axioma_ID for {0}".format(ticker))

        return str(axioma_id)

    def getTickerFromSecurityId(self,securityId,date ='2019-04-04',country ='US'):
        date=self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)

        query = """select * from openquery([ORA-GLPROD-marketdb_global],
                             'select c.id from modeldb_global.sub_issue a, modeldb_global.issue_map b,
                             asset_dim_ticker_active_int c, asset_dim_ctry_exch_int d
                             where sub_id= ''""" + securityId + """'' and c.axioma_id=d.axioma_id
                             and c.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and c.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                             and d.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and d.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                             and a.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and a.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                             and b.from_dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') and b.thru_dt > TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')
                             and c.axioma_id=b.marketdb_id
                             and b.modeldb_id=a.issue_id
                             and d.country= ''""" + country + """'' ')"""
        try:
            ticker = str(pd.read_sql(query, self._cnxn).values[0][0])
        except:
            ticker = ''
            print("No ticker for {0}".format(securityId))

        return ticker

    def pullOptionPricesTable(self, ticker='AAPL', date ='2019-04-04'):
        """
        Given a ric_root string and a date, this methods pulls the raw Option Price database from EJV into a pandas dataframe
        Inputs:
            ticker: Stock ticker
            date = string date fomrat "2019-04-04"            
        Output:
            df: dataframe
        """
        ricRoot=ticker+'.U'
        isIndex=self.isIndex(ticker)

        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)

        if not isIndex:
            query = """select trading_dt, bid_px, ask_px, universal_bid_px, universal_ask_px, vol, open_interest, a.ric_root, unscaled_strike_px, put_call_indicator, expiration_dt, exercise_style_cd, a.ric, days_to_expiration 
                    from EJV_Derivs.dbo.quote_xref a, EJV_Derivs.dbo.price b 
                    where ric_root = '"""+ ricRoot + """' and a.currency_cd= 'USD' and rcs_cd='OPT' and put_call_indicator is not null and expiration_dt >= '""" + date + """' 
                    and a.quote_id=b.quote_id and b.trading_dt = '"""+date+"""' """;
        else:
            underlyingRic, AxiomaDataId, table = self.TICKER_MAPPING_DICT.get(ticker, ('ERROR - index not handled', '', ''))
            if not table:
                print("Could not map index ticker in DB!")
                return

            query = """select trading_dt, bid_px, ask_px, universal_bid_px, universal_ask_px, vol, open_interest, a.ric_root, unscaled_strike_px, put_call_indicator, expiration_dt, exercise_style_cd, a.ric, days_to_expiration 
                    from EJV_Derivs.dbo.quote_xref a, EJV_Derivs.dbo.price b 
                    where underlying_ric = '"""+ underlyingRic + """' and a.currency_cd= 'USD' and rcs_cd='OPT' and put_call_indicator is not null and expiration_dt >= '""" + date + """' 
                    and a.quote_id=b.quote_id and b.trading_dt = '"""+date+"""' """;
        
        df = pd.read_sql(query, self._cnxn)

        #Post-processing
        df = df.drop_duplicates(keep='first')
        df = df.sort_values(['expiration_dt','unscaled_strike_px','put_call_indicator',])
        df = df.reset_index(drop=True)
        df = df.drop(['ric_root','bid_px','ask_px'],axis=1)
        df.rename(columns={'ric':'Symbol','trading_dt':'Date','universal_bid_px':'Bid','universal_ask_px':'Ask', 'exercise_style_cd' : 'ExerciseStyle', 'vol':'Volume','open_interest':'OpenInterest','unscaled_strike_px':'Strike','put_call_indicator':'CallPut', 'days_to_expiration':'TTM', 'expiration_dt':'Expiration'}, inplace = True)

        val_date = df['Date'].values[0]
        TTMs=np.array([int((ttm - val_date) / np.timedelta64(1, 'D')) for ttm in df["Expiration"].values])
        df['YearFraction'] = TTMs / 365.0

        if not isIndex:
            securityID = self.getSecurityIDFromTicker(ticker, date)
            spot = self.getUnderlyingSpotPriceFromSecurityID(securityID, date)
            df['Spot'] = float(spot)
        else:
            query_spot = """ exec MarketData.dbo.""" + table + """ @AxiomaDataIds= '""" + AxiomaDataId + """', @AsOfDate = '""" + date + """' """
            # print('checking spot from index')
            df_spots = pd.read_sql(query_spot, self._cnxn)
            df['Spot'] = df_spots.Value.values[-1]
    
        #adding a spot column (constant)
        df['IsIndex'] = int(isIndex)
        df['Date'] = date
        df['AveragePrice']=(df['Ask']+df['Bid'])/2 #...average price
        df['DBImpVol'] = -99
        df['DBDelta'] = -99
        df['DBGamma'] = -99
        df['DBVega'] = -99
        df['DBTheta'] = -99
        
        
        #ToDo: Check use of DB prefix in columns
        df = df[['Symbol','Date','Spot','IsIndex','Strike','TTM','YearFraction','CallPut', 'Expiration','ExerciseStyle','Bid','Ask', 'AveragePrice','Volume','OpenInterest','DBImpVol','DBDelta','DBGamma','DBVega','DBTheta']]
        
        df = df.sort_values(['TTM','CallPut','Strike',])
        df = df.reset_index(drop=True)
    
        return df
    
    def pullLastNDaysOfOptionPrices(self, ticker, numdays, date):
        isIndex=self.isIndex(ticker)
        underlyingRic, AxiomaDataId, table = self.TICKER_MAPPING_DICT.get(ticker, ('ERROR - index not handled', '', ''))
        ricRoot=ticker+'.U'
        date= self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)

        if isIndex:
            query ="""
                select b.trading_dt, bid_px, ask_px, universal_bid_px, universal_ask_px, vol, open_interest, a.ric_root, unscaled_strike_px, put_call_indicator, expiration_dt, exercise_style_cd, a.ric, days_to_expiration
                from EJV_Derivs.dbo.quote_xref a, EJV_Derivs.dbo.price b 
                where underlying_ric= '""" + underlyingRic + """' and put_call_indicator is not null and expiration_dt >= '""" + date+ """'
                and a.quote_id=b.quote_id and b.trading_dt in
                (select distinct top """ + str(numdays) + """ trading_dt from EJV_Derivs.dbo.price b, EJV_Derivs.dbo.quote_xref a where a.underlying_ric= '""" + underlyingRic + """' and a.quote_id=b.quote_id and trading_dt <= '""" + date+ """' order by trading_dt DESC)"""
        else:
            securityId = self.getSecurityIDFromTicker(ticker, date)
            query ="""
                select b.trading_dt, bid_px, ask_px, universal_bid_px, universal_ask_px, vol, open_interest, a.ric_root, unscaled_strike_px, put_call_indicator, expiration_dt, exercise_style_cd, a.ric, days_to_expiration
                from EJV_Derivs.dbo.quote_xref a, EJV_Derivs.dbo.price b 
                where ric_root= '""" + ricRoot + """' and put_call_indicator is not null and expiration_dt >= '""" + date+ """'
                and a.quote_id=b.quote_id and b.trading_dt in
                (select DT from openquery([ORA-GLPROD-marketdb_global], 
                'select * from ( select * from modeldb_global.sub_issue_data_active where sub_issue_id = ''"""+securityId+"""'' 
                  and dt <= TO_DATE(''"""+ date + """'', ''YYYY-MM-DD'') order by DT desc) WHERE rownum <=""" + str(numdays) + """'))"""

        ## IT SHOULD BE exp-num days in the 3rd line of the query... 
        df = pd.read_sql(query, self._cnxn)
        df = df.sort_values(['trading_dt']).reset_index(drop=True)
        return df

    def getOptionExerciseStyle(self, ticker='AAPL', date ='2019-04-04'):
        isIndex=self.isIndex(ticker)
        ricRoot = ticker + '.U'
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        if not isIndex:
            query = """select Top 1 exercise_style_cd 
                    from EJV_Derivs.dbo.quote_xref a, EJV_Derivs.dbo.price b 
                    where ric_root = '""" + ricRoot + """' and a.currency_cd= 'USD' and put_call_indicator is not null and expiration_dt >= '""" + date + """' 
                    and a.quote_id=b.quote_id and b.trading_dt = '""" + date +"""' """;
        else:
            underlyingRic, _, _ = self.TICKER_MAPPING_DICT.get(ticker, ('ERROR - index not handled', '', ''))
            query = """select Top 1 exercise_style_cd 
                    from EJV_Derivs.dbo.quote_xref a, EJV_Derivs.dbo.price b 
                    where underlying_ric = '""" + underlyingRic + """' and a.currency_cd= 'USD' and put_call_indicator is not null and expiration_dt >= '""" + date + """' 
                    and a.quote_id=b.quote_id and b.trading_dt = '""" + date + """' """;

        return pd.read_sql(query, self._cnxn).exercise_style_cd.values[0]

    @lru_cache()
    def isIndex(self, tickerOrSecurityId ='AAPL', date ='2019-04-04', _isSecurityId=False):
        '''
        This function will work both with securityIDs and tickers.
        Don't worry about argument _isSecurityId. It's for internal use.
        '''
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        if _isSecurityId:
            tickerOrSecurityId=self.getTickerFromSecurityId(tickerOrSecurityId, date)
        query = """select Top 1 lot_units_cd 
                    from EJV_Derivs.dbo.quote_xref a, EJV_Derivs.dbo.price b 
                    where description like ('%""" + tickerOrSecurityId + """%') and a.currency_cd= 'USD' and put_call_indicator is not null and expiration_dt >= '""" + date + """' 
                    and a.quote_id=b.quote_id and b.trading_dt = '""" + date +"""' """;
        try:
            valueType=pd.read_sql(query, self._cnxn).lot_units_cd.values[0]
        except:
            #Wait, this could still be a securityId and not a ticker
            if not _isSecurityId:
                return self.isIndex(tickerOrSecurityId, date, True)
            else:
                print("Query failed isIndex failed for {0} both like secId and ticker".format(tickerOrSecurityId))
                return ''

        if valueType == "SHARE":
            return False
        elif valueType == "INDEX":
            return True
        else:
            print("Warning: Could not determine if symbol is Index or not")
            return False

    def pullSpotTableFromTicker(self, ticker ='AAPL', numdays=10, date ='2019-04-04'):
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        isIndex=self.isIndex(ticker,date)
        if isIndex:
            _,AxiomaDataId, table = self.TICKER_MAPPING_DICT.get(ticker, ('ERROR - index not handled', '',''))
            if not table:
                print("Only indexes handled are SPX, NDX, RUT and DJX!")
            
            query_spot = """ exec MarketData.dbo."""+table+""" @AxiomaDataIds= '""" + AxiomaDataId + """', @AsOfDate = '""" + date + """' """
            df = pd.read_sql(query_spot, self._cnxn)[-numdays:]
            df = df.rename(columns={'Value':'ClosePrice'})
            df = df[['Date','ClosePrice']]
            df = df.reindex(index = df.index[::-1])
            df = df.reset_index(drop=True)
            """check that DATES are in different format"""
        else:
            securityID=self.getSecurityIDFromTicker(ticker,date)
            query = """select TOP """ + str(numdays) + """* from openquery([ORA-GLPROD-marketdb_global], 
                                        'select dt, ucp from modeldb_global.sub_issue_data_active where sub_issue_id = ''""" + securityID + """'' and dt <= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'')  order by dt desc')"""
            df = pd.read_sql(query, self._cnxn)
            df = df.rename(columns={'DT':'Date', 'UCP':'ClosePrice'})
        return df
    
    def pullZCurve(self, date, curve ='SwapZC', currency ='USD'):
        """
        Given a datethis methods gets the ZC curve
        Inputs:
            date: string / date fomrat "04-Apr-2019"
        Output:
            df_ZC: dataframe
        """
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        query = """
        SELECT cv.CurrencyEnum, CountryEnum, cv.CurveTypeEnum, CurveShortName, CurveLongName, TradeDate, te.Inyears, cq.Quote
        FROM [MarketData].[dbo].[Curve] cv
        join [MarketData].[dbo].[CurveNodes] cn on cv.CurveId = cn.CurveId 
        join [MarketData].[dbo].[TenorEnum] te on cn.TenorEnum = te.TenorEnum
        join [MarketData].[dbo].[CurveNodeQuote] cq on cq.CurveNodeId = cn.CurveNodeId
        and TradeDate = '""" + date + """'
        and cv.CurrencyEnum = '""" + currency + """'
        and cv.CurveTypeEnum = '""" + curve + """'
        order by InYears
        """
            
        return pd.read_sql(query, self._cnxn)
 
    # def pullLiborCurve(self, date, currency ='USD'):
    #     """
    #     Given a datethis methods gets the Libor curve
    #     Inputs:
    #         date: string / date fomrat "04-Apr-2019"
    #     Output:
    #         df_ZC: dataframe
    #     """
    #     date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
    #     query = """select * from MarketData..CurveNodes cn,  EJV_rigs.dbo.rt_n_indx i, EJV_rigs.dbo.rt_n_indx_level cnq
    #             where cn.VendorDataInternalId=i.indx_ric
    #             and i.indx_id = cnq.indx_id
    #             and cn.VendorDataIdTypeEnum = 'RIC'
    #             and i.crncy_denom_cd = '""" + currency + """'
    #             and cnq.eff_dt = '""" + date + """'
    #             """
    #     return pd.read_sql(query, self._cnxn)

    def getUnderlyingSpotPriceFromSecurityID(self, securityID ='DQ8L3JXGU111', date ="2019-04-04"):
        """
        Given a security securityID and a date this methods gets the spot price
        Inputs:
            securityID: string (Oracle Database sub_issue_id)
            date: string
        Output:
            spot: double
        """
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        query = """select * from openquery([ORA-GLPROD-marketdb_global], 
                                        'select ucp from modeldb_global.sub_issue_data_active where sub_issue_id = ''""" + securityID + """'' and dt = TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') ') """
        df = pd.read_sql(query, self._cnxn).values
        spot = float(df[0][0])
        return spot

    def getUnderlyingSpotPriceFromTicker(self, ticker, date):
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        isIndex=self.isIndex(ticker,date)
        if not isIndex:
            securityID_oracle = self.getSecurityIDFromTicker(ticker, date)
            spot = self.getUnderlyingSpotPriceFromSecurityID(securityID_oracle, date)
        else:
            _,AxiomaDataId, table = self.TICKER_MAPPING_DICT.get(ticker, ('ERROR - index not handled', '',''))
            if not table:
                print("Only indexes handled are SPX, NDX, RUT and DJX!")

            query_spot = """ exec MarketData.dbo."""+table+""" @AxiomaDataIds= '""" + AxiomaDataId + """', @AsOfDate = '""" + date + """' """
            df = pd.read_sql(query_spot, self._cnxn)
            df = df.rename(columns={'Value':'ClosePrice'})
            df = df[['Date','ClosePrice']]
            df = df.reindex(index = df.index[::-1])
            df = df.reset_index(drop=True)    
            spot = df.ClosePrice.values[0]
        return spot

    def getDividendYieldFromTicker(self,ticker,date):
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        if self.isIndex(ticker,date):
            print('No Index dividend in Pandora')
            return 0
        securityId=self.getSecurityIDFromTicker(ticker, date)
        return self.getDividendYieldFromSecurityID(securityId,date)

    def getDividendYieldFromSecurityID(self, securityID ='DQ8L3JXGU111', date ="2019-04-04"):
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        if self.isIndex(self.getTickerFromSecurityId(securityID),date):
            print('No Index dividend in Pandora')
            div = 0               
        else:
            query = """select * from openquery([ORA-GLPROD-marketdb_global], 'select div.dt DivDate, div.value 
                            from modeldb_global.sub_issue_divyield_active div 
                            where div.sub_issue_id = ''""" + securityID + """''
                            and div.dt = TO_DATE(''"""+date+"""'', ''YYYY-MM-DD'')') order by DivDate"""
            div = float(pd.read_sql(query, self._cnxn).values[0][1])
        return div

    def pullDividendListFromTicker(self, ticker, date):
        dt = self.dateStringToDatetime(date)
        date=dt.strftime(self.DATE_STANDARD_FORMAT)
        date_prev = datetime(dt.year - 1, dt.month, dt.day).strftime(self.DATE_STANDARD_FORMAT)
        query = """select * from openquery([ORA-GLPROD-marketdb_global], 'select a.axioma_id, a.ex_dt, a.gross_value, a.net_value, b.code, c.description, a.ca_sequence, a.pay_dt, a.rec_dt record_dt, a.real_ex_dt 
                        from asset_dim_cdiv_active a, currency_ref b, meta_codes c where axioma_id in (select distinct a.axioma_id from marketdb_global.asset_dim_ticker_active_int a, asset_dim_ctry_exch_int b 
                         where a.id= ''""" + ticker + """'' and a.axioma_id=b.axioma_id and a.thru_dt>= TO_DATE(''2999-12-31'', ''YYYY-MM-DD'') and b.country=''US'') and a.currency_id=b.id 
                         and a.pay_type=c.id and c.code_type like ''asset_dim_cdiv%'' and ex_dt>= TO_DATE(''""" + date_prev + """'', ''YYYY-MM-DD'') and ex_dt<= TO_DATE(''""" + date + """'', ''YYYY-MM-DD'') order by ex_dt');"""
        try:
            div_list = pd.read_sql(query, self._cnxn)
        except:
            print("Could not retrieve divident list from ticker {0}".format(ticker))
            return 0

        div_list = div_list.rename(columns ={'GROSS_VALUE':'Amount', 'EX_DT':'ExDate', 'PAY_DT':'PaymentDate', 'RECORD_DT':'RecordDate'})
        div_list["Amount"] = div_list["Amount"].astype('float64')

        try:
            div_list['Frequency'] = div_list["Amount"]
        except:
            div_list['Frequency'] = 0.0
        div_list = div_list[['RecordDate','ExDate','Amount','PaymentDate', 'Frequency']]

        return div_list

    def getLastDividendFromTicker(self, ticker, date):
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        try:
            div_list=self.pullDividendListFromTicker(ticker, date)
            last_div = float(div_list["Amount"].values[-1])
        except:
            last_div=0
        return last_div

    def calculateZCurveReplication(self, date, currency ='USD'):
        """
        Replication of OM ZC curve using alternative datasources
        """
        date = self.dateStringToDatetime(date).strftime(self.DATE_STANDARD_FORMAT)
        query1 = """select *
        from MarketData.dbo.InstrumentData a, EJV_RIGS.dbo.rt_n_indx_level b 
        where VendorDataIdTYpeEnum='EJV_indx_id' and name like '%U.S.%DOLLAR%LIBOR%'
        and convert(varbinary(max), VendorDataInternalId, 1) = b.indx_id
        and b.last_chg_dt >= '""" + date + """' and b.last_chg_dt <= '""" + date + """ 23:59'"""

        libor_df = pd.read_sql(query1, self._cnxn)
        libor_df = libor_df[['Name', 'eff_dt', 'mkt_value']]

        def mapNameToDays(name):
            TENOR_PERIOD_MAP = {
                'OVER-NIGHT'    :   'D',
                'WEEK'          :   'W',
                'MONTH'         :   'M',
                'YEAR'          :   'Y',
            }

            TENOR_PATTERN=r'U.S. DOLLAR (\d*)\s*([^\s]+).*'
            try:
                match=re.search(TENOR_PATTERN,name)
                tenorNum=match.group(1)
                tenorPeriod=TENOR_PERIOD_MAP.get(match.group(2))
            except:
                raise(Exception("Invalid LIBOR curve data"))

            return {
                        'D'     : 1,
                        '1W'    : 7,
                        '1M'    : 30,
                        '2M'    : 60,
                        '3M'    : 91,
                        '6M'    : 182,
                        '1Y'    : 365,
                    }.get(tenorNum+tenorPeriod)

        libor_df['TTM'] = libor_df['Name'].apply(mapNameToDays)
        libor_df = libor_df.sort_values(by = 'TTM').reset_index(drop=True)
        libor_df['DF'] = 0.0
        libor_df['Rate'] = 0.0
        libor_df = libor_df.rename(columns={'mkt_value':'Quote'})
        libor_df['Quote'] = libor_df['Quote']/100
        libor_df['DF'] = 1/(1+libor_df['Quote']*libor_df['TTM']/360)
        libor_df['Rate'] = -365/libor_df['TTM']*np.log(libor_df['DF'])
        libor_df = libor_df[libor_df['TTM'] != 1].reset_index(drop=True) #REMOVE OVERNIGHT

        #EURODOLLAR
        query2 = """select * from qai.dbo.DSFutContrInfo a, qai.dbo.DSFutContrVal b
        where a.ContrCode=2804 and a.FutCode=b.FutCode and Date_='""" + date + """' order by LastTrdDate"""

        eurodollar_df = pd.read_sql(query2, self._cnxn)
        eurodollar_df = eurodollar_df[['Date_','StartDate','LastTrdDate','SttlmntDate','Settlement']]

        #Check first future with maturity more than one month
        eurodollar_df['TTM']=(eurodollar_df['LastTrdDate']-eurodollar_df['Date_'])/np.timedelta64(1,'D') + 2
        eurodollar_df['F'] = 100 - eurodollar_df['Settlement']

        eurodollar_df = eurodollar_df[eurodollar_df['TTM']>7].reset_index(drop=True)
        first_future = eurodollar_df['TTM'].values[0]
        eurodollar_df['DF'] = 0.0   #Add DF and Rate columns before calculations
        eurodollar_df['Rate'] = 0.0
        #Interpolate first Future rate with libors 
        if first_future>60:
            eurodollar_df['Rate'].values[0] = (libor_df['Rate'].values[3] - libor_df['Rate'].values[2]) / (libor_df['TTM'].values[3] - libor_df['TTM'].values[2]) * ((eurodollar_df['TTM'].values[0] - libor_df['TTM'].values[2])) + libor_df['Rate'].values[2]
        elif first_future>30:
            eurodollar_df['Rate'].values[0] = (libor_df['Rate'].values[2] - libor_df['Rate'].values[1]) / (libor_df['TTM'].values[2] - libor_df['TTM'].values[1]) * ((eurodollar_df['TTM'].values[0] - libor_df['TTM'].values[1])) + libor_df['Rate'].values[1]
        else:
            eurodollar_df['Rate'].values[0] = (libor_df['Rate'].values[1] - libor_df['Rate'].values[0]) / (libor_df['TTM'].values[1] - libor_df['TTM'].values[0]) * ((eurodollar_df['TTM'].values[0] - libor_df['TTM'].values[0])) + libor_df['Rate'].values[0]

        eurodollar_df['DF'].values[0] = np.exp(-eurodollar_df['Rate'].values[0] * eurodollar_df['TTM'].values[0]/365)

        for i in range(1,len(eurodollar_df.index)):
            eurodollar_df['DF'].values[i] = eurodollar_df['DF'].values[i-1] / (1 + (eurodollar_df['F'].values[i-1]/100) * (eurodollar_df['TTM'].values[i] - eurodollar_df['TTM'].values[i-1]) /360)
            eurodollar_df['Rate'].values[i] = -365/eurodollar_df['TTM'].values[i]*np.log(eurodollar_df['DF'].values[i])

        #JOIN
        libor_df = libor_df[libor_df['TTM']<=first_future].reset_index(drop=True)
        curve_1 = libor_df.rename(columns={'eff_dt':'Date', 'TTM':'Days'})
        curve_1 = curve_1[['Date','Days','Rate']]

        curve_2 = eurodollar_df.rename(columns = {'Date_':'Date', 'TTM': 'Days' })
        curve_2 = curve_2[['Date','Days','Rate']]
        curve = pd.concat([curve_1,curve_2]).reset_index(drop=True)

        return curve


class PlutoDBAccess(PandoraDBAccess):
    @classmethod
    def vendorName(cls):
        return 'Pluto'

    def __init__(self, server=None, database=None, username=None, password=None):
        server = server or 'pluto'
        database = database or 'EJV_Derivs'
        username = username or ''
        password = password or ''
        super().__init__(server, database, username, password)