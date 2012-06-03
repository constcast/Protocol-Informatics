import Globals


def is_number(s):
    """
    Checks whether s is really a number and raises a ValueError if not
    Taken from http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-in-python
    """
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def is_ipv4(address):
    """
    Checks whether address is a textual octet represented IPv4 address with . or , as octet separator
    """
    
    parts = address.split(".")
    if len(parts) != 4:
        # Also try , as separator before returning False
        parts = address.split(",")
        if len(parts) != 4:
            return False
    for item in parts:
        try:
            val = int(item)
        except ValueError:
            return False
        if not 0 <= val <= 255:
            return False
    return True


def hash(data):
    import hashlib
    # if list....
    d = ''.join(["%s" % el for el in data])    
    return hashlib.md5(d).hexdigest()


def flow_is_valid(flows, flow):
        messages = flows[flow]
        message_indices = messages.keys()
        
        if len(messages)==1: return tuple([True,True]) # Return explicit "everything's ok" for single message flows
        
        if has_gaps(message_indices,1):
            print "ERROR: Flow {0} has gaps in sequences numberings. Skipping flow".format(flow)
            return tuple([False, False]) # return that it has failed has_gaps and is_alternating
        else:
            if Globals.getConfig().flowsMustBeStrictlyAlternating and not is_alternating(flows,flow):
                print "ERROR: Flow {0} is not strictly alternating between client and server. Skippng flow".format(flow)
                return tuple([True, False]) # return that it has passed has_gaps but failed is_alternating
        return tuple([True, True]) # return that is has passed has_gaps and is_alternating
    
def has_gaps(numbers, gap_size):
        # Based on http://stackoverflow.com/questions/4375310/finding-data-gaps-with-bit-masking
        adjacent_differences = [(y - x) for (x, y) in zip(numbers[:-1], numbers[1:])]
        for elem in adjacent_differences:
            if elem>1:
                return True
        return False

def is_alternating(flows, flow):
        if Globals.getConfig().flowsMustBeStrictlyAlternating: return True
        messages = flows[flow]
        direction = ""
        msg_keys = sorted(messages.keys())
        for msg_key in msg_keys:
            direction2 = messages[msg_key][1]
            if direction==direction2: # Current message has same direction as message before
                return False
            direction = direction2
        return True
          