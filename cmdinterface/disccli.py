# vim: set sts=4 sw=4 cindent nowrap expandtab:

# CLI file for the "Discoverer" submodule

import cmd, sys, os
import discoverer
import cli
from discoverer.message import Message
import time
import collections
import discoverer.statemachine

class DiscovererCommandLineInterface(cli.CommandLineInterface):
    def __init__(self, env, config):
        cmd.Cmd.__init__(self)
        self.env = env
        self.config = config

    def do_EOF(self, string):
        return True

    def do_exit(self, string):
        return True

    def do_quit(self, string):
        return True
        
    def setup(self, sequences): #, direction):        
        print "Performing initial message analysis and clustering"
        if sequences == None:        
            print "FATAL: No sequences loaded yet!"
            return False    
        
        #setup = discoverer.setup.Setup(sequences, direction, self.config)
        setup = discoverer.setup.Setup(sequences, self.config)
        
        self.env['cluster_collection'] = setup.get_cluster_collection()
        print "Built {0} clusters".format(setup.get_cluster_collection().num_of_clusters())
      
    def do_format_inference(self, string):
        print "Performing format inference on initial clusters"
        if not self.env.has_key('cluster_collection'):
            print "FATAL: Initial clustering not yet performed. Run 'setup' first pleaset!"
            return False    
        discoverer.formatinference.perform_format_inference_for_cluster_collection(self.env['cluster_collection'], self.config)
    
    def do_semantic_inference(self, string):
        print "Performing semantic inference on messages"
        if not self.env.has_key('cluster_collection'):
            print "FATAL: Initial clustering not yet performed. Run 'setup' first pleaset!"
            return False    
        discoverer.semanticinference.perform_semantic_inference(self.env['cluster_collection'], self.config)
    
    def do_recursive_clustering(self, string):
        print "Performing recursive clustering"
        if not self.env.has_key('cluster_collection'):
            print "FATAL: Initial clustering not yet performed. Run 'setup' first pleaset!"
            return False    
        discoverer.recursiveclustering.perform_recursive_clustering(self.env['cluster_collection'], 0)
    
    def do_fix_tokenization_errors(self, string):
        print "Fixing tokenization errors"
        if not self.env.has_key('cluster_collection'):
            print "FATAL: Initial clustering not yet performed. Run 'setup' first pleaset!"
            return False    
        self.env['cluster_collection'].fix_tokenization_errors(self.config)
        # Next two calls are needed in order to reflect the new structure
        self.do_format_inference("")
        self.do_semantic_inference("")
        print "Finished fixing tokenization errors"
        
    def help_go(self):
        print "Automatically executes all steps needed to perfom the 'Discoverer' algorithm on the set of messages"
            
            
    def do_go(self, string):
        if self.env.has_key('cluster_collection'):
            del(self.env['cluster_collection'])
             
        if self.config.loadClientAndServerParts == True:
            # Delete old generated structures
            
            
            
            #===================================================================
            # if self.env.has_key('cluster_collection_client'):
            #    del(self.env['cluster_collection_client'])
            # if self.env.has_key('cluster_collection_server'):
            #    del(self.env['cluster_collection_server'])
            # 
            # 
            #===================================================================
            # Perform discoverer for both parts
            self.go(self.env['sequences'])
            
            #self.go(self.env['sequences_client2server'], Message.directionClient2Server)
            #self.env['cluster_collection_client'] = self.env['cluster_collection']
            
            #self.combineflows(self.env['cluster_collection_client'],Message.directionClient2Server)
            #===================================================================
            # if self.env.has_key('cluster_collection'):
            #    del(self.env['cluster_collection'])
            # 
            #===================================================================
            #print "-----------------Server2client-----------------------"
            #self.go(self.env['sequences_server2client'],Message.directionServer2Client)
            #self.env['cluster_collection_server'] = self.env['cluster_collection']
            #self.combineflows(self.env['cluster_collection_server'],Message.directionServer2Client)
             
            
            #===================================================================
            # for c in self.env['cluster_collection'].get_all_cluster():
            #    print "Cluster:"
            #    print c.get_formats()
            #    print c.getRegEx()
            #    print c.getRegExVisual()
            #    print
            #===================================================================
                
            
            # Build statemachine
            
            sm = discoverer.statemachine.Statemachine(self.env['messageFlows'], self.config)
            self.env['sm'] = sm
            start = time.time()
              
            sm.build()
            duration = time.time()-start
            print "Statemachine building took {:.3f} seconds".format(duration)
            path = os.path.normpath(self.config.dumpFile)
            file = os.path.basename(self.config.inputFile)
            (filename,ext) = os.path.splitext(file)
            storePath = "{0}{1}{2}.dot".format(path,os.sep,filename) 
            #sm.dfa()
            #sm.fake()
            print "Dumping state machine"
            sm.dump_dot(storePath)
            sm.dumpTransitions()
            storePath = "{0}{1}{2}_statemachine.xml".format(path,os.sep,filename) 
            #sm.dumpStructure()
            
            
            #sm.dumpStructure(storePath)
            self.do_dumpresult("")
            
            #pickled = sm.pickle()
            #import cPickle
            #anothersm = cPickle.loads(pickled)
            #anothersm.dump("/Users/daubsi/Dropbox/anotherdump")
            self.do_dump_state("")
            self.createXMLOutput()
            
            
        else:
            # Perform discoverer only for client pat
            self.go(self.env['sequences'],"unknownDirection")
    
    def dump_sm_dot(self, filename=""):
        if filename=="":
            path = os.path.normpath(self.config.dumpFile)
            file = os.path.basename(self.config.inputFile)
            (filename,ext) = os.path.splitext(file)
            storePath = "{0}{1}{2}.dot".format(path,os.sep,filename) 
        else:
            storePath = filename               
        self.env['sm'].dump_dot(storePath)
         
    def do_dump_sm_dot(self, string):
        self.dump_sm_dot()
        
    def createXMLOutput(self):
        import os
        path = os.path.normpath(self.config.dumpFile)
        file = os.path.basename(self.config.inputFile)
        (filename,ext) = os.path.splitext(file)
        storePath = "{0}{1}{2}_output.xml".format(path,os.sep,filename)
        
        import sys
        import codecs
        old_stdout = sys.stdout
        handle = codecs.open(storePath,"w", "utf-8-sig")
        sys.stdout = handle
        
        print '<?xml version="1.0" encoding="utf-8" ?>'
        print "<protocolInformatics>"
        print self.getCCXMLRepresentation()
        print self.env['sm'].getXMLRepresentation()  
        print "</protocolInformatics>"
        
        handle.close()         
        sys.stdout = old_stdout
        import os            
        print "Finished XML output. File size %0.1f KB" % (os.path.getsize(storePath)/1024.0)         

    def do_createXMLOutput(self, string):
        self.createXMLOutput()
    
    def do_load_testdata(self, args=""):
        if len(args)!=0:
            tok = args.split()
            fileName = tok[0]
            element = int(tok[1])
            
        fileName = self.config.testFile
        import common
        import cmdinterface
        
            
        client2server_file = "{0}_client".format(fileName)
        server2client_file = "{0}_server".format(fileName)
        
        print "Loading {0} entries from test data from {1}".format(self.config.numOfTestEntries,client2server_file) 
        sequences_client2server = sequences = common.input.Bro(client2server_file, self.config.numOfTestEntries).getConnections()
        print "Loading {0} entries from test data from {1}".format(self.config.numOfTestEntries, server2client_file)
        sequences_server2client = sequences = common.input.Bro(server2client_file, self.config.numOfTestEntries).getConnections()
        sequences = [(sequences_client2server, Message.directionClient2Server),(sequences_server2client, Message.directionServer2Client)] # Keep it compatible with existing code TODO        
        
        print "Loaded {0} test sequences from input files".format(len(sequences[0][0])+len(sequences[1][0]))
        setup = discoverer.setup.Setup(sequences, self.config)
        testcluster = setup.get_cluster_collection()
        testflows = self.combineflows(testcluster)
        
        self.linkmessages(testflows)
        
        self.env['testflows']=testflows
        
        if self.env.has_key('sm'):
            self.env['sm'].setConfig(self.config)
            self.env['sm'].setTestFlows(testflows)
        
        
    def do_statemachine_accepts(self, args=""):
        # Tries to load the input and returns whether the statemachine accepts this input
        
        # Thoughts:
        # How do I map a single line of input to a transition?
        # A transition is the hash of a rich message format of a single message
        # 
        # Basic Task: Match a single message to the best matching format
        #
        # Idea: Tokenize our single message and create a Message object out of it
        # The transition have linked information about the various messages that
        # are part of the cluster whose hash is the hash of the transition
        #
        # Idea: Compare message format of our single message (only text, binary senseful
        # at this moment) to the formats of the various clusters.
        # Then first examine whether we have perfect matches with respect to text/binary
        # (this might not be the case, if we've got rich cluster formats with merged clusters or sim.
        # If yes, compare the matching clusters's const values with our message and see whether our
        # values match the const value exactly. 
        # If yes and we've only got one cluster that's our transition
        # If yes and we've got multiple matches let's see further
        # if we've got no match regarding the const values there are again 2 possibilities
        # : also consider variable cluster formats (in case our message had indeed a variable instead)
        # : also look for other cluster format combinations (e.g. merged tokens might change the length of the format, which
        # would have sorted this one out in the first instance)
        
        # Furthermore there are more test possibilites
        # e.g. load only client messages and see whether our app is able to answer with a server message
        # or load a full new set of client and server flows and replay flow by flow
       
        # Do it with flows 
        import common
        import cmdinterface
        
        
