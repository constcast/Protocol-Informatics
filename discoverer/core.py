import curses

class Message:
    # "Enums" for the token types
    typeText = 0
    typeBinary = 1
       
    def __repr__ (self): 
        return 'Msg: %s' % (self.tokenlist)
     
    def __init__(self, payload, config):
        self._payload = payload
        self._config = config
        self.tokenlist = []
        self._analyze()
        
    def get_payload(self):
        """Returns the payload of this message object"""
        return self._payload
    
    def get_tokenlist(self):
        return self.tokenlist
    
    def get_tokenrepresentation(self):
        l = []
        for type,raw,start,end in self.tokenlist:
            l.append(type)
        t = tuple(l)
        return t
    
    def get_tokenrepresentation_string(self):
        l = []
        map = {0:"text", 1:"binary"}
        for type,raw,start,end in self.tokenlist:
            l.append(map[type])
        t = tuple(l)
        return t
      
    def _analyze(self):
        # Loop through the payload, memorize the index and create appropriate tupel
        lastIsBinary = True
        textSegmentLength = 0
        textSegment = ""
        curPos = 0
        startsAt = 0
        for char in self._payload:
            curPos+=1
            #if self._config.ASCIILowerBound<=char and self._config.ASCIIUpperBound>=char:
            if curses.ascii.isprint(char):
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
                        # Create artificially binary token
                        offset = 0
                        for item in textSegmentLength:
                            tupel = (self.typeBinary, item, startsAt+offset, 1)
                            self.tokenlist.append(tupel)
                            
                    else:
                        # We finish a word now, now tokenize again
                        token = textSegment.split()
                        lastLength = -1
                        for t in token: # Make ^M^J two separate tokens
                            (head, sep, tail) = t.partition("^M^J")
                            tupel = (self.typeText, head, startsAt+lastLength+1, len(head))
                            self.tokenlist.append(tupel)
                            lastLength += len(head)
                            if head==t:                    
                                continue
                            else:                        
                                while not tail == "":
                                    (head, sep, tail) = tail.partition("^M^J")
                                    tupel = (self.typeText, head, startsAt+lastLength+1, len(head))
                                    self.tokenlist.append(tupel)
                                    lastLength += len(head)
                                tupel = (self.typeBinary, 0xd, startsAt+lastLength+1, 1)
                                self.tokenlist.append(tupel)
                                tupel = (self.typeBinary, 0xa, startsAt+lastLength+2, 1)
                                self.tokenlist.append(tupel)
                        #print tupel
                        
                else: # we read a binary
                    
                    tupel = (self.typeBinary, char, curPos, 1)
                    self.tokenlist.append(tupel)
                    #print tupel

                lastIsBinary = True
        # Finish unfinished text segments
        if not lastIsBinary:
            if textSegmentLength<self._config.minWordLength:
                print "Word length to short"
            else:
                # We finish a word now
                token = textSegment.split()
                lastLength = -1
                for t in token:
                    (head, sep, tail) = t.partition("^M^J")
                    tupel = (self.typeText, head, startsAt+lastLength+1, len(head))
                    self.tokenlist.append(tupel)
                    lastLength += len(head)
                    if head==t:                    
                        continue
                    else:                        
                        while not tail == "":
                            (head, sep, tail) = tail.partition("^M^J")
                            tupel = (self.typeText, head, startsAt+lastLength+1, len(head))
                            self.tokenlist.append(tupel)
                            lastLength += len(head)
                        tupel = (self.typeBinary, 0xd, startsAt+lastLength+1, 1)
                        self.tokenlist.append(tupel)
                        tupel = (self.typeBinary, 0xa, startsAt+lastLength+2, 1)
                        self.tokenlist.append(tupel)
                #print tupel
            