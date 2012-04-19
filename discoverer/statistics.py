import Globals

stats = {"printable":0, "binary":0, "startsWithText":0, "numMessages":0}

def update_statistics(num_printable, num_binary, startsWithText):
    stats["printable"] += num_printable
    stats["binary"] += num_binary
    if startsWithText==True:
        stats["startsWithText"] += 1
    stats["numMessages"] += 1

def get_classification():
    """
    Returns an estimated classification of the analyzed protocol.
    A protocol ist considered as "text" if it has at least 2/3 of its messages tokens 
    identified as "text" and at least 90% of all messages begin with a text token
    """
    if stats["printable"]>2*stats["binary"] and stats["startsWithText"]>=0.9*stats["numMessages"]:
        return Globals.protocolText
    else:
        return Globals.protocolBinary
        
def reset_statistics():
    stats = {"printable":0, "binary":0, "startsWithText":0, "numMessages":0}
        
    
 