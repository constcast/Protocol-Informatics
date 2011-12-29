class Message:
    # "Enums" for the token types
    typeText = 0
    typeBinary = 1
    
    _payload = None
    tokenlist = []
    
    def __init__(self, payload, config):
        self._payload = payload
        self._config = config
        self._analyze()
        
    def get_payload(self):
        """Returns the payload of this message object"""
        return self._payload
    
    def _analyze(self):
        # Loop through the payload, memorize the index and create appropriate tupel
        lastIsBinary = True
        textSegmentLength = 0
        textSegment = ""
        curPos = 0
        startsAt = 0
        for char in self._payload:
            curPos+=1
            if self._config.ASCIILowerBound<=char and self._config.ASCIIUpperBound>=char:
                if lastIsBinary:
                    lastIsBinary = False;
                    textSegmentLength = 0
                    textSegment = ""
                    startsAt = curPos
                textSegmentLength+=1
                textSegment+=chr(char)               
            else:
                if not lastIsBinary: # we finish a text segment
                    if textSegmentLength<self._config.minWordLength:
                        print "Word length to short"
                    else:
                        # We finish a word now
                        tupel = (self.typeText, textSegment, startsAt, textSegmentLength)
                        self.tokenlist.append(tupel)
                        print tupel
                        
                else: # we read a binary
                    
                    tupel = (self.typeBinary, char, curPos, 1)
                    self.tokenlist.append(tupel)
                    print tupel

                lastIsBinary = True
        # Finish unfinished text segments
        if not lastIsBinary:
            if textSegmentLength<self._config.minWordLength:
                print "Word length to short"
            else:
                # We finish a word now
                tupel = (self.typeText, textSegment, startsAt, textSegmentLength)
                self.tokenlist.append(tupel)
        print self.tokenlist
            