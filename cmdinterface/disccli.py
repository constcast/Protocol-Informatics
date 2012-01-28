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
        discoverer.recursiveclustering.perform_recursive_clustering(self.env['cluster_collection'], 0, self.config)
    
    def do_fix_tokenization_errors(self, string):
        print "Trying to fix tokenization errors"
        if not self.env.has_key('cluster_collection'):
            print "FATAL: Initial clustering not yet performed. Run 'setup' first pleaset!"
            return False    
        self.env['cluster_collection'].fix_tokenization_errors(self.env['cluster_collection'], self.config)
    
    def help_go(self):
        print "Automatically executes all steps needed to perfom the 'Discoverer' algorithm on the set of messages"
            
    def do_go(self, string):
        print "Performing discoverer algorithm"
        if self.env.has_key('cluster_collection'):
            del(self.env['cluster_collection'])
        start = time.time()
        self.do_setup("")
        elapsed = (time.time() - start)
        print "Setup took {:.3f} seconds".format(elapsed)
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
        self.do_fix_tokenization_errors("")
        # Next 2 must be called to fix entries
        self.do_format_inference("")
        self.do_semantic_inference("")
        
        #self.print_clusterCollectionInfo()
        print "Merging..."
        self.env['cluster_collection'].mergeClustersWithSameFormat(self.config)
        #self.env['cluster_collection'].mergeClustersWithSameFormat(self.config)
        #self.env['cluster_collection'].mergeClustersWithSameFormat(self.config)
        #self.env['cluster_collection'].mergeClustersWithSameFormat(self.config)
        
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
            print "Cluster information: {0} entries".format(len(messages))
            print "Format inferred: {0}".format(formats)
            # print "Token format: {0}".format(c.get_representation())s            
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
                        newstr = "'{0}' ({1}), ".format(key, sumUp.get(key))
                        values += newstr
                    print "FD, {0} values: {1}".format(len(sumUp), values[:-2])
                elif "lengthfield" in format[2]:
                    rawValues = c.get_all_values_for_token(idx)
                    sumUp = collections.Counter(rawValues)
                    values = ""
                    for key in sumUp.keys():
                        #if sumUp.get(key)>1:
                        newstr = "'{0}' ({1}), ".format(key, sumUp.get(key))
                        values += newstr
                    print "Length field, {0} values: {1}".format(len(sumUp), values[:-2])
                else:
                    if format[1] == "const":
                        value = messages[0].get_tokenAt(idx).get_token()
                        if format[0]=='binary':
                            print "const binary token, value 0x{:02x}".format(value),
                            if not format[2]==[]:
                                print "({})".format(",".join(format[2]))
                            else:
                                print ""
                        else:
                            print "const {} token, value '{}'".format(format[0],value)  
                    else: # variable
                        rawValues = c.get_all_values_for_token(idx)
                        sumUp = collections.Counter(rawValues)
                        values = ""
                        keys = sumUp.keys()
                        for i in range(0,min(5,len(keys))):
                            key = keys[i]
                            if format[0]=='binary':
                                newstr = "0x{:02x} ({}), ".format(key, sumUp.get(key))
                            else:
                                newstr = "'{0}' ({1}), ".format(key, sumUp.get(key))
                                
                            values += newstr
                        if len(values)>0:
                            values += "..."
                        if format[0]=='binary':
                            print "variable binary token, values {}".format(values),
                            if not format[2]==[]:
                                print "({})".format(",".join(format[2]))
                            else:
                                print ""
                        else:
                            print "variable text token, values: {0}".format(values)
                        
                idx += 1
                
                    
            
        
        
    def do_discoverer(self, string):
        print "We are already in Discoverer mode!"
        
        
