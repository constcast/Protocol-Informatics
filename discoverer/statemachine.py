'''
Created on 20.02.2012

@author: daubsi
'''

import copy
import uuid
from xml.sax.saxutils import escape
from cStringIO import StringIO

class State(object):
    typeIncomingClient2ServerMsg = 'IncomingClient2ServerMsg'
    typeIncomingServer2ClientMsg = 'IncomingServer2ClientMsg'
    typeIncomingNoneMsg = 'IncomingNoneMsg'
    
    def __init__(self, name, stateType, statemachine):
        self.__name = name
        self.__internalname = uuid.uuid1()
        self.__stateType = stateType
        self.__statemachine = statemachine
        
    def getName(self):
        return self.__name
    
    def getType(self):
        return self.__stateType
    
    def getInternalName(self):
        return self.__internalname
    
    def __repr__(self):
        return self.__name
    
    def __eq__(self, other):
        return self.__name == other.__name and self.__stateType == other.__stateType
    
    def getXMLRepresentation(self):
        t_list = self.__statemachine.get_transitions_from(self)
        print '<state name="{0}" internal_name="{1}" type="{2}" numOfTransitionsFrom="{3}">'.format(self.getName(), self.getInternalName(), self.getType(), len(t_list))
        if (len(t_list)>0):
            print '<referenced_transitions>'
            total = 0
            for t in t_list:
                total += t.getCounter()
    
            for idx2, t in enumerate(t_list):
                #print "\tIdx: {0}, Internal name: {1}, Probability: {2}".format(idx2, t.getInternalName(), t.getCounter()/float(total))
                print '<referenced_transition transitionProbability="{0}" reference="{1}" />'.format(t.getCounter()/float(total), t.getInternalName())
                #print '\t<internal_name>{0}</internal_name>'.format(t.getInternalName())
                #print '<referenced_transition>'
    
            print '</referenced_transitions>'
        print '</state>'
        #print "Idx: {0}, Internal name: {1}, State ID: {2}, State type: {3}, Number of transitions from: {4}".format(idx, s, s.getInternalName(), s.getType(), numOfTrans)
            
    
    
    
class Transition(object):
    def __init__(self, src, hash, dest, direction, msg,regex, regexvisual, cluster):
        self.__src = src
        self.__hash = hash
        self.__dest = dest
        self.__direction = direction
        self.__msg = msg
        self.__regex = regex
        self.__regexvisual = regexvisual
        self.__counter = 1
        self.__cluster = cluster
        self.__internalname = uuid.uuid1()
        
    def getInternalName(self):
        return self.__internalname
    
    def getCluster(self):
        return self.__cluster
    
    def getRegExVisual(self):
        return self.__regexvisual
    
    def setRegExVisual(self, regexvisual):
        self.__regexvisual = regexvisual
    def getRegEx(self):
        return self.__regex
    
    def setRegEx(self, r):
        self.__regex = r
        
    def getSource(self):
        return self.__src
    
    def setSource(self, src):
        self.__src = src
    
    def getHash(self):
        return self.__hash
    
    def getDestination(self):
        return self.__dest
    
    def setDestination(self, dest):
        self.__dest = dest
        
    def getDirection(self):
        return self.__direction

    def getMessage(self):
        return self.__msg
    
    def getCounter(self):
        return self.__counter
    
    def incCounter(self):
        self.__counter += 1
        
    def __hash__(self):
        import hashlib
        hv = hashlib.sha1("{0}{1}{2}{3}".format(self.__src, self.__hash, self.__dest, self.__direction)).hexdigest()
        return hash(hv)
    
    def __eq__(self, other):
        if self.__src == other.getSource() and self.__hash == other.getHash() and self.__dest == other.getDestination() and self.__direction == other.getDirection():
            return True
        return False
    
    def __repr__(self):
        return "({0},{1},{2},{3},{4},{5})".format(self.__src, self.__hash, self.__dest, self.__direction, self.__counter, self.__msg)
     
    def getXMLRepresentation(self):
        #return "Internal name: {0}, Source: {1}, Transition: {2}, Destination: {3}, Counter: {4}, Direction: {5}, Cluster-Reference: {6}, RegEx: {7}".format(self.getInternalName(), self.getSource(), self.getHash(), self.getDestination(), self.getCounter(), self.getDirection(), self.getCluster().getInternalName(), self.getRegEx())
        print '<transition name="{0}" numOfTraversals="{1}" direction="{2}">'.format(self.getInternalName(), self.getCounter(), self.getDirection())
        print '\t<source referenced_state="{0}" />'.format(self.getSource().getInternalName())
        #print '\t\t<name>{0}</name>'.format(self.getSource())
        #print '\t\t<internal_name>{0}</internal_name>'.format(self.getSource().getInternalName())
        #print '\t</source>'
        print '\t<hash>{0}</hash>'.format(self.getHash())
        print '\t<destination referenced_state="{0}"/>'.format(self.getDestination().getInternalName())
        #print '\t\t<name>{0}</name>'.format(self.getDestination())
        #print '\t\t<internal_name>{0}</internal_name>'.format(self.getDestination().getInternalName())
        #print '\t</destination>'
        print '\t<cluster_reference>{0}</cluster_reference>'.format(self.getCluster().getInternalName())
        print '\t<regex>{0}</regex>'.format(escape(self.getRegEx()))
        print "</transition>" 
