from collections import *
from cluster import Cluster

class ClusterCollection():
    def __init__(self):
        self.__cluster = []
    
    def get_all_cluster(self):
        return self.__cluster
    
    def get_cluster(self, representation):
        for c in self.__cluster:
            if c.get("representation")==representation:            
                return c
        return None
    
    def add_message_to_cluster(self, message):
        rep = message.get_tokenrepresentation()
        c = self.get_cluster(rep)
        if c==None:
            c = Cluster(rep)
            self.__cluster.append(c)
        c.get_messages().append(message)
        
    def num_of_clusters(self):
        return len(self.__cluster)
    