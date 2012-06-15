# vim: set sts=4 sw=4 cindent nowrap expandtab:

import cmd, sys, os
import cli

import common

def perform_merge(conns):
        ret = dict()
        single_conn = common.sequences.FlowInfo("single")
        for i in conns:
            for seq in conns[i].sequences:
                single_conn.addSequence(seq)
                
        ret["single"] = single_conn
        return ret

def perform_unique(conns):
    for i in conns:
        conns[i].uniqSequences()
    return conns

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
        self.env['sequences'] = perform_merge(self.env['sequences'])

    def do_uniq(self, string):
        """
        Uniqs the elements in the sequences enviornment. Duplicate messages within the connections
        are removed. This operation is done on per connection base: If two equal sequences are 
        distributed over multiple connections, they will be still there after the uniquing.
        Use do_merge() in order to put all sequences into a single connection context if you want to 
        globally remove duplicates
        """
        self.env['sequences'] = perform_unique(selv.env['sequences'])

            
    def do_split(self, string):
        """
        Splits the current messages at the pieces specified by <string> or in the 
        messagaeDelimiter configuration variable if string is empty
        """
        if string == "":
            splitseq = self.config.messageDelimiter
        else:
            splitseq = string
            
        print "Trying to split messages according to delimiter: \"%s\"" % (splitseq)
        seqs = self.env['sequences']
        for i in seqs:
            seqs[i].splitSequences(splitseq)
        print "Sucess!"


    def do_save(self, string):
        """
        Saves the current sequences to a file <string> or a default file 
        "working.pickle"
        """
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
        """
        Loads stored sequences from a file created by do_save()
        """
        if string == "":
            filename = "working.pickle"
        else:
            filename = string

        import cPickle
        print "Loading from file \"%s\" ..." % (filename)
        fd = file(filename, 'r')
        self.env['sequences'] = cPickle.load(fd)
        print "Success!"
        
    def do_count(self, string):
        """
        Counts the number of elements in the sequences.
        """
        conns = self.env['sequences']
        counter = 0
        for i in conns:
            counter += len(conns[i].sequences)
        print "Got %d messages in our data set" % (counter)

    def do_randsample(self, string):
        """
        Picks a random subsample from the sequences. The code tries to pick the specified
        number <string>  from each connections, if the connection has more than <string>
        elements. It will do nothing otherwise.
        """
        randompicks = 0
        if string == "":
            print "ERROR: You need to supply a number of strings to pick"
            return
        else:
            try:
                randompicks = int(string)
            except:
                print "ERROR: Could not convert number of elements to number!"
                return
        
        conns = self.env['sequences']
        for i in conns:
            conns[i].randomSample(randompicks)
            
        
    def help_count(self, string):
        print "Command syntax: count"
        print ""
        print "Counts the number of sequences in the current environment"
    
    def help_load(self, string):
        print "Command synatx: load [ <filename> ]"
        print ""
        print "Loads a previously saved sequence file which has been created with"
        print "the save command. If <filename> is specified, the given filename "
        print "is used to load the sequences. Otherwise the default filename "
        print "working.pickle is used."
    
    def help_save(self, string):
        print "Command syntax: save [ <filename> ]"
        print ""
        print "Saves the current sequences stored in the enviornment to a file."
        print "If <filename> is non-empty, it is used as a target file. Otherwise"
        print "the default filename \"working.pickle\" is used."

    def help_split(self, string):
        print "Command syntax: split [ <delimiter> ]"
        print ""
        print "Splits the sequences according to a message delimiter. If delimiter"
        print "is non-empty, the command argument will be used. Othterwise the "
        print "configuration variable messageDelimiter will be used."

    def help_randsample(self, string):
        print "Command syntax: randsample <number>"
        print ""
        print "Picks a random subsample of count <number> from each connection context."
        print "If <number> is bigger than the actual number of sequenes in a connection,"
        print "nothing will happen."
