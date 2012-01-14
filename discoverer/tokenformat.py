class TokenFormat:
    """
    Represents a token for NW aligment checks
    """
    
    def __init__(self, format):
        self.format = format
        
    def __eq__(self, other):
        if not self.format(0)==other.format(0):
            return False
        if not self.format(1)==other.format(1):
            return False
        if not self.format(2)==other.format(2):
            return False
        return True