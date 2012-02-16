from collections import Counter
from cluster import Cluster
from clustercollection import ClusterCollection
import formatinference
import semanticinference
import needlewunsch
import copy

def perform_recursive_clustering(cluster_collection, startAt):
    """
    Performs a recursive clustering on a list of clusters given via cluster_collection.
    The recursion is performed according to the Discoverer paper by Cui et al.
    At first new number of distinct values for each token are calculated in each cluster and
    if this number is lower than a configurable number, the token is considered a FD.
    Then the number of subclusters that would be generated is calculated. If these subclusters
    contain at least one cluster containing more than a configurable amount of messages, the clustering
    is performed and the token is considered a FD. Then the recursion is performed on each of the new clusters
    with the next token.
    
    
    """
    
    config = cluster_collection.get_config()
    # Scan for FD token, Phase 1
    clusters = cluster_collection.get_all_cluster()[:] # <-- "[:]" Very very important... otherwise our iterated list will change because of deletions...
    
    # Save startAt information over cluster iteration
    __startAt = startAt
     
    for cluster in clusters:
        print "Starting processing for next cluster ({0} messages)".format(len(cluster.get_messages()))
        
        startAt = __startAt
        #tokenValue = token.get_token()
        # Check distinct number of values of token
        foundFD = False
        maxTokenIdx = len(cluster.get_messages()[0].get_tokenlist())
        while not foundFD and startAt<maxTokenIdx:
            l = []
            #print "Analyzing token %s" % startAt
            # Check whether this might be a length token
            if "lengthfield" in set(cluster.get_semantics_for_token(startAt)):
                # Current token is a length token. Do not treat as FD
                startAt += 1
                continue
            for message in cluster.get_messages():
                l.append(message.get_tokenAt(startAt).get_token())
            numOfDistinctValuesForToken = len(set(l))
            if 1 < numOfDistinctValuesForToken <= config.maxDistinctFDValues:
                # FD candidate found
                # Check number of potential clusters
                sumUp = Counter(l)
                wouldCluster = False
                for key in sumUp.keys():
                    if sumUp.get(key)>config.minimumClusterSize: # Minimum cluster size of at least one cluster
                        wouldCluster = True
                        break
                if wouldCluster:
                    # Create new cluster
                    print "Subcluster prerequisites fulfilled. Adding FD semantic, splitting cluster and entering recursion"
                    # Senseless here: message.get_tokenAt(startAt).add_semantic("FD")
                    cluster.add_semantic_for_token(startAt,"FD")
                    newCollection = ClusterCollection(config)
                    for key in sumUp.keys():
                            messagesWithValue = cluster.get_messages_with_value_at(startAt,key)
                            newCluster = Cluster(messagesWithValue[0].get_tokenrepresentation())
                            newCluster.get_messages().extend(messagesWithValue)                                
                            newCluster.add_semantic_for_token(startAt, "FD")
                            newCollection.add_cluster(newCluster)
                    print "{0} sub clusters generated".format(len(sumUp.keys()))
                    
                    # Perform format inference on new cluster collection
                    formatinference.perform_format_inference_for_cluster_collection(newCollection, config)
                    semanticinference.perform_semantic_inference(newCollection, config)
                    # Merge clusters with same format
                    
                    #newCollection.mergeClustersWithSameFormat(config)
                    
                    # Perform needle wunsch
                    # Edit 20120120 - not here
                    #===========================================================
                    # cluster1 = newCollection.get_random_cluster()
                    # cluster2 = newCollection.get_random_cluster()
                    # format1 = cluster1.get_formats()
                    # format2 = cluster2.get_formats()
                    # needlewunsch.needlewunsch(format1, format2)
                    # 
                    #===========================================================
                    # Perform recursive step
                    perform_recursive_clustering(newCollection, startAt+1)
                    # Remove old parent cluster
                    cluster_collection.remove_cluster(cluster)
                    cluster_collection.add_clusters(newCollection.get_all_cluster())
                    foundFD = True
                else:
                    pass
                    #print "Subclustering prerequisites not fulfilled. Will not sub-cluster"
            startAt+=1
        print "Recursive clustering analysis for cluster finished"
    
    