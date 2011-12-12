
"""
Input module

Handle different input file types and digitize sequences

Written by Marshall Beddoe <mbeddoe@baselineresearch.net>
Copyright (c) 2004 Baseline Research

Licensed under the LGPL
"""

from pcapy  import *
from socket import *
import re
import sequences

__all__ = ["Input", "Pcap", "ASCII", "Bro"]

class Input:

    """Implementation of base input class"""

    def __init__(self, filename, maxMessages, onlyUniq):
        """Import specified filename"""

        self.set = set()
        self.index = 0
        self.maxMessages = maxMessages
        self.readMessages = 0
        self.onlyUniq = onlyUniq

    def getConnections(self):
        raise Exception("getConnections not implemented ...")

class Pcap(Input):

    """Handle the pcap file format"""

    def __init__(self, filename, maxMessages, onlyUniq, offset=14):
        Input.__init__(self, filename, maxMessages, onlyUniq)
        self.pktNumber = 0
        self.offset = offset

        # we do not perform reassembling or connection tracking
        # therefore we store all messages in a single flow-instance
        # without message numbers (this is the original PI behavior)
        self.connection = sequences.FlowInfo()

        pd = open_offline(filename)

        try:
            # we might escape this handler by raising an exception if maxmessages are read
            # we also 
            pd.dispatch(-1, self.handler)
        except Exception as inst:
            print "Finished reading packets from PCAP with reason: %s" % (inst)

    def handler(self, hdr, pkt):
        if hdr.getlen() <= 0:
            return

        # only store as much as self.maxMessages messages
        # we cannot restrict the calls to handler to 50 packets since
        # we only consider UNIQ payloads as messages. we therefore
        # need to count 50 messages in this handler
        if self.maxMessages != 0 and self.readMessages >= self.maxMessages:
            raise Exception("Extracted %d messages from PCAP file. Stopped reading file as configured" % (self.maxMessages))

        # Increment packet counter
        self.pktNumber += 1

        # Ethernet is a safe assumption
        offset = self.offset

        # Parse IP header
        iphdr = pkt[offset:]

        ip_hl = ord(iphdr[0]) & 0x0f                    # header length
        ip_len = (ord(iphdr[2]) << 8) | ord(iphdr[3])   # total length
        ip_p = ord(iphdr[9])                            # protocol type
        ip_srcip = inet_ntoa(iphdr[12:16])              # source ip address
        ip_dstip = inet_ntoa(iphdr[16:20])              # dest ip address

        offset += (ip_hl * 4)

        # Parse TCP if applicable
        if ip_p == 6:
            tcphdr = pkt[offset:]

            th_sport = (ord(tcphdr[0]) << 8) | ord(tcphdr[1])   # source port
            th_dport = (ord(tcphdr[2]) << 8) | ord(tcphdr[3])   # dest port
            th_off = ord(tcphdr[12]) >> 4                       # tcp offset

            offset += (th_off * 4)

        # Parse UDP if applicable
        elif ip_p == 17:
            offset += 8

        # Parse out application layer
        seq_len = (ip_len - offset) + 14

        if seq_len <= 0:
            return

        seq = pkt[offset:]

        l = len(self.set)
        self.set.add(seq)

        if len(self.set) == l and self.onlyUniq:
            return

        self.readMessages += 1

        self.connection.addSequence(sequences.Sequence(seq), self.readMessages)

    def getConnections(self):
        return [ self.connection ]

class ASCII(Input):

    """Handle newline delimited ASCII input files"""

    def __init__(self, filename, maxMessages, onlyUniq):
        Input.__init__(self, filename, maxMessages, onlyUniq)

        # we do not perform reassembling or connection tracking
        # therefore we store all messages in a single flow-instance
        # without message numbers (this is the original PI behavior)
        self.connection = sequences.FlowInfo()

        fd = open(filename, "r")

        lineno = 0

        while 1:
            lineno += 1
            line = fd.readline()

            if not line:
                break

            if self.maxMessages != 0 and self.readMessages > self.maxMessages:
                # we already have enough messages. stop reading
                break

            l = len(self.set)
            self.set.add(line)

            if len(self.set) == l and self.onlyUniq:
                continue
            
            self.readMessages += 1

            self.connection.addSequence(sequences.Sequence(line, self.readMessages))

    def getConnections(self):
        return [ self.connection ]


class Bro(Input):
    """ Handle output files from Bro-IDS with bro-scripts/adu_writer.bro running.
         The file format is texted-based and error prone (and someone should fix this).
         The format for each message is
         BLOCKSEPARATOR ConnectionID MessageNumber Content-Length Message
         where 
         BLOCKSEPARTOR == ******************************************
         ConnectionID  == alphnumeric unique connection identifier 
         MessageNumber == the message number of the message within the connection
         Content-Length == the length of the message 
         message == the message itself which has a length of Content-Length
    """

    def consumeMessageBlock(self, data, connectionID, messageNumber, contentLength):
    	if len (data ) == 0:
		return 

        if len(data) != contentLength:
            raise Exception("Error while parsing input file. Message:\n\n%s\n\nReal length %d does not match ContentLength %s" % (data, len(data), contentLength))

	# try to split the reassembled message into parts if a message delimiter is known
	if self.messageDelimiter:
		messageParts = data.split(self.messageDelimiter)
	else:
		messageParts = data

	for seq in messageParts:
		if len(seq) == 0:
			continue

	        # only insert uniq messages into the list of seuqences. avoid duplicate
	        l = len(self.set)
	        self.set.add(seq)
	        if len(self.set) == l and self.onlyUniq:
       		     continue

                self.readMessages += 1

                if not connectionID in self.connections:
                    self.connections[connectionID] = sequences.FlowInfo(connectionID)
                    
                self.connections[connectionID].addSequence(sequences.Sequence(seq, messageNumber))

    def getConnections(self):
        return self.connections


    def __init__(self, filename, maxMessages, onlyUniq, messageDelimiter, fieldDelimiter):
    	self.messageDelimiter = messageDelimiter
	self.fieldDelimiter = fieldDelimiter
        self.connections = dict()
        Input.__init__(self, filename, maxMessages, onlyUniq)

        self.blockseparator = "******************************************"

        sequence = ""
        connectionID = ""
        messageNumber = 0
        contentLength = 0
        content = ""

        fd = open(filename, "r")
        for line in fd:
            if self.maxMessages != 0 and self.readMessages > self.maxMessages:
                # already consumed maxMessages. stop reading more messages
                return

            if line.startswith(self.blockseparator):
                # found a new block. push the old one
                self.consumeMessageBlock(content, connectionID, messageNumber, contentLength)

                # parse next block header
                regexstring = '\*+ (\w+) ([0-9]+) ([0-9]+) (.*)'
                m = re.match(regexstring, line)
                if m: 
                    connectionID = m.group(1)
                    messageNumber = int(m.group(2))
                    contentLength = int(m.group(3))
                    content = m.group(4)
                else:
                    errorstring =  "Format missmatch in file. Expected a new message, got: " + line
                    raise Exception(errorstring)
            else:
                content.append(line)

        # try to assign last message block to last message
        self.consumeMessageBlock(content, connectionID, messageNumber, contentLength)
