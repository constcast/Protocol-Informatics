import tokenrepresentation
import common
import formatinference
import uuid
import string
from message import Message
from peekable import peekable
from formatinference import VariableTextStatistics
from formatinference import VariableNumberStatistics
from xml.sax.saxutils import escape
from cStringIO import StringIO
import Globals
import re
import log4py
import log4py.config
import logging

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
    def __init__(self, representation, origin):
        self.update({'messages':[], 'representation':representation, 'format_inference':[], 'semantics':{}, 'variable_statistics': []})        
        self.__internalname = uuid.uuid1()
        self.__origin = origin
        self.__splitpoint = "n/a"
        self.__regExVisual = ""
        self.__regEx = ""
        
    def getOrigin(self):
        return self.__origin
    
    def getSplitpoint(self):
        return self.__splitpoint
    
    def setSplitpoint(self, splitpoint):
        self.__splitpoint = str(splitpoint)
    
    def getNumberOfMessages(self):
        return len(self.get_messages())
       
    def getInternalName(self):
        return self.__internalname
    
    def getVariableStatistics(self):
        if self['variable_statistics']==[]:
            self.calculateVariableStatistics()
        return self['variable_statistics']
    
    def calculateVariableStatistics(self):
        #logging.info("Calculating variable token statistics")
        self['variable_statistics']=[]
        for idx, elem in enumerate(self['format_inference']):
            if elem.getType()==Message.typeVariable:
                stats = None
                if self['representation'][idx]==Message.typeBinary:
                    stats = VariableNumberStatistics()
                else:
                    stats = VariableTextStatistics()
                    
                for m in self.get_messages():
                    tokAt = m.get_tokenAt(idx)
                    val = tokAt.get_token()
                    stats.addValue(val)
                self['variable_statistics'].append(stats)   
            else:
                self['variable_statistics'].append(None)      
                
            
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
    def hasConstToken(self):
        numOfConst = 0
        formats = self.get_formats()
        messages = self.get_messages()
        idx = 0
        for fmt in formats:
            if fmt[1].getType()==Message.typeConst: # format is "const (xyz)"
                value = messages[0].get_tokenAt(idx).get_token()
                if value!=0x0a and value!=0x0d and fmt[0]!=Message.typeDirection:
                    numOfConst += 1
            idx += 1
        return numOfConst>0
    
    def getRegEx(self):
        #return self.calc_regEx()
    
        if self.__regEx == "":
            self.__regEx = self.calc_regEx()
        return self.__regEx
           
    def calc_regEx(self):
        if Globals.isText():
            # When we are text, only use visual regex
            return self.getRegExVisual()
        
        
        regexstr = "^"
        idx = 0
        iterator = peekable(self.get('format_inference'))
        content_msg = self.get_messages()[0]
        # Using only the first message COULD be a problem:
        # In cases where we have trailing whitespaces in one of the messages but not in the first one,
        # The regex will not include these and the regex will not be valid for this message. As a result this
        # message won't be parsed correctly in statemachine_accepts. See below for a workaround
        while not iterator.isLast():
            item = iterator.next()
            tokType = self.get('representation')[idx]
            if tokType==Message.typeDirection:
                # Add a \s* before the first text token
                if not iterator.isLast():
                    if self.get('representation')[idx+1]==Message.typeText:
                        regexstr += "(?:20)*"                      
            else:
                token = content_msg.get_tokenAt(idx)
                startsAt = token.get_startsAt()
                length = token.get_length()
                
                if isinstance(item,formatinference.Constant):
                    #if isinstance(item.getConstValue(),str):
                    token = content_msg.get_tokenAt(idx)
                    startsAt = token.get_startsAt()
                    length = token.get_length()
                    
                    payload = content_msg.get_payload()[startsAt:startsAt+length]
                    s = "".join([str(elem) for elem in payload])
                    regexstr += s
                       
                elif isinstance(item,formatinference.Variable):
                    #regexstr += "*?" # Non greedy match - will lead to lock ups
                    #regexstr += ".*" # Non greedy match - will lead to lock ups
                    #regexstr += "((?!20).)+" # Negative lookup for whitespace - does not read bytewise - will abort also on X20Xaabb200a0d
                    
                    # New approach:
                    # Do not use .* but try to be more explicit: [0-9a-f]{2} reads multiple hex values. The trailing {...} value determines how often
                    # these are observed in a cluster (based on the VariableText/NumberStatistics
                    
                    stats = self.getVariableStatistics()[idx]
                    min = 1
                    max = 1
                    if stats != None:
                        if isinstance(stats,formatinference.VariableTextStatistics):
                            min = len(stats.getShortest())
                            max = len(stats.getLongest())
                        else: # This is VariableBinaryStatistics
                            # Binary length is always 1 because we only look at one byte values
                            # min/max length is invalid here
                            ##s = str(stats.getMin())
                            ##min = len(s)
                            ##s = str(stats.getMax())
                            ##max = len(s)
                            min = length
                            max = length
                            
                        if min == max:
                            #regexstr += "(?:[0-9a-f]{2}){" + str(min) + "}"
                        
                            regexstr += "(?:[0-9a-f]{2})"
                            if min>1:
                                regexstr += "{" + str(min) + "}"
                        else:
                            regexstr += "(?:[0-9a-f]{2}){" + str(min) +","+ str(max) +"}"
                    else:
                        regexstr += "(?:[0-9a-f]{2})+"
                            
                #===============================================================
                # if not iterator.isLast():
                #                     
                #    gotGap = False                       
                #    nextStart = content_msg.get_tokenAt(idx+1).get_startsAt()
                #    if nextStart!=startsAt+length:
                #    #if nextOne.get_startsAt()!=startsAt+length+1:
                #        regexstr += "(?:20)+"
                #        gotGap = True
                #    
                #    # Added 20120409 to compensate for trailing WS tokens
                #    if not gotGap:
                #===============================================================
                # Add (?:20)* token at the beginning and end of text/binary tokens
                # This copes for the problem that Hello_World_ and Hello_World evaluate to the same format, but should have other regexes
                curType = content_msg.get_tokenAt(idx).get_tokenType()
                if iterator.isLast():
                    if curType==Message.typeText:
                        regexstr += "(?:20)*"
                else:
                    curType = content_msg.get_tokenAt(idx).get_tokenType()
                    nextType = content_msg.get_tokenAt(idx+1).get_tokenType()
                    if (curType==Message.typeBinary and nextType==Message.typeText) or ( 
                        curType==Message.typeText and nextType==Message.typeBinary):
                        regexstr += "(?:20)*"
                    elif curType==Message.typeText and nextType==Message.typeText:
                        regexstr += "(?:20)+"
                            
                #===============================================================
                #       
                # if tokType == Message.typeText:
                #    # peek ahead if next is also text
                #    # Add separator for tokenseparator (nothing by bin-bin, bin-text, text-bin but whitespace when text-text
                #    # text-text is separated by \s (whitespace)
                #    nextOne = iterator.peek()
                #    if nextOne!=None:
                #        nextType = self.get('representation')[idx+1]
                #        if nextType == Message.typeText:
                #            #regexstr += "((20)|(08)|(0a)|(0d))?" # Add whitespace token separator
                #            regexstr += "(?:20)+" # Add whitespace token separator                
                #           
                #===============================================================
            idx += 1
        if not (Globals.getConfig().calculateMaxMessageLength or Globals.getConfig().danglingRegEx):
            regexstr += "$"
        return regexstr 
    
    def performSanityCheckForRegEx(self):
        testmsg = self['messages'][0]
        if Globals.getProtocolClassification()==Globals.protocolBinary:
            regex_str = self.getRegEx()
            res = re.match(regex_str, testmsg.get_payload_as_string())
            if res==None:
                print "Error: calculated regex did not match it's payload"
                print "Payload: {0}".format(testmsg.get_payload_as_string())
                print "RegEx:   {0}".format(regex_str)
                self.calc_regEx()
                raise Exception("RegEx did not match to payload")
        if Globals.getProtocolClassification()==Globals.protocolText:    
            regex_str = self.getRegExVisual()
            res = None
            try:
                res = re.match(regex_str, testmsg.get_message())
            except Exception:
                print "Exception in sanity check:"
                print "Regex: {0}".format(regex_str)
                print "Testmsg: {0}".format(testmsg.get_message())
                print "Payload: {0}".format(testmsg.get_payload_as_string())
                import sys
                print "Exception: {0}".format(sys.exc_info())
            if res==None:
                print "Error: calculated visual regex did not match it's message"
                print "Message:      {0}".format(testmsg.get_message())
                print "Visual regEx: {0}".format(regex_str)
                self.calc_regExVisual()
                raise Exception("RegExVisual did not match to messages")
              
                              
    def getPeachRepresentation(self):
        import sys
        old_stdout = sys.stdout
        handle = StringIO()
        sys.stdout = handle
        messages =  self.get_messages()  
        formats = self.get_formats()
        var_stats = self.getVariableStatistics()
        
        repl_dict = dict()
        
        repl_dict["\""]="&quot;"
        repl_dict["\'"]="&apos;"
        
        print '<DataModel name="{0}_dm">'.format(self.getInternalName())
        for idx, format in enumerate(formats):
            category, formatType, semantics = format
            if isinstance(formatType, formatinference.Constant):
                if category==Message.typeBinary:
                    print '<Number value="{0}" size="8" token="true" />'.format(escape(str(formatType.getConstValue()), repl_dict))
                else:
                    print '<String value="{0}" token="true" nullTerminated="False" />'.format(escape(str(formatType.getConstValue()), repl_dict))
            elif isinstance(formatType, formatinference.Variable):
                elem = var_stats[idx]
                if isinstance(elem,formatinference.VariableNumberStatistics):
                    print '<Number name="{0}_{1}" size="8" />'.format(self.getInternalName(), idx)
                elif isinstance(elem,formatinference.VariableTextStatistics):
                    print '<String name="{0}_{1}" nullTerminated="False" />'.format(self.getInternalName(), idx)
        print '</DataModel>'
        body = handle.getvalue()
        handle.close()         
        sys.stdout = old_stdout
        return body
    # Force recalculation
    def updateRegEx(self):
        self.__regEx = ""
        self.__regExVisual = ""
        self.getRegExVisual()
        self.getRegEx() 
    def getXMLRepresentation(self):
        import sys
        old_stdout = sys.stdout
        handle = StringIO()
        sys.stdout = handle
        messages =  self.get_messages()  
        formats = self.get_formats()
        var_stats = self.getVariableStatistics()
        
        self.updateRegEx()
        
        print '<cluster internalName="{0}" numOfMessages="{1}">'.format(self.getInternalName(), len(messages))
        print '<regex>{0}</regex>'.format(escape(self.getRegEx()))
        print '<visualRegex>{0}</visualRegex>'.format(escape(self.getRegExVisual()))

        print '<messageFormat hash="{0}" numOfFormats="{1}">'.format(self.getFormatHash(), len(formats))
        for idx, format in enumerate(formats):
            category, formatType, semantics = format
                
            print '\t<messageFormatElement index="{0}" category="{1}">'.format(idx, category)
            if isinstance(formatType, formatinference.Constant):
                print '\t\t<format type="constant">'
                print '\t\t\t<value>{0}</value>'.format(escape(str(formatType.getConstValue())))
                print '\t\t</format>'
            elif isinstance(formatType, formatinference.Variable):
                print '\t\t<format type="variable" />'
                elem = var_stats[idx]
                if isinstance(elem,formatinference.VariableNumberStatistics):
                    print '<variableStatistic type="NumberStatistic">'
                    print '\t<minimum>{0}</minimum>'.format(elem.getMin())
                    print '\t<maximum>{0}</maximum>'.format(elem.getMax())
                    print '\t<mean>{0}</mean>'.format(elem.getMean())
                    print '\t<variance>{0}</variance>'.format(elem.getVariance())
                    print '\t<numOfDistinctSamples>{0}</numOfDistinctSamples>'.format(elem.numberOfDistinctSamples())
                    print '\t<top3list>'
                    for item,amount in elem.getTop3():
                        print '\t\t<top3listitem>'
                        print '\t\t\t<value>{0}</value>'.format(item)
                        print '\t\t\t<amount>{0}</amount>'.format(amount)
                        print '\t\t</top3listitem>'
                    print '\t</top3list>'
                    print '</variableStatistic>'
                elif isinstance(elem,formatinference.VariableTextStatistics):
                    print '<variableStatistic type="TextStatistic">'
                    print '\t<shortestText>{0}</shortestText>'.format(escape(elem.getShortest()))
                    print '\t<longestText>{0}</longestText>'.format(escape(elem.getLongest()))
                    print '\t<numOfDistinctSamples>{0}</numOfDistinctSamples>'.format(elem.numberOfDistinctSamples())
                    print '\t<top3list>'
                    for item,amount in elem.getTop3():
                        print '\t\t<top3listitem>'
                        print '\t\t\t<value>{0}</value>'.format(escape(item))
                        print '\t\t\t<amount>{0}</amount>'.format(amount)
                        print '\t\t</top3listitem>'
                    print '\t</top3list>'
                    print '</variableStatistic>'
            if (len(semantics)>0):
                print '\t\t<semantics length="{0}">'.format(len(semantics))
                for s in semantics:
                    print '\t\t\t<semantic>{0}</semantic>'.format(s)
                print '\t\t</semantics>'
            print '\t</messageFormatElement>'
            
        print '</messageFormat>'
        
        print '</cluster>'
        body = handle.getvalue()
        handle.close()         
        sys.stdout = old_stdout
        return body
    
    def flushMessages(self):
        self["messages"] = []
        #pass
        
    def getRegExVisual(self):
        #return self.calc_regExVisual()
        if self.__regExVisual == "":
            self.__regExVisual = self.calc_regExVisual()
        return self.__regExVisual
    
    def calc_regExVisual(self):
        regexstr = "^"
        idx = 0
        iterator = peekable(self.get('format_inference'))
        while not iterator.isLast():
            item = iterator.next()
            tokType = self.get('representation')[idx]
            if tokType==Message.typeDirection:
                # Add a \s* before the first text token
                if not iterator.isLast():
                    if self.get('representation')[idx+1]==Message.typeText:
                        # Only adding [\\t| ]* will not work for multiline texts like in ftp banners. Here we will need the \r \n as well.
                        # So get back to \s instead of "[\t| ]*"
                        #regexstr += "[\\t| ]*"
                        regexstr += "\\s*"
            else:            
                if isinstance(item,formatinference.Constant):
                    #if isinstance(item.getConstValue(),str):
                    if self.get('representation')[idx]==Message.typeText:
                        val = item.getConstValue()
                        # Order matters!
                        val = string.replace(val, "\\", "\\\\")
                        val = string.replace(val, "(", "\(")
                        val = string.replace(val, ")", "\)")
                        val = string.replace(val, ".", "\.")
                        val = string.replace(val, "{", "\{")
                        val = string.replace(val, "}", "\}")
                        val = string.replace(val, "]", "\]")
                        val = string.replace(val, "[", "\[")
                        val = string.replace(val, "*", "\*")
                        val = string.replace(val, "?", "\?")
                        val = string.replace(val, "$", "\$")
                        
                        
                        regexstr += val
                    else:
                        val = hex(item.getConstValue())[2:]
                        if len(val)==1:
                            val = "0{0}".format(val)
                        regexstr += "\\x{0}".format(val)
                elif isinstance(item,formatinference.Variable):
                    stats = self.getVariableStatistics()[idx]
                    min = 1
                    max = 1
                    if stats != None:
                        if isinstance(stats,formatinference.VariableTextStatistics):
                            min = len(stats.getShortest())
                            max = len(stats.getLongest())
                        else: # We"re VariableBinaryStatistics
                            # min/max is always 1
                            
                            #s = str(stats.getMin())
                            #min = len(s)
                            #s = str(stats.getMax())
                            #max = len(s)
                            min = 1
                            max = 1
                        if min == max:
                            regexstr += "."
                            if min>1:
                                regexstr += "{" + str(min) + "}"
                        else:
                            regexstr += ".{" + str(min) +","+ str(max) +"}"
                    else:
                        regexstr += ".+"
                     
                #===============================================================
                # if tokType == Message.typeText:
                #    # peek ahead if next is also text
                #    # Add separator for tokenseparator (nothing by bin-bin, bin-text, text-bin but whitespace when text-text
                #    # text-text is separated by \s (whitespace)
                #    nextOne = iterator.peek()
                #    if nextOne!=peekable.sentinel:
                #        nextType = self.get('representation')[idx+1]
                #        if nextType == Message.typeText:
                #            regexstr += "\s" # Add whitespace token separator                
                #===============================================================
                
                curType = self.get('representation')[idx]
                if iterator.isLast():
                    if curType==Message.typeText:
                        # See comment on top why "[\\t| ]*" is not enough
                        #regexstr += "[\\t| ]*"
                        regexstr += "\\s*"
                else:
                    nextType = self.get('representation')[idx+1]
                    if (curType==Message.typeBinary and nextType==Message.typeText) or ( 
                        curType==Message.typeText and nextType==Message.typeBinary):
                        # See comment on top why "[\\t| ]*" is not enough
                        #regexstr += "[\\t| ]*"
                        regexstr += "\\s*"
                    elif curType==Message.typeText and nextType==Message.typeText:
                        # See comment on top why "[\\t| ]+" is not enough
                        #regexstr += "[\\t| ]+"
                        regexstr += "\\s+"
            idx += 1
        if not (Globals.getConfig().calculateMaxMessageLength or Globals.getConfig().danglingRegEx):
            regexstr += "$"
        return regexstr 
                
                        
                
    def has_semantic_for_token(self, idx, semantic):
        """
        Checks whether the token at position idx has a given semantic
        """
        if not self.get('semantics').has_key(idx):
            return False
        try:
            return semantic in (self.get('semantics')[idx])
            # Only worked for listsreturn 0<=self.get('semantics')[idx].index(semantic)
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
            self.get('semantics')[idx] = set() #[]
        #self.get('semantics')[idx].append(semantic)
        self.get('semantics')[idx].add(semantic)
        
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
        
    def getFormatHash(self):
        """
        Returns the hash of the format inference incl. const values
        """
        import hashlib
        return hashlib.sha1(str(self.get_formats())).hexdigest()
    
    def get_formats(self):
        """
        Returns a list of all the format representations of the cluster
        """
        formats = []
        for i in range(0,len(self.get('representation'))):
            formats.append(self.get_format(i))
        return formats
    
    def get_format(self, idx):
        """
        Returns a tuple of format data for a given token consisting of
        * text/binary classification
        * the inferred format (constant vs. variable)
        * its semantics
        """
        s = []
        if self.get('semantics').has_key(idx):
            s.extend(self.get('semantics')[idx]) # Take all strings from the set and add them to the list
            
        if len(self.get('format_inference'))>idx:
            #t = "{0}".format(self.get('format_inference')[idx])
            t = self.get('format_inference')[idx]
        else:
            t = None
        return (self.get('representation')[idx], t,s)
    
        
        #if self.get('semantics').has_key(idx):
        #    return (self.get('representation')[idx], self.get('format_inference')[idx], set(self.get('semantics')[idx]))
        #else: 
        #    return (self.get('representation')[idx], self.get('format_inference')[idx],[])
    
    def get_messages(self):
        return self.get('messages')
    
    def add_messages(self, messages):
        self.get_messages().extend(messages)
        for message in messages:
            message.setCluster(self)        
        
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
        
            