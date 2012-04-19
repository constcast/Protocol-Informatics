import common
from peekable import peekable
from tokenrepresentation import TokenRepresentation
from message import Message
import uuid

def perform_semantic_inference(cluster_collection, config):
    """
    This function performs semantic inference on a list of clusters given
    For each message in these clusters semantics are inferred by analyzing the token
    resp. its context.
    
    At the moment only two semantics are automatically inferred: numeric and IPv4 address
    
    TODO: Add more semantics, e.g. EOL identifier, lenght fields, ...
    """        
# Try to perform semantic inferences

# Walk through every cluster and check messages for obvious results
    cluster = cluster_collection.get_all_cluster()        
    for c in cluster:
        messages = c.get_messages()
        for message in messages:
            tokenlist = message.get_tokenlist()
            iterator = peekable(tokenlist)
            idx = 0
            while not iterator.isLast():
            #for tokenRepresentation in tokenlist:
                tokenRepresentation = iterator.next()
                # TODO: do we need to keep semantics which involve multiple cluster? e.g. sessionids?
                previous_semantics = tokenRepresentation.get_semantics()
                tokenRepresentation.set_semantics([]) # Clear existing semantics from previous run
                if "sessionid" in previous_semantics:    
                    tokenRepresentation.add_semantic("sessionid")
                if "FD" in previous_semantics:
                    tokenRepresentation.add_semantic("FD")
                    
                token = tokenRepresentation.get_token()
                # Check whether it is numeric
                
                try:
                    isNumber = tokenRepresentation.get_tokenType()==Message.typeText and common.is_number(token)
                except TypeError:
                    if config.debug:
                        print "Error checking token {0} for number semantics".format(token)
                    isNumber = False
                if isNumber:
                    tokenRepresentation.add_semantic("numeric")
                    #c.add_semantics(idx,"numeric")
                    #print "Inferred semantic inference 'numeric' for token ", token
                
                    
                # Check whether it is an IP address
                if isinstance(token,str) and common.is_ipv4(token):
                    tokenRepresentation.add_semantic("ipv4 address")
                    # Do not add to cluster unless it is valid for all c.add_semantics(idx,"ipv4 address")
                    #print "Inferred semantic inference 'ipv4 address' for token ", token
        
                # Check for carriage return identifiers
                # When 0d is followed by 0a we've got a CR-LF
                # Sensible? When 0d or 0a is the last token, we've got a single CR resp LF
                # In all other cases assume 0d/0a is just a hex value of the protocol
                if token == 0xd:
                    nextOne = iterator.peek()
                    if isinstance(nextOne, TokenRepresentation):
                        if nextOne.get_token() == 0xa:
                            inferred_formats = c.get_format_inference()
                            if inferred_formats[idx].getType()==Message.typeConst and inferred_formats[idx+1].getType()==Message.typeConst:
                                tokenRepresentation.add_semantic("CR")
                                #c.add_semantics(idx,"CR")
                                nextOne = iterator.next()
                                nextOne.set_semantics(["LF"])
                                #c.add_semantics(idx+1, "LF")
                                idx += 1
                    
                idx +=1
        # Perform other tests like "is length field?"
        # explicitely iterate through all messages like stated in the paper
        # we could also postpone this to the call of 'pushToClusterSeminatics" but..
        
        reference_message = messages[0]
        tokenlist = reference_message.get_tokenlist()
        idx = 0
        for tokenRepresentation in tokenlist:
            if tokenRepresentation.get_tokenType()==Message.typeBinary and idx+1<len(tokenlist):
                ref_value = tokenRepresentation.get_token()
                if not tokenlist[idx+1].get_tokenType()==Message.typeText: # We require that the next token is the text token in question
                    idx += 1
                    continue
                ref_next_length = tokenlist[idx+1].get_length()
                if not ref_value == ref_next_length: # This is no length field
                    idx += 1
                    continue
                ref_message_length = reference_message.get_length()
                is_length = True
                for message in messages:
                    cmp_value = message.get_tokenlist()[idx].get_token()
                    cmp_next_length = message.get_tokenlist()[idx+1].get_length()
                    cmp_message_length = message.get_length()
                    try:
                        diff_val = abs(cmp_value - ref_value)
                    except TypeError: # Could happen if a short text token is mistaken as a binary value
                        break
                    diff_next_length = abs(cmp_next_length - ref_next_length)
                    # The next line also takes total msg length differences into account. This might not be true for
                    # all protocols
                    diff_msg_length = abs(cmp_message_length - ref_message_length)
                    
                    if config.requireTotalLengthChangeForLengthField:
                        if not (diff_val == diff_next_length == diff_msg_length):
                            is_length = False
                        break
                    else:
                        if not (diff_val == diff_next_length): 
                            is_length = False
                            break
                    
                if is_length: # set "lengthfield" semantic for every message in the cluster at the given position
                    for message in messages: # TODO: What if there's only one message in the cluster? Sensible?
                        message.get_tokenlist()[idx].add_semantic("lengthfield")
                        c.add_semantic_for_token(idx,"lengthfield")
            idx += 1
        
        # Try to identify sessionid fields
        
        reference_message = messages[0]
        nextInFlow = reference_message.getNextInFlow()
        if nextInFlow != None and not (len(messages)==1 and config.sessionIDOnlyWithClustersWithMoreThanOneMessage):
            tokenlist = reference_message.get_tokenlist()
            next_tokenlist = nextInFlow.get_tokenlist()
            ref_idx = 0
            for tokenRepresentation in tokenlist:
                tokType = tokenRepresentation.get_tokenType()
                # If its not a binary, it cannot be a cookie
                if tokType!=Message.typeBinary:
                    ref_idx += 1
                    continue
                fmt = c.get_format(ref_idx)
                # If its a binary but const, it cannot be a cookie
                if fmt[1]==Message.typeConst:
                    ref_idx += 1
                    continue
                # Set reference value
                ref_val = tokenRepresentation.get_token()
                # Walk next flow for reference value
                next_idx = 0
                for next_tokenRepresentation in next_tokenlist:
                    # Retrieve next token type
                    nextTokType = next_tokenRepresentation.get_tokenType()
                    # If it is not a binary we don't see it as a cookie
                    if config.sessionIDOnlyWithBinary:
                        if nextTokType!=Message.typeBinary:
                            next_idx += 1
                            continue
                    next_cluster = nextInFlow.getCluster()
                    # Get format of comparating message
                    comp_fmt = next_cluster.get_format(next_idx)
                    # If it is const, it cannot be a sessonid
                    if comp_fmt[1]==Message.typeConst:
                        next_idx += 1
                        continue
                    # Load comparator value
                    comp_val = next_tokenRepresentation.get_token()
                    if ref_val==comp_val: # We've got a potential hit, now compare all messages for the same idx pairs
                        isCookie = True
                        for cmp_ref_msg in messages:
                            if not isCookie:
                                break
                            if cmp_ref_msg == messages[0]: # Skip first message (we've already checked that one
                                continue
                            cmp_ref_tok_list = cmp_ref_msg.get_tokenlist()
                            
                            cmp_ref_val = cmp_ref_tok_list[ref_idx].get_token()
                            cmp_cmp_msg = cmp_ref_msg.getNextInFlow()
                            if cmp_cmp_msg == None:
                                isCookie = False
                            else:         
                                cmp_cmp_tok_list = cmp_cmp_msg.get_tokenlist()
                                if next_idx>=len(cmp_cmp_tok_list):
                                    # Obviously "next" points to messages in different clusters
                                    # so the len might differ from the reference next cluster
                                    # used to find our reference cookie value
                                    # Therefore this cannot be a cookie
                                    isCookie = False
                                    continue
                                cmp_cmp_val = cmp_cmp_tok_list[next_idx].get_token()
                                if (cmp_ref_val != cmp_cmp_val) or ((cmp_ref_val == cmp_cmp_val) and (cmp_ref_val == ref_val)):
                                    isCookie = False
                        if isCookie:
                            # Set cookie semantic in this message and the other
                            sessionid = uuid.uuid1()
                            for message in messages: # Set for every message and the cluster itself
                                #message.get_tokenlist()[ref_idx].add_semantic("sessionid_{0}".format(sessionid))
                                message.get_tokenlist()[ref_idx].add_semantic("sessionid")
                                nextMsg = message.getNextInFlow()
                                #nextMsg.get_tokenlist()[next_idx].add_semantic("sessionid_{0}".format(sessionid))
                                nextMsg.get_tokenlist()[next_idx].add_semantic("sessionid")
                            c.add_semantic_for_token(ref_idx,"sessionid")
                    next_idx += 1
                ref_idx += 1
                
            
    
    # Push to cluster
    pushUpToCluster(cluster_collection, config)    
    
    
def pushUpToCluster(cluster_collection, config):
    cluster = cluster_collection.get_all_cluster()        
    for c in cluster:
        messages = c.get_messages()
        # Sum up all semantics - put into cluster semantics if valid for every single message
        reference_message = messages[0]
        tokenlist = reference_message.get_tokenlist()
        idx = 0
        for tokenRepresentation in tokenlist:          

            referenceSemantics = tokenRepresentation.get_semantics()
            # Keep FD semantics on cluster level
            if c.has_semantic_for_token(idx,"FD"):
                c.clear_semantics_for_token(idx)
                c.add_semantic_for_token(idx,"FD")
            else:
                c.clear_semantics_for_token(idx)
            for semantic in referenceSemantics:                                    
                # Search every message instance in message cluster    
                for message in messages:
                    cmpsemantics = message.get_tokenlist()[idx].get_semantics()
                    foundSemantic = False
                    for cmpsemantic in cmpsemantics:
                        if cmpsemantic==semantic:
                            foundSemantic = True
                            break
                    if not foundSemantic:
                        break
                
                if foundSemantic == True:
                    # Add to cluster semantics
                    c.add_semantic_for_token(idx,semantic)
                    
            idx += 1
                        
                        

        
        
    