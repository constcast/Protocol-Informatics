"""
Used to store sequences read from a PCAP, ASCII or Bro-ADU file.
Sequences are stored, if applicable, including their TCP conenction or UDP bi-flow identifier
and with an marker which reflects at which position in the communication dialog the 
message appeared.
"""

class Sequence:
	def __init__(self, string):
