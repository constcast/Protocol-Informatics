import unittest
import discoverer.message
import discoverer.clustercollection
class Config:
    minWordLength = 3
    
class MergeTests(unittest.TestCase):
    
    def setUp(self):
        self.config = Config()
        self.config.minWordLength = 3
        self.config.maxMessagePrefix = 2048
        
    def binarize(self, l, s):
        for char in s:
            l.append(ord(char))
            
    def test_OneReplace(self):
        # Test 1
        payload_raw = "This"
        payload = []
        self.binarize(payload, payload_raw)
        payload.extend([0x0,0x0])
        payload_raw = "is"
        self.binarize(payload, payload_raw)
        payload.extend([0x0,0x0,0x0])
        payload_raw = "a"
        self.binarize(payload, payload_raw)
        payload.extend([0x0])
        payload_raw = "test"
        self.binarize(payload, payload_raw)
                
        msg = discoverer.message.Message(payload, self.config)
        
        assert len(msg.get_tokenlist()) == 11
        assert msg.get_tokenrepresentation() == ("text","binary","binary","binary","binary", "binary","binary", "binary","binary", "binary","text")
        
        c = discoverer.clustercollection.ClusterCollection()
        c.add_message_to_cluster(msg)
        discoverer.formatinference.perform_format_inference_for_cluster_collection(c, self.config)
        discoverer.semanticinference.perform_semantic_inference(c, self.config)
        c.fix_tokenization_errors(self.config)
        discoverer.formatinference.perform_format_inference_for_cluster_collection(c, self.config)
        discoverer.semanticinference.perform_semantic_inference(c, self.config)
        c.print_clusterCollectionInfo()
        
        assert len(msg.get_tokenlist()) == 10
        assert msg.get_tokenrepresentation() == ("text","binary","binary","text", "binary","binary", "binary","binary", "binary","text")
        
    def test_TwoReplace(self):
        # Test 2
        self.config.minWordLength = 5
        payload_raw = "This"
        payload = []
        self.binarize(payload, payload_raw)
        payload.extend([0x0,0x0])
        payload_raw = "is"
        self.binarize(payload, payload_raw)
        payload.extend([0x0,0x0,0x0])
        payload_raw = "a"
        self.binarize(payload, payload_raw)
        payload.extend([0x0])
        payload_raw = "test"
        self.binarize(payload, payload_raw)
                
        msg = discoverer.message.Message(payload, self.config)
        
        assert len(msg.get_tokenlist()) == 17
        assert msg.get_tokenrepresentation() == ("binary","binary","binary","binary","binary","binary","binary","binary", "binary","binary", "binary","binary", "binary","binary","binary","binary","binary")
        
        c = discoverer.clustercollection.ClusterCollection()
        c.add_message_to_cluster(msg)
        discoverer.formatinference.perform_format_inference_for_cluster_collection(c, self.config)
        discoverer.semanticinference.perform_semantic_inference(c, self.config)
        c.fix_tokenization_errors(self.config)
        discoverer.formatinference.perform_format_inference_for_cluster_collection(c, self.config)
        discoverer.semanticinference.perform_semantic_inference(c, self.config)
        assert len(msg.get_tokenlist()) == 10
        assert msg.get_tokenrepresentation() == ("text","binary","binary","text", "binary","binary", "binary","binary", "binary","text")
        
        c.print_clusterCollectionInfo()
        