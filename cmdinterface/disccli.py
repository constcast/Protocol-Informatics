# vim: set sts=4 sw=4 cindent nowrap expandtab:

# CLI file for the "Discoverer" submodule

import cmd, sys, os
import discoverer
import cli
import discoverer.message
import time
import collections

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
        
    def do_setup(self, string):        
        print "Performing initial message analysis and clustering"
        if not self.env.has_key('sequences'):
            print "FATAL: No sequences loaded yet!"
            return False    
        
        setup = discoverer.setup.Setup(self.env['sequences'], self.config)
        self.env['cluster_collection'] = setup.get_cluster_collection()
        print "Built ", setup.get_cluster_collection().num_of_clusters(), " clusters"
      
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
        discoverer.recursiveclustering.perform_recursive_clustering(self.env['cluster_collection'], 0, self.config)
    
    def help_go(self):
        print "Automatically executes all steps needed to perfom the 'Discoverer' algorithm on the set of messages"
            
    def do_go(self, string):
        print "Performing discoverer algorithm"
        if self.env.has_key('cluster_collection'):
            del(self.env['cluster_collection'])
        start = time.time()
        self.do_setup("")
        elapsed = (time.time() - start)
        print "Setup took ", elapsed, " seconds "
        start = time.time()
        self.do_format_inference("")
        elapsed = (time.time() - start)
        print "Format inference took ", elapsed, " seconds "
        start = time.time()
        self.do_semantic_inference("")
        elapsed = (time.time() - start)
        print "Semantic inference took ", elapsed, " seconds "
        start = time.time()
        self.do_recursive_clustering("")        
        elapsed = (time.time() - start)
        print "Recursive clustering took ", elapsed, " seconds "
        print "Results:"
        
        self.print_clusterCollectionInfo()
        print "Merging..."
        self.env['cluster_collection'].mergeClustersWithSameFormat(self.config)
        print "Merged"
        self.print_clusterCollectionInfo()
            
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
    def print_clusterCollectionInfo(self):
        cluster = self.env['cluster_collection'].get_all_cluster()             
        self.print_clusterInfo(cluster)
        
    def print_clusterInfo(self, cluster):
        for c in cluster:         
            messages =  c.get_messages()  
            formats = c.get_formats()
            print "****************************************************************************"          
            print "Cluster information: %s entries" % len(messages)
            print "Format inferred: %s" % formats
            # print "Token format: %s" % c.get_representation()            
            #for message in messages:
            #    print message
            idx = 0
            for format in formats:
                print "Token {0}:".format(idx) ,
                if "FD" in format[2]:
                    rawValues = c.get_all_values_for_token(idx)
                        sumUp = collections.Counter(rawValues)
                        values = ""
                        for key in sumUp.keys():
                            #if sumUp.get(key)>1:
                            newstr = "{0} ({1}), ".format(key, sumUp.get(key))
                            values += newstr
                    #values = c.get_values_for_token(idx)
                    print "FD, {0} values: {1}".format(len(values), ",".join(values))
                else:
                    if format[1] == "const":
                        value = messages[0].get_tokenAt(idx).get_token()
                        print "const {0} token, value {1}".format(format[0],value) 
                    else: # variable
                        rawValues = c.get_all_values_for_token(idx)
                        sumUp = collections.Counter(rawValues)
                        values = ""
                        for key in sumUp.keys():
                            #if sumUp.get(key)>1:
                            newstr = "{0} ({1}), ".format(key, sumUp.get(key))
                            values += newstr
                        print "variable {0} token, values {1}".format(format[0],values)
                idx += 1
                
                    
            
        
        
    def do_discoverer(self, string):
        print "We are already in Discoverer mode!"
        
        
