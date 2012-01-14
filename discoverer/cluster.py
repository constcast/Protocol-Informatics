
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
    
    def add_semantics(self, idx, semantic):
        if not self.get('semantics').has_key(idx):
            self.get('semantics')[idx] = []
        self.get('semantics')[idx].append(semantic)
    
    def get_semantics(self):
        return self.get('semantics')
    
    def get_formats(self):
        formats = []
        for i in range(0,len(self.get('format_inference'))):
            formats.append(self.get_format(i))
        return formats
    
    def get_format(self, idx):
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
    
    def get_format_inference(self):
        return self.get('format_inference')
    
    def get_messages_with_value_at(self, tokenIdx, value):
        l = []
        for message in self.get('messages'):
            if message.get_tokenAt(tokenIdx).get_token()==value:
                l.append(message)
        return l
    
    def get_values_for_token(self, tokenIdx):
        l = []
        for message in self.get('messages'):
            l.append(message.get_token())
        return set(l)
            