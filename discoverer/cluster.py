
class Cluster(dict):
    
    def __init__(self, representation):
        self.update({'messages':[], 'representation':representation, 'format_inference':[]})        
    
    def get_messages(self):
        return self.get('messages')
    
    def get_representation(self):
        return self.get('representation')
    
    def get_format_inference(self):
        return self.get('format_inference')
    