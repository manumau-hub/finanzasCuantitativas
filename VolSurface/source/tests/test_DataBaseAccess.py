from unittest import TestCase,skip
import numpy as np
import sys
from DataBaseAccess import DatabaseAccess
from tests.testing_tools import TestResultsXMLHandler

class PandoraDBAccessTests(TestCase):
    OVERWRITE_BASELINES=True
    TEST_DATE='2019-04-04'
    APPL_SEC_ID='DQ8L3JXGU111'
    APPL_AXIOMA_ID='KDWC2FL4X1'

    def setUp(self):
        self.dbHandler = DatabaseAccess.createInstanceOfDatabaseAccess('Pandora')

    def test_vendorName(self):
        self.assertEqual(self.dbHandler.vendorName(),'Pandora')

    def test_getSecurityIDFromTicker(self):
        result=self.dbHandler.getSecurityIDFromTicker('AAPL',date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getAxiomaIdFromTicker(self):
        result = self.dbHandler.getAxiomaIdFromTicker('AAPL',date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_pullOptionPricesTableWithStock(self):
        result=self.dbHandler.pullOptionPricesTable('AAPL', date =self.TEST_DATE)
        valueToStore=TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,'Symbol')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    @skip('Takes way too long')
    def test_pullOptionPricesTableWithStockIndex(self):
        result=self.dbHandler.pullOptionPricesTable('SPX', date =self.TEST_DATE)
        valueToStore=TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,'Symbol')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_pullLastNDaysOfOptionPricesWithStock(self):
        #Get last 2 days of option prices
        result=self.dbHandler.pullLastNDaysOfOptionPrices('AAPL', numdays=2, date=self.TEST_DATE)
        valueToStore=TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,'ric')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    @skip('Takes way too long')
    def test_pullLastNDaysOfOptionPricesWithStockIndex(self):
        #Get last 2 days of option prices
        result=self.dbHandler.pullLastNDaysOfOptionPrices('SPX', numdays=2, date=self.TEST_DATE)
        valueToStore=TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,'ric')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_getOptionExerciseStyleWithStock(self):
        result=self.dbHandler.getOptionExerciseStyle('AAPL',date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getOptionExerciseStyleWithStockIndex(self):
        result=self.dbHandler.getOptionExerciseStyle('SPX',date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_isIndex(self):
        self.assertTrue(self.dbHandler.isIndex('SPX'))
        self.assertFalse(self.dbHandler.isIndex('AAPL'))

    def test_pullSpotTableFromTickerWithStock(self):
        result = self.dbHandler.pullSpotTableFromTicker('AAPL', numdays=10,date=self.TEST_DATE)
        valueToStore=TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,'Date')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_pullSpotTableFromTickerWithStockIndex(self):
        result = self.dbHandler.pullSpotTableFromTicker('SPX', numdays=10,date=self.TEST_DATE)
        valueToStore=TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,'Date')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_pullZCurve(self):
        result = self.dbHandler.pullZCurve(date=self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result, 'Inyears')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)
    def test_getUnderlyingSpotPriceFromSecurityID(self):
        result=self.dbHandler.getUnderlyingSpotPriceFromSecurityID(self.APPL_SEC_ID,date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getUnderlyingSpotPriceFromTickerWithStock(self):
        result = self.dbHandler.getUnderlyingSpotPriceFromTicker('AAPL', date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getUnderlyingSpotPriceFromTickerWithStockIndex(self):
        result = self.dbHandler.getUnderlyingSpotPriceFromTicker('SPX', date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getDividendYieldFromSecurityID(self):
        result=self.dbHandler.getDividendYieldFromSecurityID(self.APPL_SEC_ID,self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getDividendYieldFromTickerWithStock(self):
        result=self.dbHandler.getDividendYieldFromTicker('AAPL',self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getDividendYieldFromTickerWithStockIndexAndFailReturning0(self):
        result=self.dbHandler.getDividendYieldFromTicker('SPX',self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_pullDividendListFromTicker(self):
        result=self.dbHandler.pullDividendListFromTicker('AAPL',self.TEST_DATE)
        valueToStore=TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,'RecordDate')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_getLastDividendFromTicker(self):
        result = self.dbHandler.getLastDividendFromTicker('AAPL', self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_calculateZCurveReplication(self):
        result=self.dbHandler.calculateZCurveReplication(self.TEST_DATE).Rate.values.tolist()
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)


class VendorDBAccessTests(TestCase):
    #OVERWRITE_BASELINES=True
    TEST_DATE = '2019-04-04'
    APPL_SEC_ID = '101594'
    APPL_AXIOMA_ID = 'KDWC2FL4X1'

    def setUp(self):
        self.dbHandler = DatabaseAccess.createInstanceOfDatabaseAccess('Vendor')

    def test_vendorName(self):
        self.assertEqual(self.dbHandler.vendorName(), 'Vendor')

    def test_getSecurityIDFromTicker(self):
        result=self.dbHandler.getSecurityIDFromTicker('AAPL',date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getTickerFromSecurityID(self):
        result = self.dbHandler.getTickerFromSecurityID(self.APPL_SEC_ID)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getOptionExerciseStyle(self):
        result = self.dbHandler.getOptionExerciseStyle(self.APPL_SEC_ID)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_pullOptionPricesTable(self):
        result=self.dbHandler.pullOptionPricesTable(self.APPL_SEC_ID,date=self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result, 'Symbol')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_pullOptionPricesOfTicker(self):
        result = self.dbHandler.pullOptionPricesOfTicker('AAPL', date=self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result, 'Symbol')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_pullZCurve(self):
        result=self.dbHandler.pullZCurve(self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result, 'TTM')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_pullVolatilitySurfaceOfSecurityID(self):
        result=self.dbHandler.pullVolatilitySurfaceOfSecurityID(self.APPL_SEC_ID,date=self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result, ['CallPut','Delta','Days'])
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_pullVolatilitySurfaceOfTicker(self):
        result = self.dbHandler.pullVolatilitySurfaceOfSecurityID(self.APPL_SEC_ID,
                                                                  date=self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,
                                                                                    ['CallPut', 'Delta', 'Days'])
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_isIndex(self):
        self.assertTrue(self.dbHandler.isIndex('108105'))
        self.assertFalse(self.dbHandler.isIndex(self.APPL_SEC_ID))

    def test_getSecurityIDFromCUSIP(self):
        result = self.dbHandler.getSecurityIDFromCUSIP('03783310')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getOptionInfo(self):
        result = self.dbHandler.getOptionInfo(self.APPL_SEC_ID)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getUnderlyingSpotPriceFromSecurityID(self):
        result = self.dbHandler.getUnderlyingSpotPriceFromSecurityID(self.APPL_SEC_ID,
                                                       date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                 sys._getframe().f_code.co_name,
                                                                 result)

    def test_getUnderlyingSpotPriceFromTicker(self):
        result = self.dbHandler.getUnderlyingSpotPriceFromTicker('AAPL',
                                                       date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                   sys._getframe().f_code.co_name,
                                                                   result)

    def test_pullSpotListFromSecurityId(self):
        result = self.dbHandler.pullSpotListFromSecurityId(self.APPL_SEC_ID, 10, self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result, 'Date')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_pullDividendList(self):
        result = self.dbHandler.pullDividendListFromTicker('AAPL', self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result,'RecordDate')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_getLastDividend(self):
        result = self.dbHandler.getLastDividend('AAPL',date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_getLastExerciseDate(self):
        result = self.dbHandler.getLastExerciseDate(self.APPL_SEC_ID, date=self.TEST_DATE).astype(str)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_pullLastNDaysOptionPriceFromSecurityId(self):
        result = self.dbHandler.pullLastNDaysOptionPriceFromSecurityId(self.APPL_SEC_ID, 2, self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result, 'Symbol')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)

    def test_getDividendYieldFromSecurityID(self):
        #'108105' is SPX
        result = self.dbHandler.getDividendYieldFromSecurityID('108105', date=self.TEST_DATE)
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     result)

    def test_pullNDaysOfVolatilitySurfaceFromSecurityId(self):
        result = self.dbHandler.pullNDaysOfVolatilitySurfaceFromSecurityId(self.APPL_SEC_ID,2, self.TEST_DATE)
        valueToStore = TestResultsXMLHandler.transformDataFrameIntoSerializableList(result, 'Symbol')
        TestResultsXMLHandler.assertEqualIfResultsArePresentOtherwisePersistBaseline(self,
                                                                                     sys._getframe().f_code.co_name,
                                                                                     valueToStore)
