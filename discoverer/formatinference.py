from message import Message
import string
import sys

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
        
        if not tokenRepresentation.get_tokenType()==Message.typeDirection:
            if not config.considerOneMessageAsConstant and len(messages)==1:
                constant = False
            else:
                for message in messages:
                    tl = message.get_tokenlist()
                    currentRepresentation = tl[tokenIndex]
                    if config.constantsAreCaseSensitive:
                        if not tokenRepresentation.get_token()==currentRepresentation.get_token():
                            constant = False
                            break                                                                  
                    else:    
                        if not string.upper(tokenRepresentation.get_token())==string.upper(currentRepresentation.get_token()):                                                                  
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
        super(Constant, self).__init__(Message.typeConst + " ('{0}')".format(value))
        self.__constValue = value
    #def __str__(self):
    #    return self.__stringRep
    
    #def __repr__(self):
    #    return self.__stringRep
    
    def getType(self):
        return Message.typeConst
    
    def getConstValue(self):
        return self.__constValue
        
class Variable(FormatSpecification):
    def __init__(self):
        super(Variable, self).__init__(Message.typeVariable)
    
    #def __str__(self):
    #    return self.__stringRep
    
    #def __repr__(self):
    #    return self.__stringRep
    
    def getType(self):
        return Message.typeVariable
    
class VariableStatistics(object):
    
    def __init__(self):
        self.initialize()
        
    def initialize(self):
        self.__dictionary = dict()
        self.samples = 0
        
    def reset(self):
        self.initialize()
    
    def addValue(self,value):
        self.samples += 1
        if self.__dictionary.has_key(value):
            cur_val = self.__dictionary[value]
            self.__dictionary[value] = cur_val+1
        else:
            self.__dictionary[value] = 1
        
    def numberOfDistinctSamples(self):
        return len(self.__dictionary.keys())
    def numberOfSamples(self):
        return self.samples
    def getValues(self):
        return self.__dictionary.keys()
    
    def getTop3(self):
        import operator
        sorted_dict = sorted(self.__dictionary.iteritems(), key=operator.itemgetter(1), reverse=True)
        return sorted_dict[0:3]
    
class VariableNumberStatistics(VariableStatistics):
    
    def __init__(self):
        self.initialize()
        
    def addValue(self, value):
        self.__sumPowerOne += value
        self.__sumPowerTwo += value*value
        if value<self.__min:
            self.__min = value
        if value>self.__max:
            self.__max = value
        super(VariableNumberStatistics, self).addValue(value)
    
    def initialize(self):
        super(VariableNumberStatistics, self).initialize()
        self.__sumPowerOne = 0
        self.__sumPowerTwo = 0
        self.__max = sys.float_info.min
        self.__min = sys.float_info.max
                
    def reset(self):
        self.initialize()
        
    def getMean(self):
        if self.samples>0:
            return self.__sumPowerOne/self.samples
         
    def getMax(self):
        if self.samples > 0:
            return self.__max
        else:
            return 0        
    def getMin(self):
        if self.samples > 0:
            return self.__min
        else:
            return 0 
    def getVariance(self):
        # http://de.wikipedia.org/wiki/Korrigierte_Stichprobenvarianz#Berechnung_ohne_vorherige_Mittelwertbildung
        if self.samples<2:
            return 0
        return 1.0/(self.samples-1)*(self.__sumPowerTwo - (1.0/self.samples)*(self.__sumPowerOne*self.__sumPowerOne))
    def getMedian(self):
        theValues = sorted(self.getValues())
        if len(theValues) % 2 == 1:
            return theValues[(len(theValues)+1)/2-1]
        else:
            lower = theValues[len(theValues)/2-1]
            upper = theValues[len(theValues)/2]
            return (float(lower + upper)) / 2      
              
class VariableTextStatistics(VariableStatistics):
    
    def __init__(self):
        self.initialize()
    
    def addValue(self, value):
        val_length = len(value)
        if val_length<self.__minLength:
            self.__minLength = val_length
            self.__shortest = value
        if val_length>self.__maxLength:
            self.__maxLength = val_length
            self.__longest = value
        super(VariableTextStatistics, self).addValue(value)
    
            
    def initialize(self):
        super(VariableTextStatistics, self).initialize()
        
        self.__minLength = sys.float_info.max
        self.__maxLength = sys.float_info.min
        self.__shortest = ""
        self.__longest = ""
        
    def reset(self):
        self.initialize()
        
    def getLongest(self):
        return self.__longest
    
    def getShortest(self):
        return self.__shortest
    
    

                
                
                