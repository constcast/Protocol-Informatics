"""
Sequence module

Used to store sequences read from a PCAP, ASCII or Bro-ADU file.
Sequences are stored, if applicable, including their TCP conenction or UDP bi-flow identifier
and with an marker which reflects at which position in the communication dialog the 
message appeared.
"""

class FlowInfo:
	def __init__(self, identifier = None):
		self.identifier = identifier
		self.sequences = []

	def addSequence(self, sequence):
		self.sequences.append(sequence)

class Sequence:
	def __init__(self, string, mnumber):
		self.message = string
		self.mNumber = mnumber

		self.sequence = []
		# digitize message
		for c in string: 
			self.sequence.append(ord(c))

	
