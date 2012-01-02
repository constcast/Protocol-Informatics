import curses
import string
from peekable import peekable

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
    
    def get_tokenAt(self, idx):
        return self.__tokenlist[idx]
    
    def get_tokenlist(self):
        return self.__tokenlist
    
    def get_tokenrepresentation(self):
        l = []
        for tokenRepresentation in self.__tokenlist:
            l.append(tokenRepresentation.get_tokenType())
        t = tuple(l)
        return t
      
    #===========================================================================
    # def __analyze(self):
    #    # Loop through the payload, memorize the index and create appropriate tupel
    #    lastIsBinary = True
    #    textSegment = ""
    #    curPos = 0
    #    startsAt = 0
    #    for char in self.__payload:
    #        curPos+=1
    #        if curses.ascii.isprint(char):
    #            if lastIsBinary:
    #                lastIsBinary = False;                   
    #                textSegment = ""
    #                startsAt = curPos
    #            textSegment+=chr(char)               
    #        else:
    #            if not lastIsBinary: 
    #                # We finished a text segment now, now tokenize again
    #                self.__tokenlist.extend(self.tokenizeTextSegment(textSegment, startsAt))                        
    #            else:
    #                self.__tokenlist.extend(TokenRepresentation(Message.typeBinary, char, curPos, 1))    
    #            lastIsBinary = True
    #    # Finish unfinished text segments
    #    if not lastIsBinary:
    #        # We finish a word now
    #        self.__tokenlist.extend(self.tokenizeTextSegment(textSegment, startsAt))
    #            
    #===========================================================================
    
    def __analyze(self):
        # Bro gives us explicit information about text and binary data by using a '\' and '^' prefix
        
        # TODO: What is the length of a binary token of 1 Byte? 1 or 2? Presume 1
        messageIterator = peekable(self.__payload)
        startsAt = -1
        textStarts = 0
        textToken = ""
        while not messageIterator.isLast():
            current = messageIterator.next()
            startsAt+=1
            if current=='\\' or current=='^':
                # Check for end of textToken
                if not textToken == "":
                    self.__tokenlist.extend(self.tokenizeTextSegment2(textToken, textStarts ))
                textToken = ""
                textStarts = -1
            if current=='\\':
                nextItem = messageIterator.peek()
                if nextItem=='x':
                    l = messageIterator.next(3)[1:3]
                    temp = "".join(l)                    
                    value = int(temp,16) # Convert hex to decimal
                    #startsAt+=2 Do not increase because we remove a coded char
                    self.__tokenlist.append(TokenRepresentation(Message.typeBinary, value, startsAt, 1)) 
                elif nextItem=='0':
                    messageIterator.next()
                    #startsAt+=1 Do not increase because we remove a control char
                    value = 0
                    self.__tokenlist.append(TokenRepresentation(Message.typeBinary, value, startsAt, 1))
                else:
                    print "Parsing error: Read '\\' and expected 'x' or '0' but got '", nextItem, "'"
                    print "Message was: ", self.__payload
            elif current=='^':
                nextItem = messageIterator.peek()                
                if nextItem>='A' and nextItem<='Z':
                    # Control char
                    nextItem = messageIterator.next()
                    #startsAt+=1 See above
                    value = ord(nextItem)-0x40 # 
                    self.__tokenlist.append(TokenRepresentation(Message.typeBinary, value, startsAt, 1))
                else:
                    print "Parsing error: Read '^' and expected [A-Z] but got '", nextItem, "'"
            else:
                if textToken == "":
                    textStarts=startsAt
                textToken+=current
                
        
    def convertTextSegmentToBinaryToken(self, textSegment, startsAt):
        offset = 0
        tokenList = []
        for item in textSegment:
            tokenList.append(TokenRepresentation(Message.typeBinary, item, startsAt + offset, 1))
        return tokenList
    
    #===========================================================================
    # def tokenizeTextSegment(self, textSegment, startsAt):
    #    if len(textSegment)<self.__config.minWordLength:
    #        # Word length to short
    #        # Create artificially binary token
    #        return self.convertTextSegmentToBinaryToken(textSegment,startsAt)   
    #    tokens = textSegment.split()
    #    tokenList = []
    #    lastLength = -1
    #    for t in tokens: 
    #        tail = t
    #        while not tail == "":
    #            comp = tail
    #            (head, sep, tail) = tail.partition(Message.eolDelimiter) # Make ^M^J two separate tokens
    #            tokenList.append(TokenRepresentation(Message.typeText, head, startsAt+lastLength+1, len(head)))
    #            lastLength += len(head)
    #            if head==comp: # Our eol sequence was not included in the token, so go to the next one
    #                break
    #            # Add the eol characters
    #            tokenList.append(TokenRepresentation(Message.typeBinary, 0xd, startsAt+lastLength+1, 1))
    #            tokenList.append(TokenRepresentation(Message.typeBinary, 0xa, startsAt+lastLength+2, 1))       
    #    return tokenList           
    #===========================================================================
    
    def tokenizeTextSegment2(self, textSegment, startsAt):        
        tokens = textSegment.split()
        tokenList = []
        lastLength = -1
        for t in tokens:             
            tokenList.append(TokenRepresentation(Message.typeText, t, startsAt+lastLength+1, len(t)))
            lastLength = len(t)
        return tokenList           
    
