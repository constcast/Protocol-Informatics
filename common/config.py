class Configuration:
    def __init__(self, filename):
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

        cf = file(filename, 'r')
        self.config = yaml.load(cf)
        self.checkConfig()

    def checkConfig(self):
        # extract necessary config parameters from config file
        if 'weight' in  self.config:
            self.weight = config['weight']

        if 'onlyUniqMessages' in self.config:
            self.onlyUniq = self.config['onlyUniqMessages']

        if 'format' in  self.config:
            self.format = self.config['format']
        
        if 'maxMessages' in self.config:
            maxMessages = int(self.config['maxMessages'])

        if 'analysis' in self.config:
            self.analysis = config['analysis']

        if 'graph' in config:
            graph = config['graph']

    if 'textBased' in config:
        textBased = config['textBased']

    if 'messageDelimiter' in config:
        messageDelimiter = config['messageDelimiter']

    if 'fieldDelimiter' in config:
        fieldDelimiter = config['fieldDelimiter']

    if 'entropyGnuplotFile' in config:
        gnuplotFile = config['entropyGnuplotFile']

    if weight < 0.0 or weight > 1.0:
        print "FATAL: Weight must be between 0 and 1"
        sys.exit(-1)

