
def perform_format_inference_for_cluster(c, config):        
    """
    This function performs format inferrence on a cluster given.
    The value of the token for each message within a cluster is inspected and
    the information const/variable is inferred accordingly.
    
    """
    # Perform format inference
    # Walk through every cluster and check for variable/constant properties
    
    messages = c.get_messages()
    # get prototypes from first list element
    prototypeMessage = messages[0]
    tokenList = prototypeMessage.get_tokenlist()
    tokenIndex = 0
    result = []
    for tokenRepresentation in tokenList:
        
        # Now we have the value, lets check every other message for the same value
        constant = True
        
        if not config.considerOneMessageAsConstant and len(messages)==1:
            constant = False
        else:
            for message in messages:
                tl = message.get_tokenlist()
                currentRepresentation = tl[tokenIndex]
                if not tokenRepresentation.get_token()==currentRepresentation.get_token():
                    constant = False
                    break
        if constant:
            result.append(Constant(tokenRepresentation.get_token()))
            #result.append("const")
        else:
            result.append(Variable())
            #result.append("variable")
        tokenIndex +=1
    # print "Result for cluster (" , len(c.get_messages()), " entries)",  c.get_representation(), " after property inference: ", result
    
    c.set_format_inference(result)                 


def perform_format_inference_for_cluster_collection(cluster_collection, config):
    """
    This function performs format inferrence on a cluster collection given.
    The value of the token for each message within a cluster is inspected and
    the information const/variable is inferred accordingly.
    
    """
    cluster = cluster_collection.get_all_cluster()        
    for c in cluster:
        perform_format_inference_for_cluster(c,config)
        
class FormatSpecification(object):
    
    def __init__(self, str):
        self.__stringRep = str
    
    def getStringRepresentation(self):
        return self.__stringRep
    
    def __str__(self):
        return self.__stringRep
    
    def __repr__(self):
        return self.__stringRep
    
    def getType(self):
        return "n/a"
        
class Constant(FormatSpecification):
    def __init__(self, value):
        super(Constant, self).__init__("const ('{0}')".format(value))
        
    #def __str__(self):
    #    return self.__stringRep
    
    #def __repr__(self):
    #    return self.__stringRep
    
    def getType(self):
        return "const"
        
class Variable(FormatSpecification):
    def __init__(self):
        super(Variable, self).__init__("variable")
    
    #def __str__(self):
    #    return self.__stringRep
    
    #def __repr__(self):
    #    return self.__stringRep
    
    def getType(self):
        return "variable"