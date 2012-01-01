
class TokenRepresentation():
    def __init__(self, tokenType, token, startsAt, length):
        self.__tokenType = tokenType
        self.__token = token
        self.__startsAt = startsAt
        self.__length = length
        self.__semantic = []
    
    def __repr__(self):
        return '(%s,%s,%s,%s,%s)' % (self.__tokenType, self.__token, self.__startsAt, self.__length, self.__semantic)
        
    
    def get_tokenType(self):
        return self.__tokenType
    
    def get_token(self):
        return self.__token
    
    def get_startsAt(self):
        return self.__startsAt
    
    def get_length(self):
        return self.__length
    
    def get_semantics(self):
        return self.__semantic
    
    def set_semantics(self, semantics):
        self.__semantic = semantics
    
    def add_semantic(self, semantic):
        self.__semantic.append(semantic)    
    