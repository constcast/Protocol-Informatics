import curses
import statistics
import common
#from peekable import peekable
from curses.ascii import isprint
from tokenrepresentation import TokenRepresentation

class Message:
    """ 
    This class is the base class used for operating on the sequences read from input files
    It contains the payload as well as the tokenized elements and their representation.
    Tokenization is performed according to Cui et al's paper "Discoverer" 
    
    The token represenation (list of tuples) can be obtained via get_tokenlist
    This representation's format is as follows:
        * type of token: text or binary
        * the token itself (enclosed in "" for a text token or prefixed with "0x" for a binary token
        * the start position of the token in the original sequence
        * the length of the token
    
    The messages abstract type representation (sum of types of their token tuples) can be obtained
    via get_tokenrepresentation()
    
    """
    # "Enums" for the token types
    typeText = "text"
    typeBinary = "binary"
    
    eolDelimiter = "^M^J"
       
    def __repr__ (self): 
        return 'Msg: "%s" %s' % (self.__message, self.__tokenlist)
     
    def __init__(self, payload, connident, mnumber, config):
        if len(payload)>config.maxMessagePrefix:
            # Strip payload to maxMessagePreif
            self.__payload = payload[0:config.maxMessagePrefix]
        else:
            self.__payload = payload
        self.__connident = connident
        self.__msgnumber = mnumber
        self.__message = ""
        self.__config = config
        self.__tokenlist = []
        self.__analyze()
        self.__convertPayload()
        self.__payloadhash = common.hash(self.__payload)        
        
    def __convertPayload(self):
        for i in self.__payload:
            if isprint(chr(i)):
                self.__message += chr(i)
            else:
                self.__message += '.'

    def get_length(self):
        return len(self.__payload)
        
    def get_message(self):
        return self.__message
    
    def get_payload(self):
        """Returns the payload of this message object"""        
        return self.__payload
    
    def get_tokenAt(self, idx):
        """
        Returns the token at position idx
        """
        return self.__tokenlist[idx]
    
    def insert_tokenAt(self,idx,token):
        """
        Inserts token at position idx, shifting all the remaining tokens to the right
        """
        self.__tokenlist.insert(idx, token)
        
    def remove_tokenAt(self,idx):
        """
        Removes the token at position idx from tokenlist
        """
        self.__tokenlist.pop(idx)
        
    def get_tokenAtPos(self, pos):
        """
        Returns the token associated with a certain position pos in the payload
        """
        for token in self.__tokenlist:
            if token.get_startsAt()==pos or token.get_startsAt()+token.get_length()>=pos:
                return token
        return None
    
    def get_tokenlist(self):
        return self.__tokenlist
    
    def get_tokenrepresentation(self):
        """
        Returns the token representation as a tuple
        """
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
        num_printable = 0
        num_binary = 0
        startsWithText = False
        
        for char in self.__payload:
            if curses.ascii.isprint(char):
                if num_printable==0 and num_binary == 0:
                    startsWithText = True
                num_printable += 1
                if lastIsBinary:
                    lastIsBinary = False;                   
                    textSegment = ""
                    startsAt = curPos
                textSegment+=chr(char)               
            else:
                num_binary += 1
                if not lastIsBinary: 
                    # We finished a text segment now, now tokenize again
                    self.__tokenlist.extend(self.tokenizeTextSegment(textSegment, startsAt))                        
                    lastIsBinary = True
                self.__tokenlist.append(TokenRepresentation(Message.typeBinary, char, curPos, 1))                    
            curPos+=1
        # Finish unfinished text segments
        if not lastIsBinary:
            # We finish a word now
            self.__tokenlist.extend(self.tokenizeTextSegment(textSegment, startsAt))
        statistics.update_statistics(num_printable, num_binary, startsWithText)       
    
    #===========================================================================
    # def __analyze2(self):
    #    # Bro gives us explicit information about text and binary data by using a '\' and '^' prefix
    #    
    #    
    #    messageIterator = peekable(self.__payload)
    #    startsAt = -1
    #    textStarts = 0
    #    textToken = ""
    #    while not messageIterator.isLast():
    #        current = messageIterator.next()
    #        startsAt+=1
    #        if current=='\\' or current=='^':
    #            # Check for end of textToken
    #            if not textToken == "":
    #                self.__tokenlist.extend(self.tokenizeTextSegment2(textToken, textStarts ))
    #            textToken = ""
    #            textStarts = -1
    #        if current=='\\':
    #            nextItem = messageIterator.peek()
    #            if nextItem=='x':
    #                l = messageIterator.next(3)[1:3]
    #                temp = "".join(l)                    
    #                value = int(temp,16) # Convert hex to decimal
    #                #startsAt+=2 Do not increase because we remove a coded char
    #                self.__tokenlist.append(TokenRepresentation(Message.typeBinary, value, startsAt, 1)) 
    #            elif nextItem=='0':
    #                messageIterator.next()
    #                #startsAt+=1 Do not increase because we remove a control char
    #                value = 0
    #                self.__tokenlist.append(TokenRepresentation(Message.typeBinary, value, startsAt, 1))
    #            else:
    #                print "Parsing error: Read '\\' and expected 'x' or '0' but got '", nextItem, "'"
    #                print "Message was: ", self.__payload
    #        elif current=='^':
    #            nextItem = messageIterator.peek()                
    #            if nextItem>='A' and nextItem<='Z':
    #                # Control char
    #                nextItem = messageIterator.next()
    #                #startsAt+=1 See above
    #                value = ord(nextItem)-0x40 # 
    #                self.__tokenlist.append(TokenRepresentation(Message.typeBinary, value, startsAt, 1))
    #            else:
    #                print "Parsing error: Read '^' and expected [A-Z] but got '", nextItem, "'"
    #        else:
    #            if textToken == "":
    #                textStarts=startsAt
    #            textToken+=current
    #            
    #===========================================================================
        
    def convertTextSegmentToBinaryToken(self, textSegment, startsAt):
        """
        Creates binary tokens out of each char in textSegment
        """
        offset = 0
        tokenList = []
        for item in textSegment:
            tokenList.append(TokenRepresentation(Message.typeBinary, ord(item), startsAt + offset, 1))
        return tokenList
    
    def tokenizeTextSegment(self, textSegment, startsAt):
        """
        Tokenizes textSegment, creating new text resp. binary tokens from it
        Tokens are separated by whitespaces
        """
        # TODO: Should we add explicit whitespace tokens as well?
        if len(textSegment)<self.__config.minWordLength:
            # Word length to short
            # Create artificially binary token
            return self.convertTextSegmentToBinaryToken(textSegment,startsAt)   
        tokens = textSegment.split()
        tokenList = []
        lastLength = 0
        for t in tokens: 
            #===================================================================
            # tail = t
            # while not tail == "":
            #    comp = tail
            #    (head, sep, tail) = tail.partition(Message.eolDelimiter) # Make ^M^J two separate tokens
            #    tokenList.append(TokenRepresentation(Message.typeText, head, startsAt+lastLength+1, len(head)))
            #    lastLength += len(head)
            #    if head==comp: # Our eol sequence was not included in the token, so go to the next one
            #        break
            #    # Add the eol characters
            #    tokenList.append(TokenRepresentation(Message.typeBinary, 0xd, startsAt+lastLength+1, 1))
            #    tokenList.append(TokenRepresentation(Message.typeBinary, 0xa, startsAt+lastLength+2, 1))       
            #===================================================================
            tokenStartPos = startsAt+lastLength
            if not lastLength == 0: # Add whitespace gap for every token but the first
                tokenStartPos += 1
            tokenList.append(TokenRepresentation(Message.typeText, t, tokenStartPos, len(t)))
            lastLength+=len(t)
        return tokenList           
    
    #===========================================================================
    # def tokenizeTextSegment2(self, textSegment, startsAt):        
    #    tokens = textSegment.split()
    #    tokenList = []
    #    lastLength = -1
    #    for t in tokens:             
    #        tokenList.append(TokenRepresentation(Message.typeText, t, startsAt+lastLength+1, len(t)))
    #        lastLength = len(t)
    #    return tokenList           
    # 
    #===========================================================================
