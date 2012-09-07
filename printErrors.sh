#!/bin/bash
NUM=9; BASE=dns_2000; for X in `seq 0 $[NUM-1]`; do { cd dns_${X}; ANZ=`ls | wc -l`; for IDX in `seq 0 $[ANZ-1]`; do { head -n 3 ${BASE}_${IDX}_testresults.txt | tail -n 1 | awk '{printf "%s & ",$8;} '; } done; echo; cd ..; } done



NUM=91; BASE=dns_1000; for X in `seq 0 $[NUM-1]`; do { cd ${BASE}_${X}; ANZ=`ls | wc -l`; echo -n dns\\_${X}\ \&\ ; for IDX in `seq 0 $[ANZ-1]`; do { head -n 3 ${BASE}_${IDX}_testresults.txt | tail -n 1 | awk '{printf "%s & ",$8;} '; } done; echo; cd ..; } done
