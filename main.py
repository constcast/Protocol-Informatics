#!/usr/bin/env python -u


#
# Protocol Informatics Prototype
# Written by Marshall Beddoe <mbeddoe@baselineresearch.net>
# Extended by Lothar Braun <braun@net.in.tum.de>
# Copyright (c) 2004 Baseline Research
#           (c) 2011 Lothar Braun
#
# Licensed under the LGPL
#

import PI
import entropy
import common

import sys, getopt, yaml

def main():
    configFile = None

    #
    # Parse command line options and do sanity checking on arguments
    #
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "c:")
    except:
        usage()

    for o,a in opts:
        if o in ["-c"]:
            configFile = a
        else:
            usage()

    if not configFile:
        # if we are started without a config file, we just drop into 
        # interactive mode ...
        command_line_interface(None)

    conf = common.config.Configuration(configFile)

    if conf.interactive:
        command_line_interface(conf)

    
    if conf.inputFile != None:
        file = conf.inputFile
    else:
        print "FATAL: You specified non-interactive mode, but didn't specify an inputFile. This is illegal ..."
        sys.exit(-1)

    #
    # Open file and get sequences
    #
    try:
        if conf.format == "pcap":
            sequences = common.input.Pcap(file, conf.maxMessages, conf.onlyUniq, conf.messageDelimiter, conf.fieldDelimiter).getConnections()
        elif conf.format == "ascii":
            sequences = common.input.ASCII(file, conf.maxMessages, conf.onlyUniq, conf.messageDelimiter, conf.fieldDelimiter).getConnections()
        elif conf.format == "bro":
            sequences = common.input.Bro(file, conf.maxMessages, conf.onlyUniq, conf.messageDelimiter, conf.fieldDelimiter).getConnections()
        else:
            print "FATAL: Unknown file format"
            sys.exit(-1)
    except Exception as inst:
        print ("FATAL: Error reading input file '%s':\n %s" % (file, inst))
        sys.exit(-1)

    if conf.analysis == "entropy":
        entropy.entropy.entropy_core(sequences, conf.gnuplotFile)
    elif conf.analysis == "PI":
        PI.core.pi_core(sequences, conf.weight, conf.graph, textBased)
    elif conf.analysis == "reverx":
        pass
    else:
        print "FATAL: Unknown analysis module %s configured" % (analysis)
        sys.exit(-1)

def usage():
    print "usage: %s [ -c <config> ]" % \
        sys.argv[0]
    print "       -c\tconfig file in yaml format (optional)"
    sys.exit(-1)

def command_line_interface(config):
    print "Welcome to Protocol-Informatics. What do you want to do today?"
    import cmdinterface
    cmdline = cmdinterface.cli.CommandLineInterface()
    cmdline.cmdloop()

if __name__ == "__main__":
    main()

# vim: set sts=4 sw=4 cindent nowrap expandtab:

