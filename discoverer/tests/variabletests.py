'''
Created on 18.03.2012

@author: daubsi
'''
import unittest
from discoverer.formatinference import VariableNumberStatistics
from discoverer.formatinference import VariableTextStatistics

class VariableNumericTest(unittest.TestCase):

    def testVariable(self):
        vns = VariableNumberStatistics()
        vns.addValue(10)
        vns.addValue(10)
        vns.addValue(10)
        vns.addValue(10)
        vns.addValue(0)
        assert vns.getMax()==10
        assert vns.getMin()==0
        assert vns.getMean()==8
        vns.addValue(2)
        vns.addValue(5)
        vns.addValue(7.3)
        vns.addValue(9.2)
        vns.addValue(9.2)
        vns.addValue(2)
        vns.addValue(9.2)
        l = vns.getTop3()
        assert l == [(10,4),(9.2,3),(2,2)]
        assert vns.numberOfSamples()==12
        assert vns.numberOfDistinctSamples()==6
        assert vns.getMax()==10
        assert vns.getMin()==0
        assert vns.getMedian()==6.15
                 
class VariableTextTest(unittest.TestCase):
    
    def testText(self):
        vts = VariableTextStatistics()
        vts.addValue("Hello")
        vts.addValue("World")
        vts.addValue("QUIT")
        vts.addValue("QUIT")
        vts.addValue("QUIT")
        vts.addValue("A very long word")
        vts.addValue("No")
        vts.addValue("Yes!!")
        vts.addValue("USER")
        vts.addValue("USER")
        vts.addValue("USER")
        vts.addValue("USER")
        vts.addValue("Hello")
        assert vts.numberOfSamples()==13
        assert vts.numberOfDistinctSamples()==7
        assert vts.getLongest()=="A very long word"
        assert vts.getShortest()=="No"
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testVariable']
    unittest.main()