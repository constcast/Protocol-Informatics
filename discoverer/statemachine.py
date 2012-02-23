'''
Created on 20.02.2012

@author: daubsi
'''

class Statemachine(object):
    '''
    This class represents a statemachine derived from the given message sequences
    and their corresponding formats
    '''

    __states = []
    __transitions = []
    __nextstate = 1

    def __init__(self, sequences):
        '''
        Constructor
        '''
        self.__sequences = sequences
        self.__states.append("s0")
        
    def has_gaps(self,numbers, gap_size):
        # Based on http://stackoverflow.com/questions/4375310/finding-data-gaps-with-bit-masking
        adjacent_differences = [(y - x) for (x, y) in zip(numbers[:-1], numbers[1:])]
        for elem in adjacent_differences:
            if elem>1:
                return True
        return False
        
        
    def build(self):
        
        for flow in self.__sequences:
            messages = self.__sequences[flow]
            message_indices = messages.keys()
            if self.has_gaps(message_indices,1):
                print "ERROR: Flow {0} has gaps in sequences numberings. Have to skip this one".format(flow)
            else:
                print "Running flow {0}, {1} messages".format(flow,len(messages))
                self.__states.append("e") # Error state
                curstate = "s0"
                for msg_id, message in messages.items():
                    print "Message {0} ({1}): {2}, hash {3} with format {4}".format(msg_id,message[1],message[0].get_message(), message[0].getCluster().getFormatHash(),message[0].getCluster().get_formats())
                    # Walk transitions for curstate and message's hash
                    hash = message[0].getCluster().getFormatHash()
                    found = False
                    for transition in self.__transitions:
                        if transition[0]==curstate and transition[1]==hash:
                            found = True
                            curstate = transition[2]
                            transition[4]+=1 # Inc link usage
                            break
                    if not found:
                        newstate = "s{0}".format(self.__nextstate)
                        self.__states.append(newstate)
                        self.__transitions.append([curstate,hash,newstate, message[1],1, message[0].get_message()])
                        self.__nextstate += 1
                        print "Created new state in transition ({0},{1},{2},{3},1,{4})".format(curstate,hash,newstate, message[1], message[0].get_message())
                        curstate = newstate
                    else:
                        print "Already in transition table! Forwarding to state {0}".format(curstate)
        self.compute_finals()
        
        print "Finished"
        print "States: ", "\n".join(self.__states)
        
        print "Transitions: "
        for t in self.__transitions:
            print t
        print "Finals: ", "\n".join(self.__finals)
       
    def compute_finals(self):
        # Compute finals - ugly but quick n dirty
        self.__finals = []
        for t in self.__transitions:
            s = t[2] # designated final state
            isFinal = True
            for t2 in self.__transitions:
                if t2[0] == s:
                    isFinal = False
                    break
            if isFinal:
                self.__finals.append(s)
        superfinal = "s{0}".format(self.__nextstate)
        self.__states.append(superfinal)
        for s in self.__finals:
            self.__transitions.append([s,"epsilon",superfinal, "",1,""])
        self.__finals = [superfinal]
    def fakedelta(self,state,c):
            if state=="s0":
                if c == "a":
                    return "s2"
                return "s1"  
            elif state == "s1":
                if c== "a":
                    return "s1"
                return "s2"
            elif state == "s2":
                return "s2"
            
    def dfa(self):
        #states = set([t[0] for t in self.__transitions].extend([t[2] for t in self.__transitions]))
        states = self.__states[:]
        alphabet = set([t[1] for t in self.__transitions])  
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
                print("{0} is an obsolete state. Removing...".format(s))
                self.__states.remove(s)
                # delete/change transitions from missing state to mapped state
                for t in self.__transitions[:]:
                    if t[0]==s: # delete outgoing edges
                        self.__transitions.remove(t)
                        print("Deleted outgoing edge {0}".format(t))
                    if t[2]==s: # bend incoming edges
                        t[2]=map[s]
                        print("Bended incoming edge from {0} to {1}".format(s,t[2]))
                
            
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
        if state=='e':
            return "e"
        for t in self.__transitions:
            if t[0]==state and t[1] == trans:
                return t[2]
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
            s = t[5][:25].translate(trantab)
            if t[3]=='client':
                print '{0} -> {1} [color=red,fontsize=10,label="{2}...",weight={3}]'.format(t[0],t[2],s,t[4])
            else:
                print '{0} -> {1} [color=green,fontsize=10,label="{2}...",weight={3}]'.format(t[0],t[2],s,t[4])
        print "}"
        if not file=="":
            handle.close()         
            sys.stdout = old_stdout
            import os            
            print "Finished. Written to file {}, file size %0.1f KB" % (file,os.path.getsize(file)/1024.0)               

            