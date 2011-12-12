# vim: set sts=4 sw=4 cindent nowrap expandtab:

import cmd, sys, os
import PI
import cli

class PICommandLineInterface(cli.CommandLineInterface):
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

    def do_distance(self, string):
        dmx = PI.distance.LocalAlignment(self.env['sequences'])
        self.env['dmx'] = dmx

    def do_PI(self, string):
        print "We are already in PI mode!"


    def do_phylogeny(self, string):
        if not 'dmx' in self.env:
            print "Error: No distance matrix created. Do this first ..."
            return
        
        phylo =  PI.phylogeny.UPGMA(self.env['sequences'], self.env['dmx'], self.configuration.weight)
        self.env['phylo'] = phylo
    


