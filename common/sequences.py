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

	def getSequences(self):
		return self.sequences

	def uniqSequences(self):
		"""
		Removes duplicate sequences from the stored sequences
		"""
		tmpSet = set()
		for i in self.sequences:
			tmpSet.add(i.message)
		self.sequences = []

		mCounter = 0
		for i in tmpSet:
			self.sequences.append(Sequence(i, mCounter))
			mCounter += 1

	def splitSequences(self, delim):
		"""
		Splits all messages into submessages according to the delimiter
		specified in delim
		"""
		splitSeqs = []
		mnumber = 0
		for i in self.sequences:
			splitStrings = i.getMessage().split(delim)
			for str in splitStrings:
				splitSeqs.append(Sequence(str, mnumber))
				mnumber += 1
		self.sequences = splitSeqs

	def randomSample(self, elements):
		"""
		Selects a random sample of <elements> elements for the set of its
		sequences.
		"""
		newSeqs = []
		
		if elements >= len(self.sequences):
			print "Error: Only got %d elements in the total set." % (len(self.sequences))
			return
		import random
		random.seed()
		for i in range(elements):		
			idx = random.randrange(len(self.sequences))
			print idx
			newSeqs.append(self.sequences.pop(idx))
		self.sequences = newSeqs

	def __repr__(self):
		ret = ""
		for seq in self.sequences:
			ret += "\n\t\t" + seq.message
		return ret

	
class Sequence:
	def __init__(self, string, mnumber):
		self.message = string
		self.mNumber = mnumber

		self.sequence = []
		# digitize message
		for c in string: 
			self.sequence.append(ord(c))

	
	def getMessage(self):
		return self.message

	def getSequence(self):
		return self.sequence

	def getNumber(self):
		return self.number
