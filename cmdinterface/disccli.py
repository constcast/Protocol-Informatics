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
        
    def do_go(self, string):
        print "The magic happens here ..."

        if not self.env.has_key('sequences'):
            print "FATAL: No sequences loaded yet!"
            return False    
        
        discoverer.setup.setup(self.env['sequences'], self.config)
       
        
    def do_discoverer(self, string):
        print "We are already in Discoverer mode!"
        
        