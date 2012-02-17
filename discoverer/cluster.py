import tokenrepresentation
import common

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
        self.update({'messages':[], 'representation':representation, 'format_inference':[], 'semantics':{}})        
     
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
            self.get('semantics')[idx] = []
        self.get('semantics')[idx].append(semantic)
    
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
        
    
    def get_formats(self):
        """
        Returns a list of all the format representations of the cluster
        """
        formats = []
        for i in range(0,len(self.get('format_inference'))):
            formats.append(self.get_format(i))
        return formats
    
    def get_format(self, idx):
        """
        Returns a tuple of format data for a given token consisting of
        * text/binary classification
        * the inferred format (constant vs. variable)
        * its semantics
        """
        if self.get('semantics').has_key(idx):
            return (self.get('representation')[idx], self.get('format_inference')[idx], set(self.get('semantics')[idx]))
        else: 
            return (self.get('representation')[idx], self.get('format_inference')[idx],[])
    def get_messages(self):
        return self.get('messages')
    def add_messages(self, messages):
        self.get_messages().extend(messages)        
        
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
        
            