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
        """
        Creates a distance matrix from the input sequences. Compares all sequences to each other 
        and puts the distance matrix into the environment
        """
        dmx = PI.distance.LocalAlignment(self.env['sequences'])
        self.env['dmx'] = dmx

    def do_PI(self, string):
        print "We are already in PI mode!"
        

    def do_phylogeny(self, string):
        """
        Create the phylogeny tree for the input data. Requires a distance matrix in the environment,
        which needs to be created by a call to do_distance first. 
        """
        if not 'dmx' in self.env:
            print "Error: No distance matrix created. Do this first ..."
            return
        
        print "Performing phylogeny tree creation with weight: %f %s" % (self.config.weight, str(type(self.config.weight)))
        phylo =  PI.phylogeny.UPGMA(self.env['sequences'], self.env['dmx'], self.config.weight)
        self.env['phylo'] = phylo
        print "\nDiscovered %d clusters using a weight of %.02f" % (len(phylo), self.config.weight)

    def do_graph(self, string):
        """
        Produce graphs on the phylogeny tree. Requires installed pydot library.
        """
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
        """
        Performs multi-sequence aligning on the elemnts in the previouly derived clusters.
        It is necessary to first run do_phylogeny to create a phylogeny tree that is used
        to guide the aligning task
        """

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
        """
        Shows the output of the sequencing alinging process. This can only be done
        after do_align has been called to create the list of alinged sequences.
        The output is modified by the "textBased" configuration variable. It it is
        set, the output will plainly print text sequences. If the value is set to false
        a binary output form will be chosen.

        The parameter specify whether gaps are supposed to be shown in hte consensus
        sequences, or if the sequences are shown in an ungapped form.
        """
        
        if not 'alist' in self.env:
            print "Error: No list of aligned sequences. Please create one first"
            return
        # check if we should produce gapped or ungapped output
        gapped = True
        if string == "gapped":
            gapped = True
        elif string == "ungapped":
            gapped = False

        #
        # Display each cluster of aligned sequences
        #
        i = 1
        all_cons = []
        for seqs in self.env['alist']:
            print "Output of cluster %d" % i
            if self.config.textBased == True:
                out = PI.output.TextBased(seqs)
                all_cons.append(out.cons, gapped)
            else:
                PI.output.Ansi(seqs, gapped)
            i += 1
            print ""
        
        print "Summarizing the consenus: "
        for cons in all_cons:
            print cons

    def do_go(self, string):
        """
        Run all the commands that are necessary to perforam the PI proto inference. 
        Will output the results eventually. Please note that all previously generated
        state (such as distance matrix) will be reset by this step.
        """
        print "Creating distance matrix ..."
        self.do_distance("")
        print "Creating phylogenetic tree ..."
        self.do_phylogeny("")
        if self.config.graph:
            print "Creating graphs ..."
            self.do_graph("")
        print "Performing multiple sequence aligning ..."
        self.do_align("")
        print "Preparing output!"
        self.do_output("")
