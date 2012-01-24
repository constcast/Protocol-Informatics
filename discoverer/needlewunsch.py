# This code has been taken from
# http://www.weigelworld.org/Members/shenz/lectures/ws-2008-2009/vorlesung-mit-ubungen-bioinformatik/ubungsblatter/Needleman-Wunsch.py/view
# and adapted to work with lists of tuples instead of pure chars


#
# Vorlesung "Vorlesung mit \"Ubungen: Bioinformatik
#
# 4. \"Ubung -- Needleman-Wunsch.py
#
#

# Einbinden der Matrixklasse aus dem Numeric-Modul
#import Numeric
#import numarray as Numeric
import numpy as Numeric

# Eine einfache Distanzfunktion: Z\"ahlen der Mismatches.
def d(a,b): 
    if a == b:
        return 0
    else:
        return 1

def needlewunsch(seqA, seqB):
    # Die zu alignierenden Sequenzen.
    A = seqA
    B = seqB
    
    # Die L\"angen der Sequenzen
    m = len(A)
    n = len(B)
    
    # Initialisiere die DP-Matrix und die Traceback-Matrix.
    # Beide haben Dimension (m+1)x(n+1)
    D = Numeric.zeros([m+1, n+1])
    T = Numeric.zeros([m+1, n+1])
    
    # Initialisiere die erste Zeile und erste Spalte
    # der beiden Matrizen.
    # ''vertikal" bekommt ''-1'', horizontal bekommt ''1''
    for i in range(m+1):
        D[i, 0] = i * d("-", "A")
    for j in range(n+1):
        D[0, j] = j * d("-", "A")
    for i in range(m+1):
        T[i,0] = -1 
    for j in range(n+1):
        T[0,j] =  1
    
    # Dynamische Programmierung: f\"ulle DP-Matrix.
    for i in range(1,m+1):
        for j in range(1,n+1):
            # Berechne Distanzen
            d_horiz = D[i-1,j] + d(A[i-1],"-")
            d_diag  = D[i-1,j-1] + d(A[i-1],B[j-1])
            d_vert  = D[i,j-1] + d("-", B[j-1])

            # Speichere Minimum in DP-Matrix D
            D[i,j] = min([d_horiz, d_diag, d_vert])

            # Merke Richtung in Traceback-Matrix T
            if d_diag <= d_horiz and d_diag <= d_vert:
                T[i,j] = 0
            elif d_horiz <= d_vert:
                T[i,j] = -1
            else:
                T[i,j] = +1


    # Die alignierten Strings (mit Gaps)
    # nennen wir X und Y (A', B' sind keine
    # zu\"assigen Variablennamen).
    X = []
    Y = []
    
    # Traceback: beginne in der unteren rechten
    # Zelle der Matrix und laufe solange bis oben
    # links angekommen.
    i = m
    j = n
    while i > 0 or j > 0:
        if T[i,j] == 0:   # diagonal: keine Gaps
            #===================================================================
            # X.insert(0,A[i-1])
            # Y.insert(0,B[j-1])
            # (i,j) = (i-1, j-1)
            #======================
            X.insert(0,"*")
            Y.insert(0,"*")
            (i,j) = (i-1,j-1)  
            
            
            
            #===================================================================
            # X.insert(0,A[i-1])
            # Y.insert(0,B[j-1])
            # 
            #===================================================================
            X.insert(0,"*")
            Y.insert(0,"*")
            
            (i,j) = (i-1, j-1)
        elif T[i,j] == -1: # nach links (horizontal): Gap in B
            #X.insert(0,A[i-1])
            #Y.insert(0,"GAP")
            
            X.insert(0,"*")
            Y.insert(0,"_")
            
            #X.insert(0,A[i-1])
            #Y.insert(0,"GAP")
            
            X.insert(0,"*")
            Y.insert(0,"_")
            i = i - 1
        else:              # nach oben (vertical): Gap in A            
            #X.insert(0,"GAP")
            #Y.insert(0,B[j-1])
            
            X.insert(0,"_")
            Y.insert(0,"*")
            j = j -1
    
    # Gib das Alignment aus.
    print X
    print Y
