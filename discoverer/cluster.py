from collections import *

class Cluster(dict):
    
    def __init__(self, representation):
        self.update({'messages':[], 'representation':representation})        
    
    def get_messages(self):
        return self.get('messages')
    
    def get_representation(self):
        return self.get('representation')