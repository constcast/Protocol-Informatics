# vim: set sts=4 sw=4 cindent nowrap expandtab:

import cmd, sys, os
import cli

import common

class SequencesCommandLineInterface(cli.CommandLineInterface):
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
    
    def do_merge(self, string):
        """ The sequences in env are typically distributed over multiple connections. Algorihtms
            like PI do not distinguish between multiple connections. This function merges them
            into a single one
        """
        conns = self.env['sequences']
        ret = dict()
        single_conn = common.sequences.FlowInfo("single")
        for i in conns:
            for seq in conns[i].sequences:
                single_conn.addSequence(seq)
                
        ret["single"] = single_conn

        self.env['sequences'] = ret

    def do_uniq(self, string):
        """
        Uniqs the elements in the sequences enviornment. Duplicate messages within the connections
        are removed. This operation is done on per connection base: If two equal sequences are 
        distributed over multiple connections, they will be still there after the uniquing.
        Use do_merge() in order to put all sequences into a single connection context if you want to 
        globally remove duplicates
        """
        conns = self.env['sequences']
        for i in conns:
            conns[i].uniqSequences()

            
    def do_split(self, string):
        if string == "":
            splitseq = self.config.messageDelimiter
        else:
            splitseq = string
            
        print "Trying to split messages according to delimiter: \"%s\"" % (splitseq)

    def do_save(self, string):
        if string == "":
            filename = "working.pickle"
        else:
            filename = string

        print "Saving to file \"%s\" ..." % (filename)
        import cPickle
        fd = file(filename, 'w')
        cPickle.dump(self.env['sequences'], fd)
        print "Success!"

    def do_load(self, string):
        if string == "":
            filename = "working.pickle"
        else:
            filename = string

        import cPickle
        print "Loading from file \"%s\" ..." % (filename)
        fd = file(filename, 'r')
        self.env['sequences'] = cPickle.load(fd)
        print "Success!"
        
