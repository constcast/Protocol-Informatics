#!/usr/bin/env python -u


#
# Protocol Informatics Prototype
# Written by Marshall Beddoe <mbeddoe@baselineresearch.net>
# Copyright (c) 2004 Baseline Research
#
# Licensed under the LGPL
#

from PI import *
import sys, getopt

def main():

    print "Protocol Informatics Prototype (v0.01 beta)"
    print "Written by Marshall Beddoe <mbeddoe@baselineresearch.net>"
    print "Copyright (c) 2004 Baseline Research\n"

    # Defaults
    format = "pcap"
    weight = 1.0
    graph = False
    maxMessages = 0
    textBased = False
    entropyBased = False

    #
    # Parse command line options and do sanity checking on arguments
    #
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "pabgtw:m:")
    except:
        usage()

    for o,a in opts:
        if o in ["-p"]:
            format = "pcap"
        elif o in ["-a"]:
            format = "ascii"
        elif o in ["-b"]:
            format = "bro"
        elif o in ["-w"]:
            weight = float(a)
        elif o in ["-g"]:
            graph = True
        elif o in ["-m"]:
            maxMessages = int(a)
        elif o in ["-t"]:
            textBased = True
        elif o in ["-e"]:
            entropyBased = True
        else:
            usage()

    if len(args) == 0:
        usage()

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
            sequences = input.Pcap(file)
        elif format == "ascii":
            sequences = input.ASCII(file)
        elif format == "bro":
            sequences = input.Bro(file)
        else:
            print "FATAL: Specify file format"
            sys.exit(-1)
    except Exception as inst:
        print ("FATAL: Error reading input file '%s':\n %s" % (file, inst))
        sys.exit(-1)

    #for i in range(len(sequences)):
    #print sequences.set
    #print sequences

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
        entropy_core(sequences)
    else:
        core.pi_core(sequences, weight, graph, textBased)

def usage():
    print "usage: %s [-gtpab] [-m <messages>]  [-w <weight>] <sequence file>" % \
        sys.argv[0]
    print "       -g\toutput graphviz of phylogenetic trees"
    print "       -p\tpcap format"
    print "       -a\tascii format"
    print "       -b\tBro adu output format"
    print "       -w\tdifference weight for clustering"
    print "       -m\tmaximum number of messages to use for PI"
    print "       -t\texpected a text-based protocol"
    sys.exit(-1)

def entropy_core(sequences):
    pass

if __name__ == "__main__":
    main()

# vim: set sts=4 sw=4 cindent nowrap expandtab:

