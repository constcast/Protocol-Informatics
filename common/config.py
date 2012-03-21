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
        self.format = "pcap"
        self.weight = float(1.0)
        self.graph = False
        self.maxMessages = 50
        self.ethOffset = 14
        self.messageDelimiter = None
        self.fieldDelimiter = None
        self.textBased = False
        self.configFile = None
        self.analysis = None
        self.gnuplotFile = None
        self.onlyUniq = False
        self.interactive = True
        self.inputFile = None
        # New for "Discoverer"
        self.minWordLength = 3        
        self.maxMessagePrefix = 2048
        self.minimumClusterSize = 5
        self.maxDistinctFDValues = 5
        self.requireTotalLengthChangeForLengthField = False
        self.dumpFile = "discoverer_dump.txt"
        self.breakSequences = False
        self.breakSequenceAt = "0d0a"
        self.loadClientAndServerParts = False
        self.minimizeDFA = False
        self.debug = False
        self.weightEdges = True
        self.mergeSimilarClusters = False
        self.considerOneMessageAsConstant = False
        self.nativeReverXStage1 = False
        self.fastReverXStage1 = True
        self.performReverXMinimization = False
        self.collapseFinals = True
        self.pruneBelowLinkScore = 2
        self.pruneDFAOutliers = False
        self.highlightOutlier = True
        self.testFile = None
        self.flowsMustBeStrictlyAlternating = True
        self.performReverXStage2 = False
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

