'''
Created on 15.04.2012

@author: daubsi
'''

import statistics

config = None

protocolText = "text"
protocolBinary = "binary"
__protocolType = None
__config = None

def getConfig():
    return __config

def setConfig(conf):
    global __config
    __config = conf
    
def getProtocolClassification():
    global __protocolType
    if __protocolType == None:
        __protocolType = statistics.get_classification()
    return __protocolType

def isBinary():
    return getProtocolClassification()==protocolBinary

def isText():
    return getProtocolClassification()==protocolText

def setProtocolClassification(classification):
    global __protocolType
    __protocolType = classification
