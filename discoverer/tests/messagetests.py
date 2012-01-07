import unittest
import discoverer.message

class Config:
    minWordLength = 3
    
class MessageTests(unittest.TestCase):
    
    def setUp(self):
        self.config = Config()
        
    def runTest(self):
        payload_raw = "This is a test"
        payload = []
        for char in payload_raw:
            payload.append(ord(char))
        payload.extend([0xd,0xa])
        msg = discoverer.message.Message(payload, self.config)
        assert msg.get_length() == 16
        assert len(msg.get_tokenlist()) == 6
        assert msg.get_tokenrepresentation() == ("text","text","text","text","binary", "binary")
        
        