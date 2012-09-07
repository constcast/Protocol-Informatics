import yaml
import sys

def loadConfig(filename):
    cf = file(filename, 'r')
    config = yaml.load(cf)
    return Configuration(config)

def loadConfigFromDict(d):
    return Configuration(d)

def saveConfig(configuration, filename):
    cf = file(filename, 'w')
    yaml.dump(vars(configuration), cf)

class Configuration:
    def __init__(self, d = None):
        # Defaults
        self.format = "bro"
        self.weight = float(1.0)
        self.graph = False
        self.maxFlows = 50
        self.ethOffset = 14
        self.messageDelimiter = None
        self.fieldDelimiter = None
        self.textBased = False
        self.configFile = ""
        self.analysis = None
        self.gnuplotFile = None
        self.onlyUniq = False
        self.interactive = True
        self.inputFile = ""
        # New for "Discoverer"
        self.minWordLength = 3        
        self.maxMessagePrefix = 2048
        self.minimumClusterSize = 5
        self.minDistinctFDValues = 3
        self.maxDistinctFDValues = 35
        self.requireTotalLengthChangeForLengthField = False
        self.dumpFile = "/Users/daubsi/Dropbox"
        self.breakSequences = False
        self.breakSequenceAt = "0d0a"
        self.loadClientAndServerParts = True
        self.minimizeDFA = False
        self.debug = False
        self.weightEdges = True
        self.mergeSimilarClusters = False
        self.considerOneMessageAsConstant = True
        self.nativeReverXStage1 = True
        self.fastReverXStage1 = False
        self.performReverXMinimization = True
        self.collapseFinals = True
        self.pruneBelowLinkScore = 1
        self.pruneDFAOutliers = False
        self.highlightOutlier = True
        self.flowsMustBeStrictlyAlternating = True
        self.performReverXStage2 = True
        self.buildDFAViaRegEx = False
        self.checkConsistencyOnMerge = False
        self.lastMessageIsDirectlyFinal = False
        self.strictMergeOfOutgoingEdges = True
        self.testFile = "/Users/daubsi/Dropbox/ftp_big"
        self.numOfTestEntries = 1000
        self.sessionIDOnlyWithBinary = True
        self.sessionIDOnlyWithClustersWithMoreThanOneMessage = True
        self.printMessagesOfCluster = False
        self.constantsAreCaseSensitive = True
        self.allowAdjacentFDs = True
        self.allowAdjacentTextFDs = False
        self.autoCreateXML = False
        self.calculateMaxMessageLength = False
        self.maxMessageLengthConfidenceInterval = 0.9
        self.danglingRegEx = True
        self.setAbsoluteMax = 5
        self.setPercentageThreshold = 0.3
        self.multipleChoiceChooserClass = "RandomWeightedChooser"
        self.testbasename = "/Users/daubsi/Dropbox/ftp_big_2000"
        self.autoRun = True
	self.autoRunHigh = 18;
        # Used for NW alignment in Discoverer
        self.matchScore = 1
        self.mismatchScore = 1
        self.gapScore = 1

        # update from the config dictionary if available
        if d != None:
            self.__dict__.update(d)
            if not self.checkConfig():
                print "FATAL: Could not initialize from configuration."
                sys.exit(-1)


    def checkConfig(self):
        # do sanity checks
        if self.weight < 0.0 or self.weight > 1.0:
            print "FATAL: Weight must be between 0 and 1"
            return False
        
        if self.maxMessagePrefix<1:
            print "FATAL: maxMessagePrefix must be greater than 0"
            return False
        
        if self.minWordLength<1:
            print "FATAL: MinWordLength must be greater than 0"
            return False
        if self.fastReverXStage1 and self.nativeReverXStage1:
            print "FATAL: 'fastReverXStage1' and 'nativeReverXStage1' must not be both set to True!"
            return True
        return True

    def print_config(self):
        elems = sorted(vars(self))
        maxLen = 40
        for i in elems:
            value = getattr(self,i)
            print i,
            for j in range(maxLen - len(i)):
                print "",
            print str(value),
            for j in range(maxLen - len(str(value))):
                print "", 
            print "\t\t" + str(type(value))

