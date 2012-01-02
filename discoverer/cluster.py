
class Cluster(dict):
    
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
    