import common

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
					#print "Inferred semantic inference 'numeric' for token ", token
					
				# Check whether it is an IP address
				if isinstance(token,str) and common.is_ipv4(token):
					tokenRepresentation.add_semantic("ipv4 address")
					#print "Inferred semantic inference 'ipv4 address' for token ", token
				
		# Perform other tests like "is length field?"
		
		# Check for carriage return identifiers
		# When 0d is followed by 0a we've got a CR-LF
		# When 0d or 0a is the last token, we've got a single CR resp LF
		# In all other cases assume 0d/0a is just a hex value of the protocol
		