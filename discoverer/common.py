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
    