class Statemachine(object):
    '''
    This class represents a statemachine derived from the given message sequences
    and their corresponding formats
    '''

    def __init__(self, sequences, config):
        '''
        Constructor
        '''
        self.__sequences = sequences
        #self.__start = "s0"
        #self.__states = ["s0"]
        self.__start = State("s0",State.typeIncomingNoneMsg, self)
        self.__states = [self.__start]
        self.__transitions = set()
        self.__nextstate = 1
        self.__config = config
        self.__alphabet = set()
    
    def setConfig(self,config):
        self.__config=config
    def setTestFlows(self, testflows):
        self.__testflows = testflows
           
    def accepts_flow(self, testflow, flowID=""):
        import re
        curState = self.__start
        failed = False
        
        # returns a tuple with the testresults
        # structure:
        # tuple(testSuccessful, isInTestFlows, hasMoreThanOneMessage, 
        #       has_no_gaps, is_alternating, did_all_transitions, finished_in_final)
        # tuple is built in the various checks
        
        if flowID != "":
            print "Flow {0} under test:".format(flowID)
        if self.__testflows == None:
            print "ERROR: Testflows not yet set in statemachine"
            return dict({"testSuccessful": False, "isInTestFlows": False, "hasMoreThanOneMessage": False, "has_no_gaps": False, "is_alternating": False, "did_all_transitions": False, "finished_in_final": False})
        
        messages = self.__testflows[flowID]
        # If the flow is considered invalid by itself, return True (as if there was no error in parsing)
        if len(messages)==1:
            self.log("Flow {0} has only 1 message. Skipping flow".format(flowID))
            return dict({"testSuccessful":False, "isInTestFlows": True, "hasMoreThanOneMessage": False, "has_no_gaps": False, "is_alternating": False, "did_all_transitios": False, "finished_in_final":  False})    
        returntuple = self.flow_is_valid(self.__testflows,flowID)
        if returntuple[0]==False or returntuple[1] == False:
            print "Flow is not valid"
            if returntuple[0]==False:
                return dict({"testSuccessful": False, "isInTestFlows": True, "hasMoreThanOneMessage": True, "has_no_gaps": False, "is_alternating": False, "did_all_transitions": False, "finished_in_final": False})    
            else:
                return dict({"testSuccessful": False, "isInTestFlows": True, "hasMoreThanOneMessage": True, "has_no_gaps": True, "is_alternating": False, "did_all_transitions": False, "finished_in_final": False})
                              
        if self.__config.debug:
            for key, value in testflow.items() :
                print "{0} - {1}".format(key, value)
            print
            print "Startstate: {0}".format(self.__start)
            print "Finals: {0}".format(",".join(self.__finals))
            print
        for key, value in testflow.items() :
            f = value[0]
            stateTransitions = self.get_transitions_from(curState)
            # Sort stateTransitions such that pure variable transistions come last
            #===================================================================
            # idx = 0
            # for steps in range(1,len(stateTransitions)):
            #    regex = stateTransitions[idx].getRegEx()
            #    p = re.compile("^.*[a-fA-F0-9]+.*$") # Match for any const value in regex
            #    res = p.match(regex)
            #    if res == None:
            #        # transition regex contains no const value hook, push to back
            #        t = stateTransitions[idx]
            #        stateTransitions.remove(t)
            #        stateTransitions.append(t)
            #    else:
            #        idx+=1
            #         
            # 
            #===================================================================
            self.log("Current state: {0}".format(curState))
            self.log("Possible transitions: ")
            for t in stateTransitions:
                self.log("Destination: {0}, hash: {1}, visual regex: {2}, regex: {3}, message: {4}".format(t.getDestination(), t.getHash(), t.getRegExVisual(), t.getRegEx(), t.getMessage()))
            self.log("Current input:")
            self.log("Msg: {0}".format(f.get_message()))
            payload = f.get_payload_as_string()
            self.log("Payload: {0}".format(payload))
            gotOne = False
            for t in stateTransitions:
                r = t.getRegEx()
                self.log("Testing regex visual: {0}".format(t.getRegExVisual()))
                self.log("Testing regex:        {0}".format(t.getRegEx()))
                res = None
                try:
                    p = re.compile(r)
                    res = p.match(payload)
                except AssertionError as ae:
                    print ae
                    #print "AssertionError: {0}".format(ae)
                if res:
                    gotOne = True
                    break
            if not gotOne:
                # Search for epsilon transitions
                for t in stateTransitions:
                    if t.getHash=="{{epsilon}}":
                        gotOne = True
                        break
            if gotOne:
                self.log("Found matching transition: {0}".format(t))
                curState = t.getDestination()
            else:
                self.log("Did not find any matching transition")
                failed = True
                break
        
        # Consume remaining epsilons
        if not failed:
            tryAgain = True
            while tryAgain:
                tryAgain = False
                stateTransitions = self.get_transitions_from(curState)
                for t in stateTransitions:
                        if t.getHash()=="{{epsilon}}" and (curState not in self.__finals):
                            tryAgain = True
                            curState = t.getDestination()
                            break
                        
        if failed:
            self.log("ERROR: Flow not accepted by statemachine")
            return dict({"testSuccessful": False, "isInTestFlows": True, "hasMoreThanOneMessage": True, "has_no_gaps": True, "is_alternating": True, "did_all_transitions": False, "finished_in_final": False})
        
            # Try to match the message payload with one of the regex of our transitions
        else:
            if curState in self.__finals:
                self.log("SUCCESS: Statemachine did reach acceptance state")
                return dict({"testSuccessful": True, "isInTestFlows": True, "hasMoreThanOneMessage": True, "has_no_gaps": True, "is_alternating": True, "did_all_transitions": True, "finished_in_final": True})
        
            else:
                self.log("ERROR: Statemachine did not halt in acceptance state")
                return dict({"testSuccessful": False, "isInTestFlows": True, "hasMoreThanOneMessage": True, "has_no_gaps": True, "is_alternating": True, "did_all_transitions": True, "finished_in_final": False})
                             
        
        
        #=======================================================================
        # firstitemnumber = sorted(testflow.keys())[0]
        # (msg, dir) = testflow[firstitemnumber] # Retrieve first msg
        # print "{0} / {1}".format(msg.get_message(), msg.getCluster().get_formats())
        # nextMsg = msg.getNextInFlow()
        # while nextMsg != None:
        #    print "{0} / {1}".format(nextMsg.get_message(), nextMsg.getCluster().get_formats())
        #    nextMsg = nextMsg.getNextInFlow()
        #=======================================================================
        
    def has_gaps(self,numbers, gap_size):
        # Based on http://stackoverflow.com/questions/4375310/finding-data-gaps-with-bit-masking
        adjacent_differences = [(y - x) for (x, y) in zip(numbers[:-1], numbers[1:])]
        for elem in adjacent_differences:
            if elem>1:
                return True
        return False
    
    def findTransitionBySrc(self, curState, hash):
        # First try to find exact matches
        for t in self.__transitions:
            if t.getSource() == curState and t.getHash()==hash: # Exactly this transition was already in list
                return t      
        
    def findTransition(self,curState, hash):
        # First try to find exact matches
        for t in self.__transitions:
            if t.getSource() == curState and t.getHash()==hash: # Exactly this transition was already in list
                return t      
        # Now a match of the hash is enough
        # Needed because of NFA degeneration of statemachine    
        for t in self.__transitions:
            if t.getHash() == hash: # This transition is already in list
                return t
        return None
    
    def is_alternating(self, flows, flow):
        messages = flows[flow]
        direction = ""
        msg_keys = sorted(messages.keys())
        for msg_key in msg_keys:
            direction2 = messages[msg_key][1]
            if direction==direction2: # Current message has same direction as message before
                return False
            direction = direction2
        return True
    
    def addTransition(self,src,trans,dest, direction, msg, regex, regexvisual, cluster):
        self.__transitions.add(Transition(src,trans,dest,direction,msg, regex, regexvisual, cluster))
        
    def dumpTransitions(self):
        print "Last of statemachine transitions:"
        print "================================="
        for t in self.__transitions:
            print "{0},{1},{2},{3},{4}".format(t.getSource(), t.getHash(), t.getDestination(), t.getRegEx(), t.getMessage())
            
    def fake(self):
        self.__start = "s43"
        self.__states = ["s43","s44","s45","s46","s47","s48","s49","s50", "s51", "s52","s53","s54","s55","s56","s57"]
        self.__transitions = set()
        self.__finals = []
        self.__alphabet = ["USER","PASS","QUIT","CWD","CDUP","RNFR","RNTO"]
        self.addTransition("s43","USER","s44","client","USER")
        self.addTransition("s44","PASS","s45","client","PASS")
        self.addTransition("s45","QUIT","s46","client","QUIT")
        self.addTransition("s45","CWD","s47","client","CWD")
        self.addTransition("s47","CWD","s48","client","CWD")
        self.addTransition("s47","CDUP","s53","client","CDUP")
        self.addTransition("s47","RNFR","s55","client","RNFR")
        self.addTransition("s48","CDUP","s49","client","CDUP")
        self.addTransition("s49","RNFR","s50","client","RNFR")
        self.addTransition("s50","RNTO","s51","client","RNTO")
        self.addTransition("s51","QUIT","s52","client","QUIT")
        self.addTransition("s53","QUIT","s54","client","QUIT")
        self.addTransition("s55","RNTO","s56","client","RNTO")
        self.addTransition("s56","QUIT","s57","client","QUIT")
        self.reverx_merge()
        
    def flow_is_valid(self, flows, flow):
        messages = flows[flow]
        message_indices = messages.keys()
        
        if self.has_gaps(message_indices,1):
            print "ERROR: Flow {0} has gaps in sequences numberings. Skipping flow".format(flow)
            return tuple([False, False]) # return that it has failed has_gaps and is_alternating
        else:
            if self.__config.flowsMustBeStrictlyAlternating and not self.is_alternating(flows,flow):
                print "ERROR: Flow {0} is not strictly alternating between client and server. Skippng flow".format(flow)
                return tuple([True, False]) # return that it has passed has_gaps but failed is_alternating
        return tuple([True, True]) # return that is has passed has_gaps and is_alternating
    
    def log(self, msg):
        if self.__config.debug:
            print msg
            
    def build(self):
        if self.__config.performReverXMinimization and not self.__config.fastReverXStage1 and not self.__config.nativeReverXStage1:
            # When ReverX minimization is desired we need either the fast or native stage 1!
            raise Exception("ReverX minimization is desired but neither 'nativeReverXStage1' nor 'fastReverXStage1' are set to true!")        
        if self.__config.performReverXMinimization and self.__config.fastReverXStage1:
            print "Performing fast ReverX stage 1 during iterative build"
        
        # Rationale for "fast reverx" and "native reverx"
        # fast reverx basically does the same as native reverx but sooner.
        # As the number of transition is therefore kept at a low level because of the
        # iterative approach, the speed
        # is very high in contrast to the later performed "native reverx"which works
        # on the completed state machine.
        # But there is one important difference.
        # Pruning might lead to incorrect results when the "fast" version is used.
        # Theory behind: Lets assume there are faulty input data where the sequence
        # of commands violates the protocol. If the faulty entries come soon in the sequence
        # of flows, they will create transitions that are later on reused in the "quick" mode.
        # Therefore this faulty entries are kept and maybe even exaggerated during the iterative
        # build. When it is done lateron, we have the chance of pruning the faulty entries by
        # removing them when they are below the edgeUseThreshold. Therefore outlies are completely
        # removed without interfering with the rest of the statemachine. In "fast" mode, the number
        # of edge traversals might be incremented due to the traversal reuse and get over the configured
        # threshold.
        # Faulty sequences are considered to be responsible for reflexive transitions that should
        # otherwise be spread over multiple nodes.
        
        # Important observation:
        # ======================
        #
        # We consider a state "final" where the last element of a flow ends, as
        # we cannot assume anything else.
        # Now we currently have three problems with our test sets
        # a) We have a maximum we read:
        #    If our maxMessages ends within reading a flow, we mistakenly consider
        #    our broken flow as final, thus declaring final states where there should be none
        # b) In order to reverse engineer a protocol perfectly, the test data has to be perfect
        #    as well. If we've got invalid protocol behavior - and we HAVE these - our reverse
        #    engineered protocol can never be 100% exact according to spec
        # c) Out ftp testset almost never ends with QUIT but with arbitrary commands. Therefore
        #    we create a lot of finals (not because of a or b), just because it IS the last command/server response
        #    This again does not necessarily reflect the true protocol.

        
        
        
        #self.__states.append("e") # Error state
        self.__finals = set()
        error = 0
        for flow in self.__sequences:
            messages = self.__sequences[flow]
            if len(messages)==1:
                self.log("Flow {0} has only 1 message. Skipping flow".format(flow))
                continue
            (has_no_gaps, is_alternating) = self.flow_is_valid(self.__sequences,flow)
            if not (has_no_gaps and is_alternating):                                                          
                error += 1
                continue
            else:
                self.log("Running flow {0}, {1} messages".format(flow,len(messages)))                
                curstate = self.__start
                msg_keys = messages.keys()
                for msg_key in msg_keys:
                    message = messages[msg_key]
                    self.log("Message {0} ({1}): {2}, hash {3} with format {4}".format(msg_key,message[1],message[0].get_message(), message[0].getCluster().getFormatHash(),message[0].getCluster().get_formats()))
                    # Walk transitions for curstate and message's hash
                    cluster = message[0].getCluster()
                    hash = cluster.getFormatHash()
                    regexp = message[0].getCluster().getRegEx()
                    regexpvisual = message[0].getCluster().getRegExVisual()
                        
                    self.__alphabet.add(hash)
                    #direction = message
                    
                    # ReverX state merging
                    # Search transitions for an element with the same hash (transition).
                    # If found add "cur, hash, existingState" for this message and continue
                    # with the next one
                    # In the ReverX paper, this step is executed after the trivial DFA is built.
                    # However it should be possible as well to do this during the build phase like done here
                    
                    existingTransition = self.findTransition(curstate, hash)
                    #existingTransition = self.findTransitionBySrc(curstate, hash)
                    
                    if self.__config.fastReverXStage1 and self.__config.performReverXMinimization: # Perform quick stage 1 if ReverX minimization is desired at all
                        if existingTransition:
                            if existingTransition.getSource()==curstate:
                                # Exactly this transition exists
                                existingTransition.incCounter() # Inc link usage
                                self.log("Exactly this transition already exists")
                                if msg_key == msg_keys[-1]: # Is this the last
                                    self.__finals.add(existingTransition.getDestination()) 
                                curstate = existingTransition.getDestination()
                                continue
                            else: # A transition with this hash does exist, but from a different src state
                                self.addTransition(curstate,hash,existingTransition.getDestination(), message[1], message[0].get_message(),regexp, regexpvisual, cluster)
                                curstate = existingTransition.getDestination()
                                self.log("A transition with this hash already exists, bending link to ({0},{1},{2})".format(curstate, hash, existingTransition.getDestination()))
                                if msg_key == msg_keys[-1]: # Is this the last
                                    self.__finals.add(existingTransition.getDestination()) 
                                continue
                        else: # This transition does not yet exist, add new transition with new state    
                            #newstate = "s{0}".format(self.__nextstate)
                            stateType = self.determineStateType(message[1])
                            newstate = State("s{0}".format(self.__nextstate), stateType, self)
                            self.__states.append(newstate)
                            self.addTransition(curstate,hash,newstate, message[1], message[0].get_message(), regexp, regexpvisual, cluster)
                            self.__nextstate += 1
                            self.log("Created new state in transition ({0},{1},{2},{3},1,{4})".format(curstate,hash,newstate, message[1], message[0].get_message()))
                            curstate = newstate
                            if msg_key == msg_keys[-1]: # Is this the last
                                self.__finals.add(newstate)
                    else: # Perform Reverx stage 1 later on, build SM stupid
                        if existingTransition and existingTransition.getSource()==curstate:
                            # Exactly this transition exists
                            existingTransition.incCounter() # Inc link usage
                            self.log("Exactly this transition already exists")
                            if msg_key == msg_keys[-1]: # Is this the last
                                self.__finals.add(existingTransition.getDestination()) 
                            curstate = existingTransition.getDestination()
                            continue
                        else:
                            #newstate = "s{0}".format(self.__nextstate)
                            stateType = self.determineStateType(message[1])
                            newstate = State("s{0}".format(self.__nextstate), stateType, self)
                            self.__states.append(newstate)
                            self.addTransition(curstate,hash,newstate, message[1], message[0].get_message(), regexp, regexpvisual, cluster)
                            self.__nextstate += 1
                            self.log("Created new state in transition ({0},{1},{2},{3},1,{4})".format(curstate,hash,newstate, message[1], message[0].get_message()))
                            curstate = newstate
                            if msg_key == msg_keys[-1]: # Is this the last
                                self.__finals.add(newstate)
                            
        if error>0:
            print "{0} errors observed during statemachine bulding".format(error)
        
        
        self.pruneOutliers()
                    
        self.collapse_finals()
        
        if self.__config.performReverXMinimization:
            print "Performing ReverX merge. Number of states {0}, transitions {1}".format(len(self.__states), len(self.__transitions))
            self.reverx_merge()
            print "Performed ReverX merge. Number of states {0}, transitions: {1}".format(len(self.__states),len(self.__transitions))
            self.collapse_finals()
        else:
            print("ReverX merge disabled by configuration")
        
        
        if self.__config.debug:
            print "Finished"
            print "States: ", ",".join(x.getName() for x in self.__states)
            
            print "Transitions: "
            for t in self.__transitions:
                print t
            print "Finals: ", ",".join(x.getName() for x in self.__finals)
            
            print "Consistency check: (States in transitions but not in list of states)"
            c = set()
            for t in self.__transitions:
                if not t.getSource() in self.__states:
                    c.add(t.getSource())
                if not t.getDestination() in self.__states:
                    c.add(t.getDestination())
            print c
    
    def determineStateType(self, clusterType):
        if clusterType=='server2client':
            stateType = State.typeIncomingServer2ClientMsg
        elif clusterType=='client2server':
            stateType = State.typeIncomingClient2ServerMsg
        else:
            stateType = State.typeIncomingNoneMsg 
        return stateType
                            
                  
    def pruneOutliers(self):
        # Rationale:
        # Find all nodes that are reached by transitions (== that are on the rhs)
        # removeOrphans:
        # Then substract this list from the list of all nodes --> unreachable nodes
        # Then remove all transitions where these nodes are src or dest
        # Then perform recursion until nolonger nodes are deleted
        
        if not self.__config.pruneDFAOutliers:
            return
        print "Trying to prune state machine outliers with link score below {0}".format(self.__config.pruneBelowLinkScore)
        if self.__config.performReverXMinimization and self.__config.fastReverXStage1:
            print "WARNING: Statemachine was built with fast ReverX stage 1. Pruning will probably falsify results!"
        
        print "Pruning transitions..."
        prunedTransitions = 0
        for t in copy.copy(self.__transitions):
            if t.getCounter()<self.__config.pruneBelowLinkScore:
                self.__transitions.remove(t)
                prunedTransitions += 1
        
        print "Pruned {0} transitions".format(prunedTransitions)
        
        if prunedTransitions == 0:
            print "No transitions pruned, no need to prune states. Pruning finished"
            return
        
        nodesPruned = self.removeOrphans()
        print "Pruned {0} nodes".format(nodesPruned)
        
    
    def removeOrphans(self, removed=0):
        
        nodesPruned = 0
        reachable = set()
        states = set(self.__states)
        for t in self.__transitions:
            s = t.getDestination()
            reachable.add(s)
        reachable.add(self.__start) # Always declare the start node reachable 
        if len(reachable)!=len(states): # Not all states could be reached
            nodesToPrune = states.difference(reachable)
            nodesPruned = len(nodesToPrune) 
            for s in nodesToPrune:
                if s in self.__finals:
                    self.__finals.remove(s)                            
                self.__states.remove(s)
            
                for t in copy.copy(self.__transitions):
                    if t.getSource()==s or t.getDestination()==s:
                        self.__transitions.remove(t)
            self.removeOrphans(removed=nodesPruned)
        return nodesPruned+removed

    def canTransition(self, p,q):
        l = []
        for s in self.__alphabet:
            r = self.getState(p,s)
            t = self.getState(q,s)
            if r==None or t==None:
                continue
            l.append(s)
        if len(l)==0:
            return None
        return l
    
    def reverx_merge(self):
        import time
        if self.__config.nativeReverXStage1:
            start = time.time()
            print "Performing native ReverX merge stage 1"
            # merge states reached from similar message types
        
            for q in self.__states[:]:
                if q not in self.__states: # Has q already been removed in a previous iteration?
                    continue
                for p in self.__states[:]:
                    if p not in self.__states: # Has p already been removed in a previous iteration?
                        continue
                    #if p=="e" or q=="e" or q==p or (p not in self.__states) or (q not in self.__states):
                    #    continue
                    
                    s = self.canTransition(p,q)
                    
                    if not s==None:
                        # Check if getState returned multiple destinations (== NFA!!)
                        # for the same transition and collapse them
                        if p==q:
                            for elem in s:
                                dests = self.getState(p,elem)
                                
                                #while dests!=None and len(dests)>1:
                                sub_finals = []
                                sub_nonfinals = []
                                if dests!=None:
                                    for i in dests:
                                        if i in self.__finals:
                                            sub_finals.append(i)
                                        else:
                                            sub_nonfinals.append(i)
                                while dests!=None and (len(sub_finals)>1 or len(sub_nonfinals)>1):
                                
                                #if dests!=None and len(dests)>1:
                                    # Added constraint that a mixture of final and non final states may never be merged
                                    
                                    # Split dests in lists for final and non finals
                                    sub_finals = []
                                    sub_nonfinals = []
                                    for i in dests:
                                        if i in self.__finals:
                                            sub_finals.append(i)
                                        else:
                                            sub_nonfinals.append(i)
                                    # Merge each list on its own
                                    while len(sub_finals)>1:
                                        self.mergeStates(sub_finals[0], sub_finals[1])
                                        sub_finals.pop(0)
                                        
                                    while len(sub_nonfinals)>1:
                                        self.mergeStates(sub_nonfinals[0], sub_nonfinals[1])
                                        sub_nonfinals.pop(0)
                                    
                                    #if ((dests[0] in self.__finals and dests[1] in self.__finals) or
                                    #    (dests[0] not in self.__finals and dests[1] not in self.__finals)
                                    #    ) and (dests[0].getType()==dests[1].getType()):
                                    #    self.mergeStates(dests[0],dests[1])
                                    dests = self.getState(p,elem)
                                    sub_finals = []
                                    sub_nonfinals = []
                                    if dests!=None:
                                        for i in dests:
                                            if i in self.__finals:
                                                sub_finals.append(i)
                                            else:
                                                sub_nonfinals.append(i)    
                                
                        s = self.canTransition(p,q)
                        if not s==None:   
                            for elem in s:
                                m1 = self.getState(p,elem)
                                m2 = self.getState(q,elem)
                                if not (m1==None or m2==None):
                                    # Added constraint that a mixture of final and non final states may never be merged
                                    if (self.statesAreBothFinal(m1[0],m2[0]) or self.statesAreBothNotFinal(m1[0],m2[0])) and self.statesHaveSameType(m1[0],m2[0]):
                            
                                    #if ((m1[0] in self.__finals and m2[0] in self.__finals) or 
                                     #   (m1[0] not in self.__finals and m2[0] not in self.__finals)
                                      #  ) and (m1[0].getType()==m2[0].getType()):
                                        self.mergeStates(m1[0],m2[0])
                            
                        
            elapsed = (time.time() - start)
                    
            if self.__config.debug:
                print "Transitions:"
                for t in self.__transitions:
                    print t
            print "Performed ReverX merge stage 1. {} states left, transitions {} (Took: {:.3f} seconds)".format(len(self.__states),len(self.__transitions), elapsed)
        else:
            print "Skipping native ReverX merge stage 1 by configuration"    
            
            
        # Begin ReverX Stage 2
        if not self.__config.performReverXStage2:
            return
           
        print "Performing ReverX merge stage 2"
        # merge states without a causal relation that share at least one message type
        start = time.time()
        reduce = True
        while reduce:
            reduce = False
            for q in self.__states[:]:
                if q not in self.__states: # Has q already been removed in a previous iteration
                    continue
                for p in self.__states[:]:
                    if p not in self.__states: # Has p already been removed in a previous iteration?
                        continue
                    if p.getName()=="e" or q.getName()=="e" or q==p or (p not in self.__states) or (q not in self.__states):
                        continue
                    # if there is not a causal relation
                    if (not self.referenceBetween(p,q)) or self.isMutualReachable(p,q):
                        if self.canReachSameState(p,q):
                            # Added constraint that a mixture of final and non final states may never be merged
                            if (self.statesAreBothFinal(p,q) or self.statesAreBothNotFinal(p,q)) and self.statesHaveSameType(p,q):
                            #if ((p in self.__finals and q in self.__finals) or
                            #    (p not in self.__finals and q not in self.__finals)
                            #    ) and (p.getType()==q.getType()):    
                                self.mergeStates(p,q)
                                reduce = True
            #self.minimize_dfa()
        elapsed = (time.time() - start)
        print "Transitions:"
        for t in self.__transitions:
            print t
        print "Performed ReverX merge stage 2. {} states left, transitions {} (Took: {:.3f} seconds)".format(len(self.__states),len(self.__transitions), elapsed)
        return
    
    ###
    # Working version without considerng final/non finals and without type distinction
    #===========================================================================
    # def reverx_merge(self):
    #    import time
    #    if self.__config.nativeReverXStage1:
    #        start = time.time()
    #        print "Performing native ReverX merge stage 1"
    #        # merge states reached from similar message types
    #    
    #        for q in self.__states[:]:
    #            for p in self.__states[:]:
    #                #if p=="e" or q=="e" or q==p or (p not in self.__states) or (q not in self.__states):
    #                #    continue
    #                
    #                s = self.canTransition(p,q)
    #                
    #                if not s==None:
    #                    # Check if getState returned multiple destinations (== NFA!!)
    #                    # for the same transition and collapse them
    #                    if p==q:
    #                        for elem in s:
    #                            dests = self.getState(p,elem)
    #                            
    #                            while dests!=None and len(dests)>1:
    #                                self.mergeStates(dests[0],dests[1])
    #                                dests = self.getState(p,elem)
    #                            
    #                    s = self.canTransition(p,q)
    #                    if not s==None:   
    #                        for elem in s:
    #                            m1 = self.getState(p,elem)
    #                            m2 = self.getState(q,elem)
    #                            if not (m1==None or m2==None):
    #                                self.mergeStates(m1[0],m2[0])
    #                        
    #                    
    #        elapsed = (time.time() - start)
    #                
    #        if self.__config.debug:
    #            print "Transitions:"
    #            for t in self.__transitions:
    #                print t
    #        print "Performed ReverX merge stage 1. {} states left, transitions {} (Took: {:.3f} seconds)".format(len(self.__states),len(self.__transitions), elapsed)
    #    else:
    #        print "Skipping native ReverX merge stage 1 by configuration"    
    #    print "Performing ReverX merge stage 2"
    #    # merge states without a causal relation that share at least one message type
    #    start = time.time()
    #    reduce = True
    #    while reduce:
    #        reduce = False
    #        for q in self.__states[:]:
    #            for p in self.__states[:]:
    #                if p=="e" or q=="e" or q==p or (p not in self.__states) or (q not in self.__states):
    #                    continue
    #                # if there is not a causal relation
    #                if (not self.referenceBetween(p,q)) or self.isMutualReachable(p,q):
    #                    if self.canReachSameState(p,q):
    #                        self.mergeStates(p,q)
    #                        reduce = True
    #        #self.minimize_dfa()
    #    elapsed = (time.time() - start)
    #    print "Transitions:"
    #    for t in self.__transitions:
    #        print t
    #    print "Performed ReverX merge stage 2. {} states left, transitions {} (Took: {:.3f} seconds)".format(len(self.__states),len(self.__transitions), elapsed)
    #    return
    #===========================================================================

    ###
    
    def statesAreBothFinal(self,p,q):
        return p in self.__finals and q in self.__finals
    
    def statesAreBothNotFinal(self,p,q):
        return (p not in self.__finals) and (q not in self.__finals)
    
    def statesHaveSameType(self,p,q):
        return p.getType()==q.getType()
               
    def canReachSameState(self,p,q):
        for s in self.__alphabet:
            r1 = self.getState(p,s)
            r2 = self.getState(q,s)
            if not (r1 == None or r2==None):
                if r1==r2:
                    return True
        return False
    
    def getState(self,p,s):
        l = []
        
        for t in self.__transitions:
            if t.getSource()==p and t.getHash()==s:
                l.append(t.getDestination())
        if len(l)==0:
            return None       
        return l 
    
    def mergeStates(self,p,q):
        """Merges p into q. All transitions to p are moved to q.
        If p was the start or current state, those are also moved to q.
        """
        if p==q:
            return False
    
        # Make sure that final and non final states are never merged
        
        if not (self.statesAreBothFinal(p, q) or self.statesAreBothNotFinal(p, q)):
        #if not ((p in self.__finals and q in self.__finals) or (
        #    p not in self.__finals and q not in self.__finals)):
            raise Exception("Final and non final states must not be merged!")
        
        
        if not self.statesHaveSameType(p, q):
            #if p.getType()!=q.getType()):
            raise Exception("Must not merge states with different state types")
        
        print "Merging states {0} and {1} to {1}, total states left {2}".format(p,q, len(self.__states)-1)
        self.__states.remove(p)
        if p in self.__finals:
            self.__finals.remove(p)
            # if p was a final and p and q are merged, q has to be final too
            self.__finals.add(q)
        
        #if self.current_state == q1:
        #    self.current_state = q2
        if self.__start == p:
            self.__start = q
        
        for t in copy.copy(self.__transitions):
            # Redirect target states
            
            if t.getSource()==p or t.getDestination()==p:
                self.__transitions.remove(t)
                if t.getSource()==p:
                    t.setSource(q)
                if t.getDestination()==p:
                    t.setDestination(q)
                self.__transitions.add(t)
            #===================================================================
            # if t.getSource()==p:
            #    print t
            #    #self.__transitions.remove(t)
            #    self.__transitions.remove(t)
            #    t.setSource(q)
            #    self.__transitions.add(t)
            #    
            # if t.getDestination()==p:
            #    print t
            #    self.__transitions.remove(t)
            #    t.setDestination(q)
            #    self.__transitions.add(t)
            #===================================================================
        
        return True
    
    def referenceBetween(self, p, q):
        # Checks for causal relation between two states
        # Returns True if q can be reached from p via an s
        # or p can be reached via q via an s as well
        # else False
        referenceBetween = False
        for s in self.__alphabet:
            if self.has_transition(q,s,p) or self.has_transition(p,s,q):
                referenceBetween = True
                break
        return referenceBetween
    
    def isMutualReachable(self, p, q):
        # Checks for causal relation between two states
        # Returns True if q can be reached from p via an s
        # and p can be reached via q via an t as well
        # else False
        
        for s in self.__alphabet:
            if self.has_transition(q,s,p):
                for t in self.__alphabet:
                    if s==t:
                        continue
                    if self.has_transition(p,t,q):
                        return True
        return False
   
    def get_transitions_from(self, p):
        l = []
        for t in self.__transitions:
            if t.getSource()==p:
                l.append(t)
        return l
    
    def has_transition(self, p,s,q):
        for t in self.__transitions:
            if t.getSource()==p and t.getHash()==s and t.getDestination()==q:
                return True
        return False
     
    def collapse_finals(self):
        if self.__config.collapseFinals:
            
            print "Collapsing final states"
            # Collapse finals based on node type
            client2ServerFinals = []
            server2ClientFinals = []
            noneTypeFinals = []
            for n in self.__finals:
                if n.getType()==State.typeIncomingClient2ServerMsg:
                    client2ServerFinals.append(n)
                elif n.getType()==State.typeIncomingServer2ClientMsg:
                    server2ClientFinals.append(n)
                else: 
                    noneTypeFinals.append(n)
            # Merge client2Server finals
            while len(client2ServerFinals)>1:
                #l = list(client2ServerFinals)
                #self.mergeStates(l[0], l[1])
                #client2ServerFinals.remove(l[0])
                self.mergeStates(client2ServerFinals[0], client2ServerFinals[1])
                client2ServerFinals.pop(0)
                
            # Merge server2Client finals
            while len(server2ClientFinals)>1:
                #l = list(server2ClientFinals)
                #self.mergeStates(l[0], l[1])
                #server2ClientFinals.remove(l[0])
                self.mergeStates(server2ClientFinals[0], server2ClientFinals[1])
                server2ClientFinals.pop(0)
                
            # Merge finals of unknown type (there should be none...)
            while len(noneTypeFinals)>1:
                #l = list(noneTypeFinals)
                #self.mergeStates(l[0], l[1])
                #noneTypeFinals.remove(l[0])
                self.mergeStates(noneTypeFinals[0], noneTypeFinals[1])
                noneTypeFinals.pop(0)
                
            self.__finals = []
            self.__finals.extend(client2ServerFinals)
            self.__finals.extend(server2ClientFinals)
            self.__finals.extend(noneTypeFinals)
            
            return
        
          
        #=======================================================================
        # superfinal = "s{0}".format(self.__nextstate)
        # self.__states.append(superfinal)
        # for s in self.__finals:
        #    self.addTransition(s,"{{epsilon}}",superfinal, "epsilon","epsilon", "","")
        # self.__finals = [superfinal]
        #=======================================================================
    #===========================================================================
    # def fakedelta(self,state,c):
    #        if state=="s0":
    #            if c == "a":
    #                return "s2"
    #            return "s1"  
    #        elif state == "s1":
    #            if c== "a":
    #                return "s1"
    #            return "s2"
    #        elif state == "s2":
    #            return "s2"
    #===========================================================================
            
    def dfa(self):
        #states = set([t[0] for t in self.__transitions].extend([t[2] for t in self.__transitions]))
        states = self.__states[:]
        alphabet = set([t.getHash() for t in self.__transitions])  
        alphabet.add("epsilon")   
        delta = self.delta   
        start = self.__start
        self.collapse_finals()
        
        finals = self.__finals[:]
        
        #=======================================================================
        # # Build fake DFA
        # states = ["s0","s1","s2"]
        # finals = ["s1", "s2"]
        # alphabet = ["a","b"]
        # start = "s0"
        # delta = self.fakedelta
        #=======================================================================
        import DFA
        dfa = DFA.DFA(states,alphabet,delta,start,finals)
        #dfa.pretty_print()
        if self.__config.minimizeDFA:            
            print "Minimizing DFA with {0} states... this could take some time...".format(len(states))
            import time
            start = time.time()
            dfa.delete_unreachable()
            classes = dfa.mn_classes()
            map = dfa.collapse(classes)
            elapsed = (time.time() - start)
            #dfa.pretty_print()
            new_states = dfa.states
            print "Finished! Minimizing took {:.3f} seconds (DFA now has {} states)".format(elapsed,len(new_states))
            
            # Use map function to "filter" out data
            for s in self.__states[:]:
                if map[s]!=s: # s was merged into a new state
                    # delete missing state from states
                    if self.__config.debug:
                        print "{0} is an obsolete state. Removing...".format(s)
                    self.__states.remove(s)
                    # delete/change transitions from missing state to mapped state
                    import copy
                    for t in copy.copy(self.__transitions):
                        if t.getSource()==s: # delete outgoing edges
                            self.__transitions.remove(t)
                            if self.__config.debug:
                                print "Deleted outgoing edge {0}".format(t)
                        if t.getDestination()==s: # bend incoming edges
                            t.setDestination(map[s])
                            if self.__config.debug:
                                print "Bended incoming edge from {0} to {1}".format(s,t.getDestination())
                    
                
            new_start = dfa.start
            new_finals = dfa.accepts
            new_delta = dfa.delta
            
        
        #=======================================================================
        # input = []
        # input.append("b3d01d30c9fdf5fe870c4ff2d434f600387f9e59")
        # input.append("85b13991b7fa34ced979df6295c5cb1eda4646e0")
        # input.append("b95d8287988a5bc84b2ae67673a0813e1a37c097")
        # input.append("85b13991b7fa34ced979df6295c5cb1eda4646e0")
        # input.append("e70982702732f3758e4be0eb46dd6126b1b5bb07")
        # input.append("85b13991b7fa34ced979df6295c5cb1eda4646e0")
        # input.append("8ee4b03f8d4746ab66bbdb0c74ff5f1757867759")
        # input.append("85b13991b7fa34ced979df6295c5cb1eda4646e0")
        # input.append("8ee4b03f8d4746ab66bbdb0c74ff5f1757867759")
        # input.append("85b13991b7fa34ced979df6295c5cb1eda4646e0")
        # input.append("8ee4b03f8d4746ab66bbdb0c74ff5f1757867759")
        # input.append("85b13991b7fa34ced979df6295c5cb1eda4646e0")
        # input.append("8ee4b03f8d4746ab66bbdb0c74ff5f1757867759")
        # input.append("85b13991b7fa34ced979df6295c5cb1eda4646e0")
        # input.append("8ee4b03f8d4746ab66bbdb0c74ff5f1757867759")
        # input.append("8ee4b03f8d4746ab66bbdb0c74ff5f1757867759")
        # print dfa.recognizes(input)
        #=======================================================================
        
    def delta(self,state,trans):
        if state=='e': # Error state handling
            return "e"
        for t in self.__transitions:
            if t.getSource()==state and t.getHash() == trans:
                return t.getDestination()
        return "e"
        
        
    # Important observation:
    # ======================
    #
    # We consider a state "final" where the last element of a flow ends, as
    # we cannot assume anything else.
    # Now we currently have three problems with our test sets
    # a) We have a maximum we read:
    #    If our maxMessages ends within reading a flow, we mistakenly consider
    #    our broken flow as final, thus declaring final states where there should be none
    # b) In order to reverse engineer a protocol perfectly, the test data has to be perfect
    #    as well. If we've got invalid protocol behavior - and we HAVE these - our reverse
    #    engineered protocol can never be 100% exact according to spec
    # c) Out ftp testset almost never ends with QUIT but with arbitrary commands. Therefore
    #    we create a lot of finals (not because of a or b), just because it IS the last command/server response
    #    This again does not necessarily reflect the true protocol.
    #
    # The result of this, with respect to the ftp protocol is, that a) our protocol does not finish at the
    # QUIT command, but QUIT is an "arbitrary" command.
    # The expection would be that from our "common middle state, for each command there is an outgoing client transition with the actual command,
    # followed by the server response (good or bad) and then return to the "common middle state".
    # This might also be an explanation for the observed picture of the graphs with these large reflexive
    # transitions. If there is a "faulty" transition somewhere in the beginning, we (might) create a reflexive
    # transition (e.g. return to middle state right after the client (and before the server reply). 
    # In later correct flows, the existing transition is reused and not corrected.
    # 
    
    
     
    def dump_dot(self, file=""):
        """
        Dumps the generated graph to stdout or a .dot file
        """
        if not file == "":            
            import sys
            old_stdout = sys.stdout
            handle = open(file,"w")
            sys.stdout = handle
        
        import string
        import message
        intab = '"'
        outtab = ' '
        trantab = string.maketrans(intab,outtab)
        
        print "digraph G {"
        # Add final node definitions
        for s in self.__finals:
            print '{0} [shape=circle,peripheries=2];'.format(s)
            
        for t in self.__transitions:
            
            s = "'{0}'".format(t.getMessage()[:25].translate(trantab))
            if len(t.getMessage())>25:
                s+="..."
            s+=" ({0})".format(t.getCounter())
            
            if t.getDirection()==message.Message.directionClient2Server:
                color="red"
            elif t.getDirection()==message.Message.directionServer2Client:
                color="green"
            else:
                color="black"
            
            penwidth = 1
            if self.__config.highlightOutlier:
                if t.getCounter()<self.__config.pruneBelowLinkScore: 
                    penwidth = "2,style=dotted"
                    color="blue"
                else:
                    penwidth = 1
            elif self.__config.weightEdges:
                penwidth = t.getCounter()
                            
            print '{0} -> {1} [color={2},fontsize=10,label="{3}",penwidth={4}];'.format(t.getSource(),t.getDestination(),color,s,penwidth)
        print "}"
        if not file=="":
            handle.close()         
            sys.stdout = old_stdout
            import os            
            print "Finished. 'dot' file written to file {}, file size {:.1f} KB".format(file,os.path.getsize(file)/1024.0)               

    def getXMLRepresentation(self):
        """
        Dumps the generated graph to stdout or a .dot file
        """
             
        import sys
        old_stdout = sys.stdout
        #handle = open(filename,"w")
        #print "Writing to {0}".format(filename)
        handle = StringIO()
        sys.stdout = handle
        
    
        print '<protocol_statemachine>'
        print '\t<start_state referencedState="{0}" />'.format(self.__start.getInternalName())
        #print '\t\t<name>{0}</name>'.format(self.__start)
        #print '\t\t<internal_name>{0}</internal_name>'.format(self.__start.getInternalName())
        #print '\t</start_state>'
        print '\t<final_states numOfFinalState="{0}">'.format(len(self.__finals))
        for f in self.__finals:
            print '\t\t<final_state referencedState="{0}" />'.format(f.getInternalName())
            #print '\t\t\t<name>{0}</name>'.format(f)
            #print '\t\t\t<internal_name>{0}</internal_name>'.format(f.getInternalName())
            #print '\t\t</final_state>'
        print '\t</final_states>'
        print '<transitions numOfTransitions="{0}">'.format(len(self.__transitions))
        for idx, t in enumerate(self.__transitions):
            t.getXMLRepresentation()
            #print "Idx: {0}, Internal name: {1}, Source: {2}, Transition: {3}, Destination: {4}, Counter: {5}, Direction: {6}, Cluster-Reference: {7}, RegEx: {8}".format(idx, t.getInternalName(), t.getSource(), t.getHash(), t.getDestination(), t.getCounter(), t.getDirection(), t.getCluster().getInternalName(), t.getRegEx())
        print "</transitions>"
        print "<states>"
        for idx, s in enumerate(self.__states):
            s.getXMLRepresentation()
            #===================================================================
            # t_list = self.get_transitions_from(s)
            # total = 0
            # numOfTrans = len(t_list)
            # for t in t_list:
            #    total += t.getCounter()
            # 
            # print "Idx: {0}, Internal name: {1}, State ID: {2}, State type: {3}, Number of transitions from: {4}".format(idx, s, s.getInternalName(), s.getType(), numOfTrans)
            # for idx2, t in enumerate(t_list):
            #    print "\tIdx: {0}, Internal name: {1}, Probability: {2}".format(idx2, t.getInternalName(), t.getCounter()/float(total))
            # 
            #===================================================================
        print "</states>"
        print '</protocol_statemachine>'    
        body = handle.getvalue()
        handle.close
        sys.stdout = old_stdout
        return body