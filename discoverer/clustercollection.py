from collections import Counter
from cluster import Cluster
import random
import discoverer

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
        if self.__cluster.count(cluster) == 0:
            self.__cluster.append(cluster)
    
    def add_clusters(self, clusters):
        for cluster in clusters:
            self.add_cluster(cluster)
        #self.__cluster.extend(clusters)
        
    def mergeClustersWithSameFormat(self, config):
        # This code performs cluster comparision not as described in the paper, as
        # it uses the explicit format for finding identical clusters. It does however not
        # * check whether "constant" in cluster A is the same as in cluster B (in this case they should obviously not be merged!)
        # * and it does not perform variable/constant considerations as described in the paper
        # 
        #=======================================================================
        # print "Trying to merge clusters"
        # l = []
        # for cluster in self.__cluster:
        #    l.append(tuple(cluster.get_format_inference()))
        # sumUp = Counter(l) # Counts identical format inference tuples
        # cntMerged = 0
        # for key in sumUp.keys(): # Iterate all existing format inference tuples
        #    if sumUp.get(key)>1: # There are clusters with the same format inferred
        #        target = None
        #        for cluster in self.__cluster:
        #            if tuple(cluster.get_format_inference())==key:
        #                if target == None:
        #                    target = cluster
        #                else:
        #                    
        #                    target.add_messages(cluster.get_messages())
        #                    self.__cluster.remove(cluster)
        #                    cntMerged += 1    
        #        # self.__cluster.append(target) Not necessary: target is already in cluster
        #        print "Merged ", cntMerged, " clusters with the same format"
        #=======================================================================
        
        # Different approach
        # Iterate collection and compare each and every cluster representation explicitly
        # Do not use needle-wunsch here
        
        # Tag each mergable cluster with reference to the first cluster and put a merged version of these into the tempcollection
        # once the whole collection has been traversed. Then remove them from the collection. Continue as long as there is still an item left
        # in the original collection.
        # tempCollection will contain all the merged clusters and the unmergable cluster left in the end
        
        if len(self.__cluster)==1:
            return # We cannot merge a single cluster
        
        
        copiedCollection = self.__cluster[:]  # <-- [:] is very important to work on a copy of the list
        ori_len = len(copiedCollection)
        tempCollection = ClusterCollection()

        while len(copiedCollection)>0:            
            mergeCandidates = []            
            cluster1 = copiedCollection[0]
            idx_inner = 1
            while (idx_inner < len(copiedCollection)-1):             
            #for idx_inner in range(1,len(copiedCollection)-1):    
                
                cluster2 = copiedCollection[idx_inner]
                format1 = cluster1.get_formats()
                format2 = cluster2.get_formats()
                if not len(format1)==len(format2):
                    continue # The two clusters have different length [should not happen within subclusters]
                # Perform token check
                shouldMerge = True
                for format_token_idx in range(0,len(format1)-1):
                    token1 = cluster1.get_format(format_token_idx)
                    token2 = cluster2.get_format(format_token_idx)
                    representation = token1[0]
                    fmt_infer= token1[1]
                    semantics = token1[2]
                    if not representation == token2[0]: # Token mismatch --> will not merge
                        shouldMerge = False
                        break
                    
                    checkValues = False
                    if semantics == token2[2]:
                        if len(semantics)==0: # They match because there are no semantics... :-(
                            checkValues = True 
                    else: # Semantics mismatch --> will not merge
                        shouldMerge = False
                        break
                    
                    
                    if checkValues:
                        if fmt_infer == token2[1]:
                            # Check constant/variable cover
                            if fmt_infer=='const': 
                                # Check instance of const value
                                # FIX: Each cluster must have at least 1 message!
                                if not cluster1.get_messages()[0].get_tokenAt(format_token_idx).get_token() == cluster2.get_messages()[0].get_tokenAt(format_token_idx).get_token():
                                    # Const value mismatch --> will not merge
                                    shouldMerge = False
                                    break
                            else:
                                # Check variable/variable instances
                                # Check for overlap in values. If there is no overlap -> Mismatch
                                allvalues1 = cluster1.get_values_for_token(format_token_idx)
                                allvalues2 = cluster2.get_values_for_token(format_token_idx)
                                if len(allvalues1.intersection(allvalues2))==0:
                                    # No overlap -> Mismatch
                                    shouldMerge = False
                                    break
                            
                        else:
                            # Variable/Constant format inference
                            # Check whether variable token takes value of constant one at least once
                            found = True
                            if fmt_infer == 'const':
                                # Search for cluster1's value in cluster2
                                cluster1val = cluster1.get_messages()[0].get_tokenAt(format_token_idx).get_token()
                                hits = cluster2.get_messages_with_value_at(format_token_idx,cluster1val)
                                found = len(hits)>0
                            else:
                                # Search for cluster2's value in cluster1
                                cluster2val = cluster2.get_messages()[0].get_tokenAt(format_token_idx).get_token()
                                hits = cluster1.get_messages_with_value_at(format_token_idx,cluster2val)
                                found = len(hits)>0
                            if not found:
                                # No instance of variable in const mismatch --> will not merge
                                shouldMerge = False
                                break
            
            
                               
                # End of token iteration
                if shouldMerge:    
                    mergeCandidates.append(cluster2)
                idx_inner += 1     
            # End of for each clusterloop
            
            newCluster = Cluster(cluster1.get_representation())             
            newCluster.add_messages(cluster1.get_messages())
            
            for cluster in mergeCandidates:                    
                newCluster.add_messages(cluster.get_messages())
                copiedCollection.remove(cluster)
            
            discoverer.formatinference.perform_format_inference_for_cluster(newCluster,config)    
            # TODO: Build up new semantic information in newCluster
            copiedCollection.remove(cluster1)               
            tempCollection.add_cluster(newCluster)            
                
        # Clear own collection
        self.__cluster = []
        # Copy all clusters from tempCollection to our self
        self.add_clusters(tempCollection.get_all_cluster())
        if ori_len == len(self.__cluster):
            print "No mergable clusters within collection identified"
        else:
            print "Cluster collection shrunk from %i to %i by merging", ori_len, len(self.__cluster)
    
    def get_random_cluster(self):             
        return random.choice(self.__cluster)
        
    def add_message_to_cluster(self, message):
        rep = message.get_tokenrepresentation()
        c = self.get_cluster(rep)
        if c==None:
            c = Cluster(rep)
            self.__cluster.append(c)
        c.get_messages().append(message)
        
    def num_of_clusters(self):
        return len(self.__cluster)
    