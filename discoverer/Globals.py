'''
Created on 15.04.2012

@author: daubsi
'''

import statistics

config = None

protocolText = "text"
protocolBinary = "binary"
__protocolType = None
def getProtocolClassification():
    global __protocolType
    if __protocolType == None:
        __protocolType = statistics.get_classification()
    return __protocolType


