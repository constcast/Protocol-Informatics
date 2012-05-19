#!/bin/bash

# First concat client and server parts by: 'cat client.bro server.bro > allinone.bro
# Then call this script with ./convert_bro_to_testdata allinone.bro

cat $1 | awk {'print $2 " " $3 " " $4 " " $6'} | sort -k 1,2 | awk {'print $1 " " $4'} > $1_test
