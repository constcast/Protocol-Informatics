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

import sys, getopt, yaml, os

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
        # if we are started without a config file, we check for an existing file
        # named config.yml in the current directory and try load it if available
        if os.access("config.yml", os.R_OK):
            print "Found default configuration file \"config.yml\". Trying to load the file ..."
            conf = common.config.loadConfig("config.yml")
            command_line_interface(conf)
        else:
            # ok, we didn't find a default config. We are now trying to create one
            # from the default configuration
            print "No default configuration found. Createing a default config file \"config.yml\"."
            command_line_interface(None, True)

        # this function should never return, but we make sure by exiting here
        return

    conf = common.config.loadConfig(configFile)

    if conf.interactive:
        command_line_interface(conf)
        return

    
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
    print "       -c\tconfig file in yaml format (optional)."
    print ""
    print "If no config file is specified, the default configuration is read from config.yml in the current directory."
    print "If no config.yml is available in the current directory, a new config.yml with default values is created."
    sys.exit(-1)

def command_line_interface(config, savedefault = False):
    import cmdinterface
    cmdline = cmdinterface.cli.CommandLineInterface(config)
    if savedefault:
        cmdline.config.configFile = "config.yml"
        cmdline.do_saveconfig("")
    print ""
    print "Welcome to Protocol-Informatics. What do you want to do today?"
    print ""
    cmdline.cmdloop()


if __name__ == "__main__":
    main()

# vim: set sts=4 sw=4 cindent nowrap expandtab:

