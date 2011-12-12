import yaml, sys


class Configuration:
    def __init__(self, filename = None):
        # Defaults
        self.format = "pcap"
        self.weight = 1.0
        self.graph = False
        self.maxMessages = 0
        self.messageDelimiter = None
        self.fieldDelimiter = None
        self.textBased = False
        self.configFile = None
        self.analysis = None
        self.gnuplotFile = None
        self.onlyUniq = False
        self.interactive = True
        self.inputFile = None

        if filename != None:
            self.configFile = filename
            self.importConfig(filename)


    def importConfig(self, filename):
        cf = file(filename, 'r')
        self.config = yaml.load(cf)
        self.checkConfig()

    def checkConfig(self):
        # extract necessary config parameters from config file
        if 'weight' in  self.config:
            self.weight = self.config['weight']

        if 'onlyUniqMessages' in self.config:
            self.onlyUniq = self.config['onlyUniqMessages']

        if 'format' in  self.config:
            self.format = self.config['format']
        
        if 'maxMessages' in self.config:
            maxMessages = int(self.config['maxMessages'])

        if 'analysis' in self.config:
            self.analysis = self.config['analysis']

        if 'graph' in self.config:
            self.graph = self.config['graph']

        if 'textBased' in self.config:
            self.textBased = self.config['textBased']

        if 'messageDelimiter' in self.config:
            self.messageDelimiter = self.config['messageDelimiter']

        if 'fieldDelimiter' in self.config:
            self.fieldDelimiter = self.config['fieldDelimiter']

        if 'entropyGnuplotFile' in self.config:
            self.gnuplotFile = self.config['entropyGnuplotFile']

        if 'interactive' in self.config:
            self.interactive = self.config['interactive']
            
        if 'inputFile' in self.config:
            self.inputFile = self.config['inputFile']

        if self.weight < 0.0 or self.weight > 1.0:
            print "FATAL: Weight must be between 0 and 1"
            sys.exit(-1)

