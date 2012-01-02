# vim: set sts=4 sw=4 cindent nowrap expandtab:

# CLI file for the "Discoverer" submodule

import cmd, sys, os
import discoverer
import cli

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
        discoverer.formatinference.perform_format_inference(self.env['cluster_collection'], self.config)
    
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
        
    def do_go(self, string):
        print "Performing discoverer algorithm"
        if self.env.has_key('cluster_collection'):
            del(self.env['cluster_collection'])
        self.do_setup("")
        self.do_format_inference("")
        self.do_semantic_inference("")
        self.do_recursive_clustering("")        
        
        print "Results:"
        cluster = self.env['cluster_collection'].get_all_cluster()        
     
        for c in cluster:         
            messages = c.get_messages()
            print "Cluster information: %s entries, %s format infered" % (len(messages), c.get_format_inference())
            for message in messages:
                print message
        
    def do_discoverer(self, string):
        print "We are already in Discoverer mode!"
        
        