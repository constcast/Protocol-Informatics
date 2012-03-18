import tokenrepresentation
import common
import formatinference
from message import Message
from peekable import peekable
from formatinference import VariableTextStatistics
from formatinference import VariableNumberStatistics
class Cluster(dict):
    """
    This class represents a cluster of messages.
    Messages are contained in a list and obtained via get_messages()
    New messages can be added via add_messages
    The cluster representation (e.g. "(binary, text, text)") has to be set during the __init__.
    In addition the inferred message format (const vs. variable) is contained in a separate list
    (obtainable via get_format_inference()).
    A filtering function that only returns with a specific value at token position X can be called
    via get_messages_with_value_at()
    """
    def __init__(self, representation):
        self.update({'messages':[], 'representation':representation, 'format_inference':[], 'semantics':{}, 'variable_statistics': []})        
    
    def getVariableStatistics(self):
        if self['variable_statistics']==[]:
            self.calculateVariableStatistics()
        return self['variable_statistics']
    
    def calculateVariableStatistics(self):
        for idx, elem in enumerate(self['format_inference']):
            if elem.getType()==Message.typeVariable:
                stats = None
                if self['representation'][idx]==Message.typeBinary:
                    stats = VariableNumberStatistics()
                else:
                    stats = VariableTextStatistics()
                for m in self.get_messages():
                    tokAt = m.get_tokenAt(idx)
                    val = tokAt.get_token()
                    stats.addValue(val)
                self['variable_statistics'].append(stats)   
            else:
                self['variable_statistics'].append(None)      
                
            
    def clear_semantics(self):
        """
        Removes all the semantic information from the whole cluster
        """
        for k in self.get('semantics'):
            del self.get('semantics')[k]
        
    def clear_semantics_for_token(self,idx):
        """
        Clears the semantic information for the token at position idx
        """        
        if self.get('semantics').has_key(idx):                
            del self.get('semantics')[idx]
    def hasConstToken(self):
        numOfConst = 0
        formats = self.get_formats()
        messages = self.get_messages()
        idx = 0
        for fmt in formats:
            if fmt[1].getType()==Message.typeConst: # format is "const (xyz)"
                value = messages[0].get_tokenAt(idx).get_token()
                if value!=0x0a and value!=0x0d and fmt[0]!=Message.typeDirection:
                    numOfConst += 1
            idx += 1
        return numOfConst>0       
    def getRegEx(self):
        regexstr = "^"
        idx = 0
        iterator = peekable(self.get('format_inference'))
        content_msg = self.get_messages()[0]
        while not iterator.isLast():
            item = iterator.next()
            tokType = self.get('representation')[idx]
            if tokType!=Message.typeDirection:
                token = content_msg.get_tokenAt(idx)
                startsAt = token.get_startsAt()
                length = token.get_length()
                
                if isinstance(item,formatinference.Constant):
                    #if isinstance(item.getConstValue(),str):
                    token = content_msg.get_tokenAt(idx)
                    startsAt = token.get_startsAt()
                    length = token.get_length()
                    
                    payload = content_msg.get_payload()[startsAt:startsAt+length]
                    s = "".join([str(elem) for elem in payload])
                    regexstr += s
                       
                    #===========================================================
                    # if self.get('representation')[idx]==Message.typeText:
                    #     #regexstr += item.getConstValue()
                    # else:
                    #    val = hex(item.getConstValue())[2:]
                    #    if len(val)==1:
                    #        val = "0{0}".format(val)
                    #    regexstr += "\\x{0}".format(val)
                    #===========================================================
                elif isinstance(item,formatinference.Variable):
                    #regexstr += "*?" # Non greedy match
                    regexstr += ".*" # Non greedy match
                
                if not iterator.isLast():
                    nextStart = content_msg.get_tokenAt(idx+1).get_startsAt()
                    if nextStart!=startsAt+length:
                    #if nextOne.get_startsAt()!=startsAt+length+1:
                        regexstr += "(?:20)+"
                #===============================================================
                # if tokType == Message.typeText:
                #    # peek ahead if next is also text
                #    # Add separator for tokenseparator (nothing by bin-bin, bin-text, text-bin but whitespace when text-text
                #    # text-text is separated by \s (whitespace)
                #    nextOne = iterator.peek()
                #    if nextOne!=None:
                #        nextType = self.get('representation')[idx+1]
                #        if nextType == Message.typeText:
                #            #regexstr += "((20)|(08)|(0a)|(0d))?" # Add whitespace token separator
                #            regexstr += "(?:20)+" # Add whitespace token separator                
                #            
                #===============================================================
            idx += 1
        regexstr += "$"
        return regexstr 
        
    def getRegExVisual(self):
        regexstr = "^"
        idx = 0
        iterator = peekable(self.get('format_inference'))
        while not iterator.isLast():
            item = iterator.next()
            tokType = self.get('representation')[idx]
            if tokType!=Message.typeDirection:
                if isinstance(item,formatinference.Constant):
                    #if isinstance(item.getConstValue(),str):
                    if self.get('representation')[idx]==Message.typeText:
                        regexstr += item.getConstValue()
                    else:
                        val = hex(item.getConstValue())[2:]
                        if len(val)==1:
                            val = "0{0}".format(val)
                        regexstr += "\\x{0}".format(val)
                elif isinstance(item,formatinference.Variable):
                    #regexstr += "*?" # Non greedy match
                    regexstr += ".*" # Non greedy match
                if tokType == Message.typeText:
                    # peek ahead if next is also text
                    # Add separator for tokenseparator (nothing by bin-bin, bin-text, text-bin but whitespace when text-text
                    # text-text is separated by \s (whitespace)
                    nextOne = iterator.peek()
                    if nextOne!=peekable.sentinel:
                        nextType = self.get('representation')[idx+1]
                        if nextType == Message.typeText:
                            regexstr += "\s" # Add whitespace token separator                
            idx += 1
        regexstr += "$"
        return regexstr 
                
                        
                
    def has_semantic_for_token(self, idx, semantic):
        """
        Checks whether the token at position idx has a given semantic
        """
        if not self.get('semantics').has_key(idx):
            return False
        try:
            return 0<=self.get('semantics')[idx].index(semantic)
        except:
            return False
    def set_semantics(self, semantics):
        """
        Replaces current semantics for the whole cluster
        """
        self.clear_semantics()
        self.get('semantics').update(semantics)

    def add_semantics(self, semantics):
        """
        Extends current semantics of cluster with another list of semantics
        """
        self.get('semantics').extend(semantics)        
        
    def add_semantic_for_token(self, idx, semantic):
        """
        Adds a single semantic for token at idx
        """
        if not self.get('semantics').has_key(idx):
            self.get('semantics')[idx] = set() #[]
        #self.get('semantics')[idx].append(semantic)
        self.get('semantics')[idx].add(semantic)
        
    def get_semantics(self):
        """
        Gets semantics for whole cluster
        """
        return self.get('semantics')
    
    def get_semantics_for_token(self, idx):
        """
        Gets semantics for token at idx
        """
        if self.get('semantics').has_key(idx):
            return self.get('semantics')[idx]
        return []
        
    def getFormatHash(self):
        """
        Returns the hash of the format inference incl. const values
        """
        import hashlib
        return hashlib.sha1(str(self.get_formats())).hexdigest()
    
    def get_formats(self):
        """
        Returns a list of all the format representations of the cluster
        """
        formats = []
        for i in range(0,len(self.get('representation'))):
            formats.append(self.get_format(i))
        return formats
    
    def get_format(self, idx):
        """
        Returns a tuple of format data for a given token consisting of
        * text/binary classification
        * the inferred format (constant vs. variable)
        * its semantics
        """
        s = []
        if self.get('semantics').has_key(idx):
            s.extend(self.get('semantics')[idx]) # Take all strings from the set and add them to the list
            
        if len(self.get('format_inference'))>idx:
            #t = "{0}".format(self.get('format_inference')[idx])
            t = self.get('format_inference')[idx]
        else:
            t = None
        return (self.get('representation')[idx], t,s)
    
        
        #if self.get('semantics').has_key(idx):
        #    return (self.get('representation')[idx], self.get('format_inference')[idx], set(self.get('semantics')[idx]))
        #else: 
        #    return (self.get('representation')[idx], self.get('format_inference')[idx],[])
    
    def get_messages(self):
        return self.get('messages')
    
    def add_messages(self, messages):
        self.get_messages().extend(messages)
        for message in messages:
            message.setCluster(self)        
        
    def get_representation(self):
        return self.get('representation')
    def set_representation(self, rep):
        self['representation']=rep
            
    def get_format_inference(self):
        return self.get('format_inference')
    
    def set_format_inference(self, formats):
        self['format_inference'] = formats        
        
    def get_messages_with_value_at(self, tokenIdx, value):
        """
        Returns all messages with value at position tokenIdx in the cluster
        """
        l = []
        for message in self.get('messages'):
            if message.get_tokenAt(tokenIdx).get_token()==value:
                l.append(message)
        return l
    
    def mergeToken(self, idx1, idx2):
        """
        Merges two tokens in a message with indices idx1 and idx2. idx1 and idx2 need to be adjacent.
        binary/binary and binary/text could be merged (the latter only during a bigger merge phase when the first binary tokens have
        already been merged into a text token)
        Original tokens are removed from cluster and the new token is inserted at position idx1.
        It is build as 'text' token and has the combined values, the start position of idx1 and the length of length(idx1)+length(idx2)
        This merge is performed for every message
        At last the cluster representation is updated with the combined new token representation
        """
        if idx1>idx2:
            idx1,idx2 = idx2,idx1
        if not idx2 == idx1+1:
            print "FATAL: Merge indices are not adjacent! (idx1: {0}, idx2: {1}".format(idx1,idx2)
            return                
        for message in self.get_messages():          
            token1 = message.get_tokenAt(idx1)
            token2 = message.get_tokenAt(idx2)
            if token1.get_tokenType()=='binary':
                t1val = chr(token1.get_token())
            else:
                t1val = token1.get_token()
            if token2.get_tokenType()=='binary':
                t2val = chr(token2.get_token())
            else:
                t2val = token2.get_token()                
            newval = t1val + t2val
            message.remove_tokenAt(idx2)
            message.remove_tokenAt(idx1)
            newToken = tokenrepresentation.TokenRepresentation("text", newval, token1.get_startsAt(), token1.get_length()+token2.get_length())
            message.insert_tokenAt(idx1,newToken)
                            
        # Update token representation
        rep = list(self.get_representation())
        rep.pop(idx2)
        rep.pop(idx1)
        rep.insert(idx1,"text")     
        self.set_representation(tuple(rep))
        
    
            
    def get_values_for_token(self, tokenIdx):
        """ 
        Returns the set of all values of tokens at position tokenIdx in all messages of a cluster
        """ 
        l = []
        m = []
        for message in self.get('messages'):
            l.append(message.get_tokenAt(tokenIdx).get_token())        
        m.extend(set(l))
        return m
    
    def get_all_values_for_token(self, tokenIdx):
        """
        Returns all values of tokens at position tokenIdx in all messages of a cluster
        Contains duplicates -> can be used for Counter() counting operaitons
        """
        l = []        
        for message in self.get('messages'):
            l.append(message.get_tokenAt(tokenIdx).get_token())        
        return l
        
            