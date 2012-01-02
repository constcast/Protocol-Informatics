import common

def perform_semantic_inference(cluster_collection, config):        
# Try to perform semantic inferences

# Walk through every cluster and check messages for obvious results
	cluster = cluster_collection.get_all_cluster()        
	for c in cluster:
		messages = c.get_messages()
		for message in messages:
			tokenlist = message.get_tokenlist()
			for tokenRepresentation in tokenlist:
				tokenRepresentation.set_semantics([]) # Clear existing semantics from previous run
				token = tokenRepresentation.get_token()
				# Check whether it is numeric
				try:
					isNumber = common.is_number(token)
				except TypeError:
					print "Error checking token ", token, " for number semantics"
					isNumber = False
				if isNumber:
					tokenRepresentation.add_semantic("numeric")
					#print "Infered semantic inference 'numeric' for token ", token
					
				# Check whether it is an IP address
				if isinstance(token,str) and common.is_ipv4(token):
					tokenRepresentation.add_semantic("ipv4 address")
					#print "Infered semantic inference 'ipv4 address' for token ", token
				
		# Perform other tests like "is length field?"