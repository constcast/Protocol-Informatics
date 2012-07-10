#!/bin/bash
set -x

# Performs a batch test for discoverer
#
# Some variables
COPYDIR=dns_1000
PREFIX=dns_1000
FULLPATH=/home/daubersc/result/
NUMOFFILES=90
CONFIGFILE=config_dns_1000.yml
for TESTNUM in `seq 0 $NUMOFFILES`;
do
	
	echo Running batch $TESTNUM
	python main.py -c ${CONFIGFILE}
	# Move results away
	cd /home/daubersc/result
	# Create target directory if it does not exist
	if [ ! -d ${COPYDIR}_${TESTNUM} ]; then
		mkdir ${COPYDIR}_${TESTNUM}
	fi
	for TESTNUMIDX in `seq 0 $NUMOFFILES`;
	do
		mv ${PREFIX}_${TESTNUMIDX}_testresults.txt ${COPYDIR}_${TESTNUM}
	done
	cd /home/daubersc/Protocol-Informatics
	# Change config file for next rum
	cat ${CONFIGFILE} | sed "s§inputFile: ${FULLPATH}${PREFIX}_$TESTNUM§inputFile: ${FULLPATH}${PREFIX}_$[TESTNUM+1]§" > config2.yml
	mv config2.yml ${CONFIGFILE} 
done
