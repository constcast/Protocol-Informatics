from message import Message
from clustercollection import ClusterCollection
import string

class Setup:
    """
    This is the starting class of the Discoverer implementation
    It creates Message objects out of the sequences read from an inputfile
    performs type inference and and clusters them ("Initial clustering" step) 
    """

    def __init__(self,flowBasedSequences, direction, config):
        if flowBasedSequences==None:
            print "FATAL: No sequences loaded yet"
            return False

        self.cluster_collection = ClusterCollection(config)    
        for i in flowBasedSequences:
                flowInfo = flowBasedSequences[i]
                for seq in flowInfo.sequences:
                    #===========================================================
                    # myseq = seq.sequence
                    # if myseq[0] == 0xd:
                    #    if myseq[1] == 0xa:
                    #        print "Found 0D0A in seq ", myseq, " in flowInfo ", flowInfo
                    #===========================================================
                    newMessage = Message(seq.sequence, seq.connIdent, seq.mNumber, seq.flowNumber, direction, config)
                    self.cluster_collection.add_message_to_cluster(newMessage)
                    
                    #print newMessage.get_payload()
                    #print "Tokenlist of ", seq.sequence, " = ", newMessage.get_tokenrepresentation_string()
                    # Cluster message
                    
                    #===============================================================
                    # newrep = newMessage.get_tokenrepresentation()
                    # if not cluster.has_key(newrep):
                    #    cluster.update({newrep: [newMessage]})
                    # else:
                    #    l = cluster.get(newrep)
                    #    l.append(newMessage)
                    #    cluster.update({newrep: l})
                    #===============================================================
         
        
        
    def __repr__(self):
        return "%s" % self.cluster_collection
    
    def get_cluster_collection(self):
        
        return self.cluster_collection
    
    def debug(self):
        cluster = self.cluster_collection.get_all_cluster()        
        # Print cluster
        for c in cluster:
            keys = c.keys()
            for key in keys:
                l = c.get(key)
                print "Key: {0} Elements: {1}".format(key,l)  
            
        