import message

class TokenRepresentation():
    """
    This class encapsulates a token derived from the message
    Each TokenRepresentation has a type, either "binary" or "text"
    (function get_tokenType()), the token itself (function get_token())
    the information where it started in the original message (function get_startsAt())
    the length (function get_length()) and the semantic information that could be inferred from
    other code modules for that token (function get_semantics()).
    get_semantics() can contain multiple information.
    New semantic information can be added via function add_semantic or a list of semantics
    can be given via add_semantics, overwriting existing defintions 
    """
    
    def __init__(self, tokenType, token, startsAt, length):
        self.__tokenType = tokenType
        self.__token = token
        self.__startsAt = startsAt
        self.__length = length
        self.__semantic = []
    
    def __repr__(self):
        if self.__tokenType == message.Message.typeText:
            return '(%s,"%s",%s,%s,%s)' % (self.__tokenType, self.__token, self.__startsAt, self.__length, self.__semantic)
        else:
            return '(%s,0x%s,%s,%s,%s)' % (self.__tokenType, self.__token, self.__startsAt, self.__length, self.__semantic)
        
    
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
    