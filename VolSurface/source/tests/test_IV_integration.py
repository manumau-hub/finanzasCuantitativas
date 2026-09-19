from unittest import TestCase
from DataBaseAccess import DatabaseAccess
from implied_vol_calculator import ImpliedVolatilityCalculator
import statsmodels.api as sm
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd


class VolatilitySurfaceTests(TestCase):
    ROOT_FINDER_MAX_ITER = 10#100
    PRICER_MAX_ITER = 15#1500
    MIN_TTM = 0

    def setUp(self):
        self.ticker='AAPL'
        self.date='2019-04-04'  #keep it in yyyy-mm-dd format
        self.dbVendorHandle=DatabaseAccess.createInstanceOfDatabaseAccess('Vendor')
        self.benchmarkSecurityId=self.dbVendorHandle.getSecurityIDFromTicker(self.ticker)
        self.spotPrice = self.dbVendorHandle.getUnderlyingSpotPriceFromSecurityID(self.benchmarkSecurityId,self.date)
        self.dbInternalHandle=DatabaseAccess.createInstanceOfDatabaseAccess('Pandora')
        self.oracleSecurityID = self.dbInternalHandle.getSecurityIDFromTicker(self.ticker,date=self.date,db='ORACLE')
        self.EJVSecurityID = self.dbInternalHandle.getSecurityIDFromTicker(self.ticker,date=self.date,db='EJV')
        self.dividendYield=self.getDividendYield()
        self.optionPricesTable=self.getOptionPricesTable()
        # self.benchmarkSurface = self.dbVendorHandle.pullVolatilitySurfaceOfSecurityID(self.benchmarkSecurityId, self.date)
        self.benchmarkSurface=self.optionPricesTable
        self.zCurve=self.dbInternalHandle.pullZCurve(self.date)

    def getDividendYield(self):
        '''ToDo: add method for comparison of calculated div yield with DB div yield'''
        return self.dbInternalHandle.getDividendYieldFromSecurityID(self.oracleSecurityID)

    def getOptionPricesTable(self):
        return self.dbInternalHandle.pullOptionPricesTable(self.ticker, self.date)

    def tearDown(self):
        self.dbVendorHandle.disconnect()

    def _setupComparableDFs(self,rawLocalDF,rawVendorDF):
        localIV = rawLocalDF.loc[:, ['TTM', 'CallPut', 'Strike', 'ImpliedVol', 'OptionPrice']]

        #vendorIV = rawVendorDF.loc[:,
        #           ['Days', 'CallPut', 'ImpliedStrike', 'ImpliedVolatility', 'ImpliedPremium']]

        vendorIV = rawVendorDF.loc[:,
                   ['TTM', 'CallPut', 'Strike', 'DBImpVol', 'AveragePrice']]

        vendorIV.rename(columns={'DBImpVol': 'ImpliedVol',
                                 'AveragePrice': 'OptionPrice'}, inplace=True)

        vendorMoneyness = localIV['Strike'].values / self.spotPrice     #Using vendor spotPrice!!
        localIV['Moneyness']=localIV['Strike'].values / self.spotPrice
        vendorIV['Moneyness']=vendorIV['Strike'].values / self.spotPrice

        vendorIV.loc[vendorIV.ImpliedVol==-99,'ImpliedVol'] = 0.0

        return (localIV,vendorIV)

    def test_testTrinomialWithBisection(self):
        IVCalculator = ImpliedVolatilityCalculator(
                                                   'bisection',
                                                   'Trinomial',
                                                   self.zCurve,
                                                   self.dividendYield,
                                                   self.optionPricesTable,
                                                   self.date,
                                                   self.MIN_TTM,
                                                   self.ROOT_FINDER_MAX_ITER,
                                                   self.PRICER_MAX_ITER)
        IVPointwise = IVCalculator.calculateImpliedVol()
        """
        Criteria was discussed in https://jira.axiomainc.com/browse/RISK-2311
        Reference paper: Modelling the implied volatility surface an empirical study for FTSE options - Alentorn 2004
        Link: ...\Phoenix-Research\QPRA\ImpliedVolatilityPython\References\Modelling the implied volatility surface an empirical study for FTSE options - Alentorn 2004.pdf
        """
        localIV, vendorIV = self._setupComparableDFs(IVPointwise,self.benchmarkSurface)

        localSmiles=dict()
        vendorSmiles=dict()
        #Dimensions to be used for different vol smiles
        '''
        ToDo:
        * TTMs between local and vendor do not match!!!
        * IvyDB ImpliedStrike != EJV Option Strike
        '''
        availableTTMs=set(vendorIV['TTM'].values)
        availablePutCall=['C','P']
        for ttm in availableTTMs:
            for putCall in availablePutCall:
                localSmiles[(putCall,ttm)]=localIV[(localIV["CallPut"]==putCall) & (localIV["TTM"]==ttm)].loc[:,['Moneyness','ImpliedVol']]
                vendorSmiles[(putCall,ttm)]=vendorIV[(vendorIV["CallPut"]==putCall) & (vendorIV["TTM"]==ttm)].loc[:,['Moneyness','ImpliedVol']]
                #polynomial = PolynomialFeatures(degree=2).fit_transform(localSmiles[(putCall,ttm)]['Moneyness'].values)
                #model = sm.OLS(localSmiles[(putCall,ttm)]['ImpliedVol'].values, polynomial).fit()

                #What are we regressing!?
                # vendor vs model or model itself???

                model = sm.OLS(localSmiles[(putCall, ttm)]['ImpliedVol'].values, vendorSmiles[(putCall, ttm)]['ImpliedVol'].values).fit()
                print(model.params)

                #model... Obtain parameters
