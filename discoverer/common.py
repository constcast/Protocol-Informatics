def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def is_ipv4(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True