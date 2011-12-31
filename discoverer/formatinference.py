
def perform_format_inference(cluster_collection, config):        
    # Perform format inference
    # Walk through every cluster and check for variable/constant properties
    cluster = cluster_collection.get_all_cluster()        
    # Print cluster
    
    for c in cluster:
        messages = c.get_messages()
        # get prototypes from first list element
        prototypeMessage = messages[0]
        tokenList = prototypeMessage.get_tokenlist()
        tokenIndex = 0
        result = []
        for type, value, begin, end in tokenList:
            # Now we have the value, lets check every other message for the same value
            constant = True
            for message in messages:
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
        print "Result for cluster (" , len(c.get_messages()), " entries)",  c.get_representation(), " after property inference: ", result
                         
