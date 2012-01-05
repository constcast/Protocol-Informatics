from collections import Counter
from cluster import Cluster

class ClusterCollection():
    """
    This class acts as a collection for clusters
    It offers functions to add and remove a cluster as well as
    adding messages to the correct cluster based on it's token representation.
    add_message_to_cluster() will only work in the initial clustering phase
    when each cluster has a unique format
    function mergeClusterWithSameFormat merges two clusters which exhibit the same
    representation.
    """
    def __init__(self):
        self.__cluster = []
    
    def get_all_cluster(self):
        return self.__cluster
    
    def get_cluster(self, representation):
        for c in self.__cluster:
            if c.get("representation")==representation:            
                return c
        return None
    
    def remove_cluster(self, cluster):
        self.__cluster.remove(cluster)
        
    def add_cluster(self, cluster):
        self.__cluster.append(cluster)
    
    def add_clusters(self, clusters):
        self.__cluster.extend(clusters)
        
    def mergeClustersWithSameFormat(self):
        l = []
        for cluster in self.__cluster:
            l.append(tuple(cluster.get_format_inference()))
        sumUp = Counter(l)
        cntMerged = 0
        for key in sumUp.keys():
            if sumUp.get(key)>1: # There are clusters with the same format inferred
                target = None
                for cluster in self.__cluster:
                    if tuple(cluster.get_format_inference())==key:
                        if target == None:
                            target = cluster
                        else:
                            target.add_messages(cluster.get_messages())
                            self.__cluster.remove(cluster)
                            cntMerged += 1    
                self.__cluster.append(target)
                print "Merged ", cntMerged, " clusters with the same format"
                
        
    def add_message_to_cluster(self, message):
        rep = message.get_tokenrepresentation()
        c = self.get_cluster(rep)
        if c==None:
            c = Cluster(rep)
            self.__cluster.append(c)
        c.get_messages().append(message)
        
    def num_of_clusters(self):
        return len(self.__cluster)
    