#!/bin/bash
set -x

# Performs a batch test for discoverer
#
# Some variables
COPYDIR=ftp_10000
PREFIX=ftp_10000
NUMOFFILES=3
for TESTNUM in `seq 0 $NUMOFFILES`;
do
	
	echo Running batch $TESTNUM
	python main.py
	# Move results away
	cd /home/daubersc/result
	# Create target directory if it does not exist
	if [ ! -d ${COPYDIR}_${TESTNUM} ]; then
		mkdir ${COPYDIR}_${TESTNUM}
	fi
	mv ${PREFIX}_?_testresults.txt ${COPYDIR}_${TESTNUM}
	cd /home/daubersc/Protocol-Informatics
	# Change config file for next rum
	cat config.yml | sed s/10000_$TESTNUM/10000_${TESTNUM+1}/ > config2.yml
	mv config2.yml config.yml
done
