
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
        self.update({'messages':[], 'representation':representation, 'format_inference':[]})        
    
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
    