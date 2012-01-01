import curses
import string

from tokenrepresentation import TokenRepresentation
class Message:
    # "Enums" for the token types
    typeText = "text"
    typeBinary = "binary"
    
    eolDelimiter = "^M^J"
       
    def __repr__ (self): 
        return 'Msg: %s %s' % (self.__payload, self.__tokenlist)
     
    def __init__(self, payload, config):
        self.__payload = payload
        self.__config = config
        self.__tokenlist = []
        self.__analyze()
        
    def get_length(self):
        return len(self.__payload)
        
    def get_payload(self):
        """Returns the payload of this message object"""
        return self.__payload
    
    def get_tokenlist(self):
        return self.__tokenlist
    
    def get_tokenrepresentation(self):
        l = []
        for tokenRepresentation in self.__tokenlist:
            l.append(tokenRepresentation.get_tokenType())
        t = tuple(l)
        return t
      
    def __analyze(self):
        # Loop through the payload, memorize the index and create appropriate tupel
        lastIsBinary = True
        textSegment = ""
        curPos = 0
        startsAt = 0
        for char in self.__payload:
            curPos+=1
            if curses.ascii.isprint(char):
                if lastIsBinary:
                    lastIsBinary = False;                   
                    textSegment = ""
                    startsAt = curPos
                textSegment+=chr(char)               
            else:
                if not lastIsBinary: 
                    # We finished a text segment now, now tokenize again
                    self.__tokenlist.extend(self.tokenizeTextSegment(textSegment, startsAt))                        
                else:
                    self.__tokenlist.extend(TokenRepresentation(Message.typeBinary, char, curPos, 1))    
                lastIsBinary = True
        # Finish unfinished text segments
        if not lastIsBinary:
            # We finish a word now
            self.__tokenlist.extend(self.tokenizeTextSegment(textSegment, startsAt))
                
    def convertTextSegmentToBinaryToken(self, textSegment, startsAt):
        offset = 0
        tokenList = []
        for item in textSegment:
            tokenList.append(TokenRepresentation(Message.typeBinary, item, startsAt + offset, 1))
        return tokenList
    
    def tokenizeTextSegment(self, textSegment, startsAt):
        if len(textSegment)<self.__config.minWordLength:
            # Word length to short
            # Create artificially binary token
            return self.convertTextSegmentToBinaryToken(textSegment,startsAt)   
        tokens = textSegment.split()
        tokenList = []
        lastLength = -1
        for t in tokens: 
            tail = t
            while not tail == "":
                comp = tail
                (head, sep, tail) = tail.partition(Message.eolDelimiter) # Make ^M^J two separate tokens
                tokenList.append(TokenRepresentation(Message.typeText, head, startsAt+lastLength+1, len(head)))
                lastLength += len(head)
                if head==comp: # Our eol sequence was not included in the token, so go to the next one
                    break
                # Add the eol characters
                tokenList.append(TokenRepresentation(Message.typeBinary, 0xd, startsAt+lastLength+1, 1))
                tokenList.append(TokenRepresentation(Message.typeBinary, 0xa, startsAt+lastLength+2, 1))       
        return tokenList           