#        discoverer.formatinference.perform_format_inference_for_cluster_collection(testcluster, self.config)
        #testflow = testflows[testflows.keys()[element]]
        if not self.env.has_key('testflows'):
            self.do_load_testdata(args)
        
        if not self.env.has_key('testflows'):
            print "ERROR: Loading test data failed!"
            return
        
        testflows = self.env['testflows']
        # Test all flows
        failedelements = []
        success = 0
        failures = 0
        not_in_testflows = 0
        only_one_msg = 0
        has_gaps = 0
        not_alternating = 0
        not_all_transitioned = 0
        not_ended_in_final = 0
        test2go = len(testflows.keys())
        self.env['sm'].setConfig(self.config)
        self.env['sm'].setTestFlows(testflows)
        for elem in testflows.keys():
            print "{0} flows left to test".format(test2go)
            res = self.statemachine_accepts_flow(elem)
            test2go -= 1
            
            if res['testSuccessful']==True:
                success += 1
            else:
                failures += 1
                
                if not res['isInTestFlows']: not_in_testflows += 1
                elif not res['hasMoreThanOneMessage']: only_one_msg += 1
                elif not res['has_no_gaps']: has_gaps += 1
                elif not res['is_alternating']: not_alternating += 1
                elif not res['did_all_transitions' ]: 
                    not_all_transitioned += 1
                    failedelements.append(elem)
                elif not res['finished_in_final']: 
                    not_ended_in_final += 1
                    failedelements.append(elem)
        print "Finished"
        print "Testresults"
        print "==========="
        print "Number of flows: {0}, Success: {1}, Failures: {2}".format(success+failures, success, failures)
        if failures>0:
            print "Test flowID not in test flows: {0}".format(not_in_testflows)
            print "Flow had only one message: {0}".format(only_one_msg)
            print "Flow had gaps: {0}".format(has_gaps)
            print "Flow was not alternating: {0}".format(not_alternating)
            print "Flow rejected prematurely: {0}".format(not_all_transitioned)
            print "Flow did not end in final state: {0}".format(not_ended_in_final)
            print
            
            if len(failedelements)>0:
                print "Failed test flows (only tested flows):"
                for elem in failedelements:
                    print "{0}".format(elem)
        
    def do_statemachine_accepts_flow(self, flow):
        self.statemachine_accepts_flow(flow)
        
    def statemachine_accepts_flow(self, flow):
        if not self.env.has_key('testflows'):
            print "Test flows not loaded yet!"
            return dict({"testSuccessful": False, "isInTestFlows": False, "hasMoreThanOneMessage": False, "has_no_gaps": False, "is_alternating": False, "did_all_transitions": False, "finished_in_final": False})
        if not self.env['testflows'].has_key(flow):
            print "Flow {0} not in test flows!".format(flow)
            return dict({"testSuccessful": False, "isInTestFlows": False, "hasMoreThanOneMessage": False, "has_no_gaps": False, "is_alternating": False, "did_all_transitions": False, "finished_in_final": False})
               
        flowitems = self.env['testflows'][flow]
        return self.env['sm'].accepts_flow(flowitems,flow, printSteps=True)
    
    def do_dump_transitions(self,str):
        if self.env.has_key('sm'):
            self.env['sm'].dumpTransitions()
        else:
            print "No statemachine built, cannot dump transitions"
        
    def combineflows(self, cluster_collection):
        #if not self.env.has_key('messageFlows'):
        #    self.env['messageFlows'] = {}
        tmp_flows = {}
        for c in cluster_collection.get_all_cluster():
            for message in c.get_messages():
                if not tmp_flows.has_key(message.getConnectionIdentifier()):
                    tmp_flows[message.getConnectionIdentifier()] = {}
                subflow = tmp_flows[message.getConnectionIdentifier()]
                subflow[message.getFlowSequenceNumber()] = (message, message.getDirection())
                # subflow[message.getFlowSequenceNumber()] = (message, flowDirection)
        return tmp_flows
    
    def do_listflowIDs(self,str):
        self.listflowIDs()
        
    def listflowIDs(self):
        if not self.env.has_key('messageFlows'):
            print "ERROR: No message flows loaded yet"
            return
        
        messageFlows = self.env['messageFlows']
        
        print "Flow IDs in message flow collection"
        
        flowKeys = messageFlows.keys()
        for flowKey in flowKeys:
            print "\t{0}".format(flowKey) 
            
    def do_printflow(self, flowID):
        self.printflow(flowID)
        
    def printflow(self, flowID):
        if flowID=="":
            print "ERROR: Usage: printflow <flowID>"
            return
        
        if not self.env.has_key('messageFlows'):
            print "ERROR: No message flows loaded yet"
            return
        
        messageFlows = self.env['messageFlows']

        if not messageFlows.has_key(flowID):
            print "ERROR: Flow {0} not found in message flows. Please check flow ID".format(flowID)
            return
        
        messages = messageFlows[flowID]
        if len(messages)>0:
            print "Flow: {0} ({1} messages)".format(flowID, len(messages))
            firstitemnumber = sorted(messages.keys())[0]
            (msg, direction) = messages[firstitemnumber] # Retrieve first msg
            print "\t{0}".format(msg.get_message())
            nextMsg = msg.getNextInFlow()
            while nextMsg != None:
                print "\t{0}".format(nextMsg.get_message())                
                nextMsg = nextMsg.getNextInFlow()
        
    def linkmessages(self, messageFlows):
        print "Linking messages within flow"
        for flow in messageFlows:
            messages = messageFlows[flow]
            if len(messages)==1:
                if self.config.debug:
                    print "Flow {0} has only 1 message. Skipping flow".format(flow)
                continue
            #message_indices = messages.keys()
            from discoverer.peekable import peekable
            iterator = peekable(messages.items())
            #for msg_id, message in messages.items():
            lastMsg = None
            (msg_id, message) = iterator.next()
            message = message[0]
            while not iterator.isLast():
                if lastMsg != None:
                    lastMsg.setNextInFlow(message)
                    message.setPrevInFlow(lastMsg)
                lastMsg = message
                #else
                #    lastMsg = message
                (msg_id, message) = iterator.next()
                message = message[0]
            if lastMsg != message:
                lastMsg.setNextInFlow(message)
                message.setPrevInFlow(lastMsg)
            
            if self.config.debug:
                self.printflow(flow)
                 
    def do_dump_state(self, str):
        import cPickle
        handle = open("/Users/daubsi/Dropbox/disc_state","wb")
        sys.setrecursionlimit(50000)
        cPickle.dump(self.env, handle,2)
        handle.close()
        
    def do_load_state(self, str):
        import cPickle
        handle = open("/Users/daubsi/Dropbox/disc_state","rb")
        self.env = cPickle.load(handle)
        handle.close()
                    
    def go(self, sequences):
        
        import discoverer.statistics
        discoverer.statistics.reset_statistics()
        print "Performing discoverer algorithm"
        
        start = time.time()
        
        self.setup(sequences)
            
        elapsed = (time.time() - start)
        print "Setup took {:.3f} seconds".format(elapsed)
        #=======================================================================
        # if discoverer.statistics.get_classification() == "text" and self.config.breakSequences == True:
        #    print "Protocol is considered as 'text' and breakSequences is configured to 'true'. Reloading input..."
        #    import cmdinterface
        #    cmdinterface.cli.CommandLineInterface.do_read(breakSequences=True)
        #    del(self.env['cluster_collection'])
        #    
        #    self.do_setup(breakSequences=True)
        #=======================================================================
        
        self.env['messageFlows'] = self.combineflows(self.env['cluster_collection'])
        #self.combineflows(self.env['cluster_collection'])
        self.linkmessages(self.env['messageFlows'])
        start = time.time()
        self.do_format_inference("")
        elapsed = (time.time() - start)
        print "Format inference took {:.3f} seconds".format(elapsed)
        start = time.time()
        self.do_semantic_inference("")
        elapsed = (time.time() - start)
        print "Semantic inference took {:.3f} seconds".format(elapsed)
        start = time.time()
        self.do_recursive_clustering("")        
        elapsed = (time.time() - start)
        print "Recursive clustering took {:.3f} seconds".format(elapsed)
        start = time.time()
        
        self.do_fix_tokenization_errors("")
        elapsed = (time.time() - start)
        print "Fixing tokenization errors took {:.3f} seconds".format(elapsed)
        
        
        
        #self.print_clusterCollectionInfo()
        start = time.time()
        print "Merging..."
        self.env['cluster_collection'].mergeClustersWithSameFormat()
        #self.env['cluster_collection'].mergeClustersWithSameFormat(self.config)
        #self.env['cluster_collection'].mergeClustersWithSameFormat(self.config)
        #self.env['cluster_collection'].mergeClustersWithSameFormat(self.config)
        elapsed = (time.time() - start)
        print "Merging took {:.3f} seconds".format(elapsed)
        print "Finished"

        if self.config.debug:                
            self.env['cluster_collection'].print_clusterCollectionInfo()
            
        #=======================================================================
        # # Needlewunsch test
        # print "Now performing Needleman Wunsch alignment of two cluster representations"
        # import random
        # cluster1 = random.choice(cluster)
        # cluster2 = random.choice(cluster)
        # format1 = cluster1.get_formats()
        # format2 = cluster2.get_formats()
        # print "Current formats:"
        # print format1
        # print format2
        # print "Needlewunsch results:"
        # discoverer.needlewunsch.needlewunsch(format1, format2)
        #=======================================================================
               
    def do_dumpflow(self,file):
        if not self.config.loadClientAndServerParts:
            print "Flow dumping is only available when analyzing client and server flows"
            return
        if file!="":
            import os.path
            path = os.path.normpath(self.config.dumpFile)
            file = os.path.basename(self.config.inputFile)         
            (filename,ext) = os.path.splitext(file)
            storePath = "{0}{1}{2}_flow_dump.txt".format(path,os.sep,filename)
            import sys
            old_stdout = sys.stdout
            handle = open(storePath,"w")
            sys.stdout = handle
        print "Dump of 'Discoverer' flows"
        for f in self.env['messageFlows']:
            print "Flow: %s" % f
            for entry in self.env['messageFlows'][f]:
                print "\t{0}:\t{1} - {2}".format(entry,self.env['messageFlows'][f][entry][0].get_message(), self.env['messageFlows'][f][entry][0].getCluster().getFormatHash())
        if file!="":
            handle.close()         
            sys.stdout = old_stdout           
            print "Finished. File size %0.1f KB" % (os.path.getsize(storePath)/1024.0)
            
    def do_print_clusterinfo(self, string):
        if not self.env.has_key('cluster_collection'):
            print "No cluster loaded yet"
            return
        self.env['cluster_collection'].print_clusterCollectionInfo()
    def do_dumpresult(self, string):
        if self.config.loadClientAndServerParts == True:
            # Dump 2 collections to two files
            path = os.path.normpath(self.config.dumpFile)
            file = os.path.basename(self.config.inputFile)
            (filename,ext) = os.path.splitext(file)
            storePath = "{0}{1}{2}_formats_dump.txt".format(path,os.sep,filename)
            self.dump2File(self.env['cluster_collection'],storePath)
            #storePath = "{0}{1}{2}_formats.xml".format(path,os.sep,filename)
            #self.dumpXML(self.env['cluster_collection'], storePath)
            #storePath = "{0}{1}{2}_server_dump.txt".format(path,os.sep,filename)
            #self.dump2File(self.env['cluster_collection_server'],storePath)
        else:
            # Dump only one file (client traffic)
            path = os.path.normpath(self.config.dumpFile)
            file = os.path.basename(self.config.inputFile)
            (filename,ext) = os.path.splitext(file)
            storePath = "{0}{1}{2}_dump.txt".format(path,os.sep,filename)
            self.dump2File(self.env['cluster_collection'],storePath)
    
    def getCCXMLRepresentation(self):
        return self.env['cluster_collection'].getXMLRepresentation()        
    def dump2File(self, cluster_collection, storePath):
        print "Dumping result to file {0}".format(storePath)
        cluster_collection.print_clusterCollectionInfo(storePath)
        
    def do_discoverer(self, string):
        print "We are already in Discoverer mode!"
        
        
