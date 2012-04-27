'''
Created on 05.04.2012

@author: daubsi
'''

import re

# To be used standalone to split input files accordingly

def has_gaps(numbers, gap_size):
        # Based on http://stackoverflow.com/questions/4375310/finding-data-gaps-with-bit-masking
        adjacent_differences = [(y - x) for (x, y) in zip(numbers[:-1], numbers[1:])]
        for elem in adjacent_differences:
            if elem>1:
                return True
        return False

def is_alternating(messages):
    direction = ""
    msg_keys = sorted(messages.keys())
    for msg_key in msg_keys:
        direction2 = messages[msg_key][3]
        if direction==direction2: # Current message has same direction as message before
            return False
        direction = direction2
    return True
    
class Splitter(object):
    '''
    classdocs
    '''

    def __init__(self, infilename):
        '''
        Constructor
        '''
        self.infilename = infilename
        
    def split(self, chunksize):
        fdinclient = open("/Users/daubsi/Dropbox/ftp_big_client", "r")
        fdinserver = open("/Users/daubsi/Dropbox/ftp_big_server", "r")
        
        flowcontainer = dict()
        
        for inline in fdinclient:
            regexstring = '\*+ (\w+) ([0-9]+) ([0-9]+) ([0-9]+) (.*)'
            m = re.match(regexstring, inline)
            connectionID = m.group(1)
            messageNumber = int(m.group(2))
            flowMessageNumber = int(m.group(3))
            contentLength = int(m.group(4))
            content = m.group(5)
        
            msg = tuple([flowMessageNumber, contentLength, content, "client2server"])
            if not flowcontainer.has_key(connectionID):
                flowcontainer[connectionID] = dict()
            msgcontainer = flowcontainer[connectionID]
            msgcontainer[flowMessageNumber] = msg
        print "Loaded client part"
        for inline in fdinserver:
            regexstring = '\*+ (\w+) ([0-9]+) ([0-9]+) ([0-9]+) (.*)'
            m = re.match(regexstring, inline)
            connectionID = m.group(1)
            messageNumber = int(m.group(2))
            flowMessageNumber = int(m.group(3))
            contentLength = int(m.group(4))
            content = m.group(5)
         
            msg = tuple([flowMessageNumber, contentLength, content,"server2client"])
            if not flowcontainer.has_key(connectionID):
                flowcontainer[connectionID] = dict()
            msgcontainer = flowcontainer[connectionID]
            msgcontainer[flowMessageNumber] = msg
        print "Loaded server part"
        
        fdinclient.close()
        fdinserver.close()
        
        print "{0} number of flows".format(len(flowcontainer))
        nr = 0
        
        fdoutclient = open("{0}_{1}_{2}_client".format("ftp_big_splits",chunksize, nr), "w")
        fdoutserver = open("{0}_{1}_{2}_server".format("ftp_big_splits",chunksize, nr), "w")
        nr = 0
        linecnt = 0
        blockseparator = "******************************************"
        print "Opened output file Nr: {0}".format(nr)
        flowcnt = 0
        for flow in flowcontainer:
            msgcontainer = flowcontainer[flow]
            message_indices = msgcontainer.keys()
            if len(msgcontainer)==1: continue # Skip 1-message flows
            
              
            if has_gaps(message_indices,1):
                continue
            if not is_alternating(msgcontainer):
                continue
            
            c_out = 1
            s_out = 1
            totalcnt = 1
            for m_key in sorted(msgcontainer.keys()):
                msg = msgcontainer[m_key]
                if msg[3]=="server2client":
                    fdoutserver.write("{0} {1} {2} {3} {4} {5}\n".format(blockseparator, flow, c_out, totalcnt, msg[1], msg[2])) 
                    c_out += 1
                else:
                    fdoutclient.write("{0} {1} {2} {3} {4} {5}\n".format(blockseparator, flow, s_out, totalcnt, msg[1], msg[2])) 
                    s_out += 1
                totalcnt += 1
            flowcnt += 1
            if flowcnt>=chunksize:
                fdoutclient.close()
                fdoutserver.close()
                nr += 1
                fdoutclient = open("{0}_{1}_{2}_client".format("ftp_big_splits",chunksize, nr), "w")
                fdoutserver = open("{0}_{1}_{2}_server".format("ftp_big_splits",chunksize, nr), "w")
                flowcnt = 0
                #print "{0} lines read and {1} chunksize flows read. Creating new output file {2}_{1}_{3}".format(linecnt, chunksize,self.infilename, nr)
                #linecnt = 0
                #fdout = open("{0}_{1}_{2}".format(self.infilename,chunksize, nr), "w")
                #inset.clear()
        fdoutclient.close()
        fdoutserver.close()
            
        
        
    

def main():
    s = Splitter("")
    s.split(2000)
    
    
if __name__ == "__main__":
    main()
      
            