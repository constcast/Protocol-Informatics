import discoverer

cluster = {}

def setup(flowBasedSequences, config):
    if flowBasedSequences==None:
        print "FATAL: No sequences loaded yet"
        return False
    
    for i in flowBasedSequences:
            flowInfo = flowBasedSequences[i]
            for seq in flowInfo.sequences:
                newMessage = discoverer.core.Message(seq.sequence, config)
                #print newMessage.get_payload()
                #print "Tokenlist of ", seq.sequence, " = ", newMessage.get_tokenrepresentation_string()
                # Cluster message
                
                newrep = newMessage.get_tokenrepresentation_string()
                if not cluster.has_key(newrep):
                    cluster.update({newrep: [newMessage]})
                else:
                    l = cluster.get(newrep)
                    l.append(newMessage)
                    cluster.update({newrep: l})
            
    # Print cluster
    keys = cluster.keys()
    for key in keys:
        l = cluster.get(key)
        print "Key:", key, " Elements: ", l  
        
    # Step 1 finished
    
    # Perform format inference
    # Walk through every cluster and check for variable/constant properties
    print '+++++++++++++++++++++++++++++++++++'
    keys = cluster.keys()
    for key in keys:
        l = cluster.get(key)
        print "Key:", key, " Elements: ", l  
        # get prototypes from first list elemnt
        prototypeMessage = l[0]
        tokenList = prototypeMessage.get_tokenlist()
        tokenIndex = 0
        result = []
        for type, value, begin, end in tokenList:
            # Now we have the value, lets check every other message for the same value
            constant = True
            for message in l:
                tl = message.get_tokenlist()
                t,v,b,e = tl[tokenIndex]
                if not value==v:
                    constant = False
                    break
            if constant:
                result.append("const")
            else:
                result.append("variable")
            tokenIndex +=1
        print "Result for cluster after property inference: ", result
                      
