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

import sys, getopt, yaml

def main():

     # Defaults
    format = "pcap"
    weight = 1.0
    graph = False
    maxMessages = 0
    textBased = False
    entropyBased = False
    configFile = None
    config = None

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
        weigth = config['weight']

    if not 'format' in  config:
        print "FATAL: No input format configured!"
        sys.exit(-1)
    else:
        format = config['format']

    if 'maxMessages' in config:
        maxMessages = int(config['maxMessages'])

    if 'graph' in config:
        graph = config['graph']

    if 'textBased' in config:
        textBased = config['textBased']

    if 'entropyBased' in config:
        entropyBased = config['entropyBased']

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
            sequences = PI.input.Pcap(file)
        elif format == "ascii":
            sequences = PI.input.ASCII(file)
        elif format == "bro":
            sequences = PI.input.Bro(file)
        else:
            print "FATAL: Specify file format"
            sys.exit(-1)
    except Exception as inst:
        print ("FATAL: Error reading input file '%s':\n %s" % (file, inst))
        sys.exit(-1)

    if len(sequences) == 0:
        print "FATAL: No sequences found in '%s'" % file
        sys.exit(-1)
    else:
        print "Found %d unique sequences in '%s'" % (len(sequences), file)
    if maxMessages != 0 and len(sequences) > maxMessages:
        print "Only considering the first %d messages for PI" % (maxMessages)
        sequences = sequences[0:maxMessages]
        print "Number of messages: %d" % (len(sequences))

    if entropyBased:
        entropy.entropy.entropy_core(sequences)
    else:
        PI.core.pi_core(sequences, weight, graph, textBased)

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
        

if __name__ == "__main__":
    main()

# vim: set sts=4 sw=4 cindent nowrap expandtab:

