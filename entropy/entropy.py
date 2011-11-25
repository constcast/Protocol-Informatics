# vim: set sts=4 sw=4 cindent nowrap expandtab:

import sys

def entropy_core(sequences, gnuplotFile):
    byte_sequences = []
    for i in sequences:
        byte_sequences.append(i[1])

    longest_sequence =  len(max(byte_sequences, key=len))

    fileDesc = sys.stdout
    if gnuplotFile:
        fileDesc = file(gnuplotFile, 'w+')

    byte_vectors = []
    for i in range(longest_sequence):
        byte_vectors.append([])

    # loop over all sequences and record byte frequencies
    for i in byte_sequences:
        byteNum = 0
        for symbol in i:
            byte_vectors[byteNum].append(symbol)
            byteNum += 1


    # calculate entropy
    entropy_vector = []
    bytenum = 1
    for byteseq in byte_vectors:
        seqlen = len(byteseq)
        uniqbytes = set(byteseq)
        entropy = float(len(uniqbytes)) /  float(seqlen)
        fileDesc.write("%d %f %d %d\n" % (bytenum, entropy, len(uniqbytes), seqlen))
        byteNum += 1

