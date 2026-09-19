import json
import inspect
from pathlib import PurePath

#############In PROD, this must remain False#############
SAVE_NEW_BASELINES=True
#########################################################

class TestResultsXMLHandler:
    @classmethod
    def getBaselinePathFromClassInstance(cls, testClassInstance):
        pyFile = inspect.getfile(testClassInstance.__class__)
        className = testClassInstance.__class__.__name__
        pyFileName = PurePath(pyFile).stem
        path = pyFileName + '_' + className + '_baseline.xml'
        return path

    @classmethod
    def saveResultsToXML(cls,testClassInstance,testMethodName,results):
        path=cls.getBaselinePathFromClassInstance(testClassInstance)
        try:
            with open(path, 'r') as f:
                resultsDict = json.load(f)
        except:
            resultsDict={}
        resultsDict[testMethodName]=results

        with open(path, 'w') as f:
            json.dump(resultsDict, f)

    @classmethod
    def loadResultsFromXML(cls,testClassInstance,testMethodName):
        path=cls.getBaselinePathFromClassInstance(testClassInstance)
        try:
            with open(path, 'r') as f:
                resultsDict = json.load(f)
        except:
            print("Could not find baseline file {0}. Creating a new one.".format(path))
            return
        return resultsDict.get(testMethodName)

    @classmethod
    def assertEqualIfResultsArePresentOtherwisePersistBaseline(cls,testClassInstance,testMethodName,actualResult):
        expectedResults=cls.loadResultsFromXML(testClassInstance,testMethodName) if not getattr(testClassInstance,'OVERWRITE_BASELINES',False) else None
        testPath=testClassInstance.__class__.__name__+'.'+testMethodName
        if expectedResults:
            print("Found baseline for test {0}. Asserting...".format(testPath))
            testClassInstance.assertEqual(actualResult,expectedResults)
        else:
            if SAVE_NEW_BASELINES:
                print("Storing baseline for test {0}".format(testPath))
                cls.saveResultsToXML(testClassInstance,testMethodName,actualResult)
            else:
                raise(AssertionError("Missing baseline for test {0}".format(testPath)))

    @classmethod
    def transformDataFrameIntoSerializableList(cls,df,sortColumns):
        if isinstance(sortColumns,str):
            sortColumns = [sortColumns]
        return df.sort_values(by=sortColumns).to_records(index=False).tolist()