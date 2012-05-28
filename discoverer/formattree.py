from cStringIO import StringIO
import re

class FormatTreeNode(object):
    
    def __init__(self, format, parent, index, nodename):
        self.__format = format
        self.__parent = parent
        self.__children = []
        self.__cluster = []
        self.__index = index
        self.__nodename = nodename
        
    def getName(self):
        return self.__nodename
    
    def getFormat(self):
        return self.__format
                      
    def getIndex(self):
        return self.__index
                
    def addChild(self, child):
        self.__children.append(child)
    
    def addContainedCluster(self, cluster):
        self.__cluster.append(cluster)    
    
    def getContainedCluster(self):
        return self.__cluster
    
    def removeContainedCluster(self, cluster):
        self.__cluster.remove(cluster)
                        
    def getChildren(self):
        return self.__children
    
    def getMaxSpread(self):
        ms = len(self.__children)
        for c in self.__children:
            if c.getMaxSpread()>ms:
                ms = c.getMaxSpread()
        return ms
    
class FormatTree(object):
    
    def __init__(self):
        self.__root = FormatTreeNode(None, None,0, "s0")
        
    def getRoot(self):
        return self.__root
    
    def rec_dump(self, currentNode):
    
        for node in currentNode.getChildren():
            s = node.getName()
            s = re.sub("'", "", s)
            print "{0} [shape=circle];".format(s)
            
            t = currentNode.getName()
            t = re.sub("'", "", t)
            
            u = str(node.getFormat())
            u = re.sub("'", "", u) 
            print '{0} -> {1} [label="{2}"];'.format(t, s, u)
            self.rec_dump(node)
            
    def dump(self):
        import sys
        old_stdout = sys.stdout
        handle = StringIO()
        sys.stdout = handle
        try:
            print "digraph ProtocolStatemachine {"
            currentNode = self.getRoot()
            self.rec_dump(currentNode)
            print "}"
            body = handle.getvalue()
            handle.close()         
            sys.stdout = old_stdout
            return body
        except:
            handle.close()         
            sys.stdout = old_stdout
            
            print sys.exc_info()