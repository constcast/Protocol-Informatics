# vim: set sts=4 sw=4 cindent nowrap expandtab:

# CLI file for the "Discoverer" submodule

import cmd, sys, os
import discoverer
import cli
import discoverer.message
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
        
    def setup(self, sequences):        
        print "Performing initial message analysis and clustering"
        if sequences == None:        
            print "FATAL: No sequences loaded yet!"
            return False    
        
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
            
            if self.env.has_key('cluster_collection_client'):
                del(self.env['cluster_collection_client'])
            if self.env.has_key('cluster_collection_server'):
                del(self.env['cluster_collection_server'])
            
            # Perform discoverer for both parts
            print "-----------------Client2Server-----------------------"
            self.go(self.env['sequences_client2server'])
            self.env['cluster_collection_client'] = self.env['cluster_collection']
            self.env['message_flows'] = {}
            self.combineflows(self.env['cluster_collection_client'])
            if self.env.has_key('cluster_collection'):
                del(self.env['cluster_collection'])
            
            print "-----------------Server2client-----------------------"
            self.go(self.env['sequences_server2client'])
            self.env['cluster_collection_server'] = self.env['cluster_collection']
            self.combineflows(self.env['cluster_collection_server'])
            self.printflows() 
            
            # Build statemachine
            sm = discoverer.statemachine.Statemachine(self.env['messageFlows'])  
            sm.build()         
        else:
            # Perform discoverer only for client pat
            self.go(self.env['sequences'])
        
    def combineflows(self, cluster_collection):
        if not self.env.has_key('messageFlows'):
            self.env['messageFlows'] = {}
        for c in cluster_collection.get_all_cluster():
            for message in c.get_messages():
                if not self.env['messageFlows'].has_key(message.getConnectionIdentifier()):
                    self.env['messageFlows'][message.getConnectionIdentifier()] = {}
                subflow = self.env['messageFlows'][message.getConnectionIdentifier()]
                subflow[message.getFlowSequenceNumber()] = message
    def printflows(self):
        #print self.env['messageFlows']
        pass
    
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
                print "\t{0}:\t{1} - {2}".format(entry,self.env['messageFlows'][f][entry].get_message(), self.env['messageFlows'][f][entry].getCluster().getFormatHash())
        if file!="":
            handle.close()         
            sys.stdout = old_stdout           
            print "Finished. File size %0.1f KB" % (os.path.getsize(storePath)/1024.0)
                  
    def do_dumpresult(self, string):
        if self.config.loadClientAndServerParts == True:
            # Dump 2 collections to two files
            path = os.path.normpath(self.config.dumpFile)
            file = os.path.basename(self.config.inputFile)
            (filename,ext) = os.path.splitext(file)
            storePath = "{0}{1}{2}_client_dump.txt".format(path,os.sep,filename)
            self.dump2File(self.env['cluster_collection_client'],storePath)
            storePath = "{0}{1}{2}_server_dump.txt".format(path,os.sep,filename)
            self.dump2File(self.env['cluster_collection_server'],storePath)
        else:
            # Dump only one file (client traffic)
            path = os.path.normpath(self.config.dumpFile)
            file = os.path.basename(self.config.inputFile)
            (filename,ext) = os.path.splitext(file)
            storePath = "{0}{1}{2}_dump.txt".format(path,os.sep,filename)
            self.dump2File(self.env['cluster_collection'],storePath)
            
    def dump2File(self, cluster_collection, storePath):
        print "Dumping result to file {0}".format(storePath)
        cluster_collection.print_clusterCollectionInfo(storePath)
        
    def do_discoverer(self, string):
        print "We are already in Discoverer mode!"
        
        
