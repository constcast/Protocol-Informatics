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
    # go into command line mode if no arguments are given
    if len(sys.argv) == 1:
        command_line_interface()
        sys.exit(0)

     # Defaults
    format = "pcap"
    weight = 1.0
    graph = False
    maxMessages = 0
    messageDelimiter = None
    fieldDelimiter = None
    textBased = False
    configFile = None
    analysis = None
    config = None
    gnuplotFile = None
    onlyUniq = False

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

    if len(args) == 0:
        usage()

    if not configFile:
        print "FATAL: No config file given. Don't know how to proceed!"
        
    config = parseConfig(configFile)

    # extract necessary config parameters from config file
    if not 'weight' in  config:
        print "FATAL: No weight configured!"
        sys.exit(-1)
    else:
        weight = config['weight']

    if 'onlyUniqMessages' in config:
        onlyUniq = config['onlyUniqMessages']

    if not 'format' in  config:
        print "FATAL: No input format configured!"
        sys.exit(-1)
    else:
        format = config['format']
        
    if 'maxMessages' in config:
        maxMessages = int(config['maxMessages'])

    if not 'analysis' in config:
        print "FATAL: analysis module not configured!"
    else:
        analysis = config['analysis']

    if 'graph' in config:
        graph = config['graph']

    if 'textBased' in config:
        textBased = config['textBased']

    if 'messageDelimiter' in config:
        messageDelimiter = config['messageDelimiter']

    if 'fieldDelimiter' in config:
        fieldDelimiter = config['fieldDelimiter']

    if 'entropyGnuplotFile' in config:
        gnuplotFile = config['entropyGnuplotFile']

    if weight < 0.0 or weight > 1.0:
        print "FATAL: Weight must be between 0 and 1"
        sys.exit(-1)

    file = sys.argv[len(sys.argv) - 1]

    try:
        file
    except:
        usage()

    #
    # Open file and get sequences
    #
    try:
        if format == "pcap":
            sequences = common.input.Pcap(file, maxMessages, onlyUniq).getConnections()
        elif format == "ascii":
            sequences = common.input.ASCII(file, maxMessages, onlyUniq).getConnections()
        elif format == "bro":
            sequences = common.input.Bro(file, maxMessages, onlyUniq, messageDelimiter, fieldDelimiter).getConnections()
        else:
            print "FATAL: Specify file format"
            sys.exit(-1)
    except Exception as inst:
        print ("FATAL: Error reading input file '%s':\n %s" % (file, inst))
        sys.exit(-1)

    if analysis == "entropy":
        entropy.entropy.entropy_core(sequences, gnuplotFile)
    elif analysis == "PI":
        PI.core.pi_core(sequences, weight, graph, textBased)
    elif analysis == "reverx":
        pass
    else:
        print "FATAL: Unknown analysis module %s configured" % (analysis)
        sys.exit(-1)

def usage():
    print "usage: %s  -c <config> <sequence file>" % \
        sys.argv[0]
    print "       -c\tconfig file in yaml format"
    sys.exit(-1)

def parseConfig(f):
    try:
        cf = file(f, 'r')
        config = yaml.load(cf)
        return config
    except Exception as e:
        print "Could not parse config file \"%s\": %s" % (f, e)
        sys.exit(-1)

def command_line_interface():
    cmdline = common.cli.CommandLineInterface()
    cmdline.cmdloop()

if __name__ == "__main__":
    main()

# vim: set sts=4 sw=4 cindent nowrap expandtab:

