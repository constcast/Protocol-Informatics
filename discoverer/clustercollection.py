from collections import Counter
from cluster import Cluster
import random
import discoverer
import curses
import formatinference
from message import Message
from xml.sax.saxutils import escape
from cStringIO import StringIO

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
    def __init__(self,config):
        self.__cluster = []
        self.__config = config
    
    def get_config(self):
        return self.__config
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
        
    def mergeClustersWithSameFormat(self):
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
        
        config = self.__config
        
        if not config.mergeSimilarClusters:
            print "Cluster merging disabled via configuration"
            return
        
        copiedCollection = self.__cluster[:]  
        ori_len = len(copiedCollection)
        tempCollection = ClusterCollection(config)

        while len(copiedCollection)>0:            
            mergeCandidates = []            
            cluster1 = copiedCollection[0]
            idx_inner = 1
            while (idx_inner < len(copiedCollection)):             
            #for idx_inner in range(1,len(copiedCollection)-1):    
                
                cluster2 = copiedCollection[idx_inner]
                format1 = cluster1.get_formats()
                format2 = cluster2.get_formats()
                if not len(format1)==len(format2):
                    idx_inner += 1
                    continue # The two clusters have different length [should not happen within subclusters]
                # Perform token check
                shouldMerge = True
                for format_token_idx in range(0,len(format1)-1):
                    token1 = cluster1.get_format(format_token_idx)
                    token2 = cluster2.get_format(format_token_idx)
                    representation = token1[0]
                    fmt_infer = token1[1]
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
                        if fmt_infer.getType() == token2[1].getType():
                            # Check constant/variable cover
                            if fmt_infer.getType()=='const': 
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
                                if len(set(allvalues1).intersection(set(allvalues2)))==0:
                                    # No overlap -> Mismatch
                                    shouldMerge = False
                                    break
                            
                        else:
                            # Variable/Constant format inference
                            # Check whether variable token takes value of constant one at least once
                            found = True
                            if fmt_infer.getType() == 'const':
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
            newCluster.set_semantics(cluster1.get_semantics())             
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
            print ("Cluster collection shrunk from {0} to {1} by merging".format(ori_len, len(self.__cluster)))
    
    def get_random_cluster(self):             
        return random.choice(self.__cluster)
        
    def add_message_to_cluster(self, message):
        rep = message.get_tokenrepresentation()
        c = self.get_cluster(rep)
        if c==None:
            c = Cluster(rep)
            self.__cluster.append(c)
        c.add_messages([message])
        #c.get_messages().append(message)
        
    def num_of_clusters(self):
        return len(self.__cluster)
    
    def isTextCandidate(self, cluster, idx):
        """
        Determines whether a certain token is a candidate for binary->text migration
        Token needs to fulfill the following criteria:
        * is binary
        * has no semantics (also no FD) // TODO: Check for FD in cluster
        * is ascii-printable
        """
        fmt = cluster.get_formats()[idx]
        if fmt[0] in ('text','direction'):
            return False
        isCandidate = True
        for message in cluster.get_messages():
            if not isCandidate:
                break
            token = message.get_tokenAt(idx)
            if not len(token.get_semantics())==0: # Has semantics, probably no text
                isCandidate = False
                break
            value = token.get_token()
            if not curses.ascii.isprint(value): # Binary value is no printable character
                isCandidate = False
                break
        if not isCandidate:
            return False
        return True
        #print "Binary token {} is text candidate".fmt(idx)
        
        
    def fix_tokenization_errors(self, config):
        """ 
        Fixes tokenization errors. Tries to build text tokens (1<size<minWordLength)
        out of binary tokens that fulfill the following criteria:
        * binary
        * not FD
        * no semantics
        * printable ascii value
        Rationale:
        At first the candidate tokens that fulfill the above citeria are chosen and
        put into a list. For example: indices = [0,2,4,5,8,9,10,13,14,16]
        Then this list is traversed from last to first and sequences of adjacent numbers
        are sought. (here 4-5, 8-10, 13-14) These are the candidates that can be merged
        Candidates are merged one by one from last to first.
        Note:
        It is necessary to rebuild format inference and semantic inference afterwards, as
        these are not refreshed automatically
        
        """
        clusters = self.__cluster[:] 
        #clusters = clustercollection.get_all_cluster()
        for cluster in clusters:
            indices = []
            for idx in range(len(cluster.get_formats())-1,-1,-1):
                if self.isTextCandidate(cluster, idx):
                    indices.append(idx)
            if len(indices)==0:
                continue # No candidates found
            indices.reverse() # New
            #print indices
            # Try to find sequences of adjacent numbers that are shorter than minWordLength
            # Fake
            #indices = [0,2,4,5,8,9,10,13,14,16]

            #print indices       
            
            idx = len(indices)-1
            while idx>0:
                groupStart = indices[idx];
                groupEnd = groupStart;
                while idx > 0 and indices[idx] - indices[idx - 1] == 1:
                    groupEnd = indices[idx-1];
                    idx -=1
                
                # End of sequence
                if not groupEnd == groupStart:
                    #print "Subsequence found: [{}-{}]".format(groupEnd,groupStart)
                    # merge it
                    while groupStart>groupEnd:
                            cluster.mergeToken(groupStart-1,groupStart)
                            groupStart -= 1
                idx-=1
            #print "Finished"
    
    def print_clusterCollectionInfo(self, file=""):
        """
        Prints the inferred formats for all clusters in the collection in a human
        readable way
        """
        cluster = self.__cluster[:]             
        self.print_clusterInfo(cluster, file)
        
    def getXMLRepresentation(self):         
        import sys
        old_stdout = sys.stdout
        handle = StringIO()
        sys.stdout = handle

        print '<cluster_collection numberOfCluster="{0}">'.format(len(self.get_all_cluster()))
        
        for c in self.__cluster:
            messages =  c.get_messages()  
            formats = c.get_formats()
            var_stats = c.getVariableStatistics()
            
            print '<cluster internal_name="{0}" numOfMessages="{1}">'.format(c.getInternalName(), len(messages))
            print '<regex>{0}</regex>'.format(escape(c.getRegEx()))
            print '<visual_regex>{0}</visual_regex>'.format(escape(c.getRegExVisual()))

            print '<message_format hash="{0}" numOfFormats="{1}">'.format(c.getFormatHash(), len(formats))
            for idx, format in enumerate(formats):
                category, formatType, semantics = format
                    
                print '\t<message_format_element index="{0}" category="{1}">'.format(idx, category)
                if isinstance(formatType, formatinference.Constant):
                    print '\t\t<format type="constant">'
                    print '\t\t\t<constant_value>{0}</constant_value>'.format(escape(str(formatType.getConstValue())))
                    print '\t\t</format>'
                elif isinstance(formatType, formatinference.Variable):
                    print '\t\t<format type="variable" />'
                    elem = var_stats[idx]
                    if isinstance(elem,formatinference.VariableNumberStatistics):
                        print '<variable_statistic type="NumberStatistic">'
                        print '\t<minimum>{0}</minimum>'.format(elem.getMin())
                        print '\t<maxmimum>{0}</maximum>'.format(elem.getMax())
                        print '\t<mean>{0}</mean>'.format(elem.getMean())
                        print '\t<variance>{0}</variance>'.format(elem.getVariance())
                        print '\t<num_of_distinct_samples>{0}</num_of_distinct_samples>'.format(elem.numberOfDistinctSamples())
                        print '\t<top3list>'
                        for item,amount in elem.getTop3():
                            print '\t\t<top3listitem>'
                            print '\t\t\t<value>{0}</value>'.format(item)
                            print '\t\t\t<amount>{0}</amount>'.format(amount)
                            print '\t\t</top3listitem>'
                        print '\t</top3list>'
                        print '</variable_statistic>'
                    elif isinstance(elem,formatinference.VariableTextStatistics):
                        print '<variable_statistic type="TextStatistic">'
                        print '\t<shortest_text>{0}</shortest_text>'.format(escape(elem.getShortest()))
                        print '\t<longest_text>{0}</longest_text>'.format(escape(elem.getLongest()))
                        print '\t<num_of_distinct_samples>{0}</num_of_distinct_samples>'.format(elem.numberOfDistinctSamples())
                        print '\t<top3list>'
                        for item,amount in elem.getTop3():
                            print '\t\t<top3listitem>'
                            print '\t\t\t<value>{0}</value>'.format(escape(item))
                            print '\t\t\t<amount>{0}</amount>'.format(amount)
                            print '\t\t</top3listitem>'
                        print '\t</top3list>'
                        print '</variable_statistic>'
                if (len(semantics)>0):
                    print '\t\t<semantics length="{0}">'.format(len(semantics))
                    for s in semantics:
                        print '\t\t\t<semantic>{0}</semantic>'.format(s)
                    print '\t\t</semantics>'
                print '\t</message_format_element>'
                
            print '</message_format>'
            
            print '</cluster>'


        print '</cluster_collection>'
        body = handle.getvalue()
        handle.close()         
        sys.stdout = old_stdout
        return body
    
    def print_clusterInfo(self, cluster, file=""):
        """
        Prints the inferred formats for a cluster in a human readable way
        If file is set, output will be written to a file instead of stdout
        """
        if not file == "":            
            import sys
            old_stdout = sys.stdout
            handle = open(file,"w")
            sys.stdout = handle
            print "Dump of 'Discoverer' analysis"
            print "Current config:"
            self.__config.print_config()
        print "{0} cluster(s) have been generated".format(len(cluster))
        
        print "Statistics: {0}".format(discoverer.statistics.stats)        
        print "Protocol is classified as: {0}".format(discoverer.statistics.get_classification())
        
        totalNumOfNoConstCluster = 0
        for c in cluster:
                
            messages =  c.get_messages()  
            formats = c.get_formats()
            print "*"*50
            print "Cluster information: {0} entries".format(len(messages))
            print "Internal name: {0}".format(c.getInternalName())
            print "Format inferred ({0} token):\t{1}".format(len(formats),formats)
            print "Variable stats:"
            var_stats = c.getVariableStatistics()
            for idx, elem in enumerate(var_stats):
                if isinstance(elem,formatinference.VariableNumberStatistics):
                    print "Index {0}, Numeric: Min: {1}, Max: {2}, Mean: {3}, Variance: {4}, Distinct: {5}, Top3: {6}".format(idx, elem.getMin(), elem.getMax(), elem.getMean(), elem.getVariance(), elem.numberOfDistinctSamples(), ", ".join("'" + str(idx)+"' ("+str(item) +")" for idx,item in elem.getTop3()))
                elif isinstance(elem,formatinference.VariableTextStatistics):
                    print "Index {0}, Text: Shortest: '{1}', Longest: '{2}', Distinct: {3}, Top3: {4}".format(idx, elem.getShortest(), elem.getLongest(), elem.numberOfDistinctSamples(), ", ".join("'" + str(idx)+"' ("+str(item)+")" for idx,item in elem.getTop3()))
            print "Messageformat hash:\t\t{0}".format(c.getFormatHash())
            print "RegEx\t\t\t\t\t{0}".format(c.getRegEx())
            print "RegExVisual:\t\t\t{0}".format(c.getRegExVisual())
            # print "Token fmt: {0}".fmt(c.get_representation())s            
            #for message in messages:
            #    print message
            idx = 0
            numOfConst = 0
            for fmt in formats:
                print "Token {0}:".format(idx) ,
                if "FD" in fmt[2]:
                    rawValues = c.get_all_values_for_token(idx)
                    sumUp = Counter(rawValues)
                    values = ""
                    for key in sumUp.keys():
                        #if sumUp.get(key)>1:
                        newstr = "'{0}' ({1}), ".format(key, sumUp.get(key))
                        values += newstr
                    print "FD, {0} values: {1}".format(len(sumUp), values[:-2])
                elif "lengthfield" in fmt[2]:
                    rawValues = c.get_all_values_for_token(idx)
                    sumUp = Counter(rawValues)
                    values = ""
                    for key in sumUp.keys():
                        #if sumUp.get(key)>1:
                        newstr = "'{0}' ({1}), ".format(key, sumUp.get(key))
                        values += newstr
                    print "Length field, {0} values: {1}".format(len(sumUp), values[:-2])
                else:
                    if fmt[1].getType()==Message.typeConst: # format is "const (xyz)"
                        value = messages[0].get_tokenAt(idx).get_token()
                        if fmt[0]=='binary':
                            print "const binary token, value 0x{:02x}".format(value),
                            if not fmt[2]==[]:
                                print "({})".format(",".join(fmt[2]))
                            else:
                                print ""
                        else:
                            print "const {} token, value '{}'".format(fmt[0],value)  
                        
                        # Count token as contributing to const if it is no EOL and no direction token
                        if value!=0x0a and value!=0x0d and fmt[0]!=Message.typeDirection:
                            numOfConst += 1
                        
                    else: # variable
                        rawValues = c.get_all_values_for_token(idx)
                        sumUp = Counter(rawValues)
                        values = ""
                        keys = sumUp.keys()
                        for i in range(0,min(5,len(keys))):
                            key = keys[i]
                            if fmt[0]=='binary':
                                newstr = "0x{:02x} ({}), ".format(key, sumUp.get(key))
                            else:
                                newstr = "'{0}' ({1}), ".format(key, sumUp.get(key))
                                
                            values += newstr
                        if len(values)>0:
                            values += "..."
                        if fmt[0]=='binary':
                            print "variable binary token, values {}".format(values),
                            if not fmt[2]==[]:
                                print "({})".format(",".join(fmt[2]))
                            else:
                                print ""
                        else:
                            print "variable text token, values: {0}".format(values)
                        
                idx += 1
            if numOfConst == 0:
                # We've got a variable only cluster
                totalNumOfNoConstCluster += 1
    
        print
        print "Cluster without a single const token (excl. EOL): {0}".format(totalNumOfNoConstCluster)
                                                                            
        if not file=="":
            handle.close()         
            sys.stdout = old_stdout
            import os            
            print "Finished. File size %0.1f KB" % (os.path.getsize(file)/1024.0)               
