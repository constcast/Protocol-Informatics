import distance, phylogeny, multialign, output

def pi_core(sequences, weight, graph, textBased):
    #
    # Create distance matrix (LocalAlignment, PairwiseIdentity, Entropic)
    #
    print "Creating distance matrix ..."
    dmx = distance.LocalAlignment(sequences)
    print "complete"

    #
    # Pass distance matrix to phylogenetic creation function
    #
    print "Creating phylogenetic tree ..."
    phylo = phylogeny.UPGMA(sequences, dmx, minval=weight)
    print ""

    #
    # Output some pretty graphs of each cluster
    #
    if graph:
        cnum = 1
        for cluster in phylo:
            out = "graph-%d" % cnum
            print "Creating %s .." % out,
            cluster.graph(out)
            print "complete"
            cnum += 1

    print "\nDiscovered %d clusters using a weight of %.02f" % \
        (len(phylo), weight)

    #
    # Perform progressive multiple alignment against clusters
    #
    i = 1
    alist = []
    for cluster in phylo:
        print "Performing multiple alignment on cluster %d .." % i,
        aligned = multialign.NeedlemanWunsch(cluster)
        print "complete"
        alist.append(aligned)
        i += 1
    print ""

    #
    # Display each cluster of aligned sequences
    #
    i = 1
    for seqs in alist:
        print "Output of cluster %d" % i
        if textBased:
            output.TextBased(seqs)
        else:
            output.Ansi(seqs)
        i += 1
        print ""


