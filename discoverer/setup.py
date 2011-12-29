import discoverer

def setup(flowBasedSequences, config):
    if flowBasedSequences==None:
        print "FATAL: No sequences loaded yet"
        return False
    
    for i in flowBasedSequences:
            flowInfo = flowBasedSequences[i]
            for seq in flowInfo.sequences:
                newMessage = discoverer.core.Message(seq.sequence, config)
                #print newMessage.get_payload()
                
