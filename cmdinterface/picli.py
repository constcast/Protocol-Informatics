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
        
        phylo =  PI.phylogeny.UPGMA(self.env['sequences'], self.env['dmx'], self.config.weight)
        self.env['phylo'] = phylo
        print "\nDiscovered %d clusters using a weight of %.02f" % (len(phylo), self.config.weight)

    def do_graph(self, string):
        if not 'phylo' in self.env:
            print "Error: No phylogentic tree to graph."
            return
        #
        # Output some pretty graphs of each cluster
        #
        cnum = 1
        for cluster in self.env['phylo']:
            out = "graph-%d" % cnum
            print "Creating %s .." % out,
            cluster.graph(out)
            print "complete"
            cnum += 1

    def do_align(self, string):
        if not 'phylo' in self.env:
            print "Error:No phylogentic tree. Please create one first!"
            return

        i = 1
        alist = []
        for cluster in self.env['phylo']:
            print "Performing multiple alignment on cluster %d .." % i,
            aligned = PI.multialign.NeedlemanWunsch(cluster)
            print "complete"
            alist.append(aligned)
            i += 1
        print ""
        self.env['alist'] = alist
        

    def do_output(self, string):
        if not 'alist' in self.env:
            print "Error: No list of aligned sequences. Please create one first"
            return
        #
        # Display each cluster of aligned sequences
        #
        i = 1
        for seqs in self.env['alist']:
            print "Output of cluster %d" % i
            if self.config.textBased == True:
                PI.output.TextBased(seqs)
            else:
                PI.output.Ansi(seqs)
            i += 1
            print ""

    def do_go(self, string):
        print "Creating distance matrix ..."
        self.do_distance("")
        print "Creating phylogenetic tree ..."
        self.do_phylogeny("")
        print "Creating graphs ..."
        self.do_graph("")
        print "Performing multiple sequence aligning ..."
        self.do_align("")
        print "Preparing output!"
        self.do_output("")
