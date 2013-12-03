import unittest, sys, time
sys.path.extend(['.','..','../..','py'])
import h2o, h2o_hosts, h2o_cmd, h2o_import as h2i, h2o_common, h2o_print, h2o_rf

# RF train parameters
paramsTrainRF = { 
    'ntrees': 5, 
    'max_depth': 15,
    'nbins': 100,
    'ignored_cols_by_name': 'AirTime, ArrDelay, DepDelay, CarrierDelay, IsArrDelayed', 
    'timeoutSecs': 14800,
    }

# RF test parameters
paramsScoreRF = {
    # scoring requires the response_variable. it defaults to last, so normally
    # we don't need to specify. But put this here and (above if used) 
    # in case a dataset doesn't use last col 
    'response_variable': None,
    'timeoutSecs': 14800,
    }

trainDS = {
    'csvFilename' : 'airlines_all.csv',
    'timeoutSecs' : 14800,
    'header'      : 1
    }

# FIX should point to a different smaller dataset
scoreDS = {
    'csvFilename' : 'airlines_all.csv',
    'timeoutSecs' : 14800,
    'header'      : 1
    }

PARSE_TIMEOUT=14800

class releaseTest(h2o_common.ReleaseCommon, unittest.TestCase):

    def parseFile(self, importFolderPath='datasets', csvFilename='airlines_all.csv', 
        timeoutSecs=500, **kwargs):
        csvPathname = importFolderPath + "/" + csvFilename

        start = time.time()
        parseResult = h2i.import_parse(path=csvPathname, schema='hdfs', timeoutSecs=timeoutSecs)
        elapsed = time.time() - start
        print "Parse of", parseResult['destination_key'], "took", elapsed, "seconds"
        parseResult['python_call_timer'] = elapsed
        print "Parse result['destination_key']:", parseResult['destination_key']

        start = time.time()
        inspect = h2o_cmd.runInspect(None, parseResult['destination_key'], timeoutSecs=200)
        elapsed = time.time() - start
        print "Inspect:", parseResult['destination_key'], "took", elapsed, "seconds"
        h2o_cmd.infoFromInspect(inspect, csvPathname)
        numRows = inspect['numRows']
        numCols = inspect['numCols']
        print "numRows:", numRows, "numCols", numCols
        return parseResult

    def loadTrainData(self):
        kwargs   = trainDS.copy()
        trainParseResult = self.parseFile(**kwargs)
        return trainParseResult
    
    def loadScoreData(self):
        kwargs   = scoreDS.copy()
        scoreParseResult = self.parseFile(**kwargs)
        return scoreParseResult 

    def test_c8_rf_airlines_hdfs(self):
        trainParseResult = self.loadTrainData()
        kwargs   = paramsTrainRF.copy()
        trainResult = h2o_rf.trainRF(trainParseResult, **kwargs)

        scoreParseResult = self.loadScoreData()
        kwargs   = paramsScoreRF.copy()
        scoreResult = h2o_rf.scoreRF(scoreParseResult, trainResult, **kwargs)

if __name__ == '__main__':
    h2o.unit_main()
