'''
Created on 20.02.2012

@author: daubsi
'''

class Transition(object):
    def __init__(self, src, hash, dest, direction, msg):
        self.__src = src
        self.__hash = hash
        self.__dest = dest
        self.__direction = direction
        self.__msg = msg
        self.__counter = 1
    
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
        self.__start = "s0"
        self.__states = ["s0"]
        self.__transitions = set()
        self.__nextstate = 1
        self.__config = config
        self.__alphabet = set()
        
    def has_gaps(self,numbers, gap_size):
        # Based on http://stackoverflow.com/questions/4375310/finding-data-gaps-with-bit-masking
        adjacent_differences = [(y - x) for (x, y) in zip(numbers[:-1], numbers[1:])]
        for elem in adjacent_differences:
            if elem>1:
                return True
        return False
       
    def findTransition(self,curState, hash):
        # First try to find exact matches
        for t in self.__transitions:
            if t.getSource() == curState and t.getHash()==hash: # Exactly this transition was already in list
                return t      
        # Now a match of the hash is enough    
        for t in self.__transitions:
            if t.getHash() == hash: # This transition is already in list
                return t
        return None
    
    def is_alternating(self, flow):
        messages = self.__sequences[flow]
        direction = ""
        for msg_id, message in messages.items():
            direction2 = messages[1]
            if direction==direction2: # Current message has same direction as message before
                return False
        return True
    
    def addTransition(self,src,trans,dest, direction, msg):
        self.__transitions.add(Transition(src,trans,dest,direction,msg))
        
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
    
    def build(self):
        self.__states.append("e") # Error state
        for flow in self.__sequences:
            messages = self.__sequences[flow]
            if len(messages)==1:
                if self.__config.debug:
                    print "Flow {0} has only 1 message. Skipping flow".format(flow)
                continue
            message_indices = messages.keys()
            if self.has_gaps(message_indices,1):
                print "ERROR: Flow {0} has gaps in sequences numberings. Skipping flow".format(flow)
            elif not self.is_alternating(flow):
                print "ERROR: Flow {0} is not strictly alternating between client and server. Skippng flow".format(flow)
                pass
            else:
                if self.__config.debug:
                    print "Running flow {0}, {1} messages".format(flow,len(messages))                
                curstate = "s0"
                for msg_id, message in messages.items():
                    if self.__config.debug:
                        print "Message {0} ({1}): {2}, hash {3} with format {4}".format(msg_id,message[1],message[0].get_message(), message[0].getCluster().getFormatHash(),message[0].getCluster().get_formats())
                    # Walk transitions for curstate and message's hash
                    hash = message[0].getCluster().getFormatHash()
                    self.__alphabet.add(hash)
                    #direction = message
                    
                    # ReverX state merging
                    # Search transitions for an element with the same hash (transition).
                    # If found add "cur, hash, existingState" for this message and continue
                    # with the next one
                    # In the ReverX paper, this step is executed after the trivial DFA is built.
                    # However it should be possible as well to do this during the build phase
                    
                    existingTransition = self.findTransition(curstate, hash)
                    if existingTransition:
                        if existingTransition.getSource()==curstate:
                            # Exactly this transition exists
                            curstate = existingTransition.getDestination()
                            existingTransition.incCounter() # Inc link usage
                            if self.__config.debug:
                                print "Exactly this transition already exists"
                            continue
                        else: # A transition with this hash does exist, but from a different src state
                            self.addTransition(curstate,hash,existingTransition.getDestination(), message[1], message[0].get_message())
                            curstate = existingTransition.getDestination()
                            if self.__config.debug:
                                print "A transition with this hash already exists, bending link to ({0},{1},{2})".format(curstate, hash, existingTransition.getDestination())
                            continue
                    else: # This transition does not yet exist, add new transition with new state    
                        newstate = "s{0}".format(self.__nextstate)
                        self.__states.append(newstate)
                        self.addTransition(curstate,hash,newstate, message[1], message[0].get_message())
                        self.__nextstate += 1
                        if self.__config.debug:
                            print "Created new state in transition ({0},{1},{2},{3},1,{4})".format(curstate,hash,newstate, message[1], message[0].get_message())
                        curstate = newstate
                    
        #=======================================================================
        #                
        #                found = False
        #            for transition in self.__transitions:
        #                # Check for equiality of current state, transitional hash and client2server or server2client
        #                if transition[0]==curstate and transition[1]==hash and transition[3]==message[1]:
        #                    found = True
        #                    curstate = transition[2]
        #                    transition[4]+=1 # Inc link usage
        #                    break
        #            if not found:
        #                newstate = "s{0}".format(self.__nextstate)
        #                self.__states.append(newstate)
        #                self.__transitions.append([curstate,hash,newstate, message[1],1, message[0].get_message()])
        #                self.__nextstate += 1
        #                if self.__config.debug:
        #                    print "Created new state in transition ({0},{1},{2},{3},1,{4})".format(curstate,hash,newstate, message[1], message[0].get_message())
        #                curstate = newstate
        #            else:
        #                if self.__config.debug:
        #                    print "Already in transition table! Forwarding to state {0}".format(curstate)
        #=======================================================================
        
        self.compute_finals()
        print "Performing ReverX merge. Number of states {0}, transitions {1}".format(len(self.__states), len(self.__transitions))
        self.reverx_merge()
       
        print "Performed ReverX merge. Number of states {0}, transitions: {1}".format(len(self.__states),len(self.__transitions))
        self.compute_finals()
        
        if self.__config.debug:
            print "Finished"
            print "States: ", "\n".join(self.__states)
            
            print "Transitions: "
            for t in self.__transitions:
                print t
            print "Finals: ", "\n".join(self.__finals)
    
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
        start = time.time()
        print "Performing ReverX merge stage 1"
        # merge states reached from similar message types
    
        for q in self.__states[:]:
            for p in self.__states[:]:
                #if p=="e" or q=="e" or q==p or (p not in self.__states) or (q not in self.__states):
                #    continue
                
                s = self.canTransition(p,q)
                
                if not s==None:
                    # Check if getState returned multiple destinations (== NFA!!)
                    # for the same transition and collapse them
                    if p==q:
                        for elem in s:
                            dests = self.getState(p,elem)
                            
                            while dests!=None and len(dests)>1:
                                self.mergeStates(dests[0],dests[1])
                                dests = self.getState(p,elem)
                            
                    s = self.canTransition(p,q)
                    if not s==None:   
                        for elem in s:
                            m1 = self.getState(p,elem)
                            m2 = self.getState(q,elem)
                            if not (m1==None or m2==None):
                                self.mergeStates(m1[0],m2[0])
                        
                    
        elapsed = (time.time() - start)
                
        print "Transitions:"
        for t in self.__transitions:
            print t
        print "Performed ReverX merge stage 1. {} states left, transitions {} (Took: {:.3f} seconds)".format(len(self.__states),len(self.__transitions), elapsed)
        
        print "Performing ReverX merge stage 2"
        # merge states without a causal relation that share at least one message type
        start = time.time()
        reduce = True
        while reduce:
            reduce = False
            for q in self.__states[:]:
                for p in self.__states[:]:
                    if p=="e" or q=="e" or q==p or (p not in self.__states) or (q not in self.__states):
                        continue
                    # if there is not a causal relation
                    if (not self.referenceBetween(p,q)) or self.isMutualReachable(p,q):
                        if self.canReachSameState(p,q):
                            self.mergeStates(p,q)
                            reduce = True
            #self.minimize_dfa()
        elapsed = (time.time() - start)
        print "Transitions:"
        for t in self.__transitions:
            print t
        print "Performed ReverX merge stage 2. {} states left, transitions {} (Took: {:.3f} seconds)".format(len(self.__states),len(self.__transitions), elapsed)
        return
                        
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
    
        
        print "Merging states {0} and {1} to {1}".format(p,q)
        self.__states.remove(p)
        if p in self.__finals:
            self.__finals.remove(p)
        
        #if self.current_state == q1:
        #    self.current_state = q2
        if self.__start == p:
            self.__start = q
        import copy
        for t in copy.copy(self.__transitions):
            # Redirect target states
            if t.getSource()==p:
                #self.__transitions.remove(t)
                self.__transitions.remove(t)
                t.setSource(q)
                self.__transitions.add(t)
                continue
            if t.getDestination()==p:
                self.__transitions.remove(t)
                t.setDestination(q)
                self.__transitions.add(t)
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
    
    def has_transition(self, p,s,q):
        for t in self.__transitions:
            if t.getSource()==p and t.getHash()==s and t.getDestination()==q:
                return True
        return False
     
    def compute_finals(self):
        # Compute finals - ugly but quick n dirty
        self.__finals = []
        for t in self.__transitions:
            s = t.getDestination() # designated final state
            isFinal = True
            for t2 in self.__transitions:
                if t2.getSource() == s:
                    isFinal = False
                    break
            if isFinal:
                self.__finals.append(s)
        superfinal = "s{0}".format(self.__nextstate)
        self.__states.append(superfinal)
        for s in self.__finals:
            self.addTransition(s,"epsilon",superfinal, "epsilon","epsilon")
        self.__finals = [superfinal]
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
        start = "s0"
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
                    for t in self.__transitions[:]:
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
        
    def dump(self, file=""):
        """
        Dumps the generated graph to stdout or a .dot file
        """
        if not file == "":            
            import sys
            old_stdout = sys.stdout
            handle = open(file,"w")
            sys.stdout = handle
        
        import string
        intab = '"'
        outtab = ' '
        trantab = string.maketrans(intab,outtab)
        
        print "digraph G {"
        for t in self.__transitions:
            s = t.getMessage()[:25].translate(trantab)
            if t.getDirection()=='client':
                print '{0} -> {1} [color=red,fontsize=10,label="{2}...",penwidth={3}]'.format(t.getSource(),t.getDestination(),s,t.getCounter() if self.__config.weightEdges else 1)
            elif t.getDirection()=='server':
                print '{0} -> {1} [color=green,fontsize=10,label="{2}...",penwidth={3}]'.format(t.getSource(),t.getDestination(),s,t.getCounter() if self.__config.weightEdges else 1)
            else:
                print '{0} -> {1} [color=black,fontsize=10,label="{2}...",penwidth={3}]'.format(t.getSource(),t.getDestination(),s,t.getCounter() if self.__config.weightEdges else 1)
        print "}"
        if not file=="":
            handle.close()         
            sys.stdout = old_stdout
            import os            
            print "Finished. 'dot' file written to file {}, file size {:.1f} KB".format(file,os.path.getsize(file)/1024.0)               

            