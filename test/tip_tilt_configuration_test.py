#!/usr/bin/env python
import unittest
from pi_gcs.tip_tilt_configuration import TipTiltConfiguration

__version__ = "$Id:$"


class TipTiltConfigurationTest(unittest.TestCase):


    def setUp(self):
        self._cfg= TipTiltConfiguration()


    def testHappyCreation(self):
        hostname= 'asdf'
        posToMilliRadALinear= 12.2
        posToMilliRadAOffset= -123
        posToMilliRadBLinear= 33e-3
        posToMilliRadBOffset= 4.4
        self._cfg.hostname= hostname
        self._cfg.positionToMilliRadAxisALinearCoeff= posToMilliRadALinear
        self._cfg.positionToMilliRadAxisAOffsetCoeff= posToMilliRadAOffset
        self._cfg.positionToMilliRadAxisBLinearCoeff= posToMilliRadBLinear
        self._cfg.positionToMilliRadAxisBOffsetCoeff= posToMilliRadBOffset

        self.assertEqual(hostname, self._cfg.hostname)
        self.assertEqual(posToMilliRadALinear,
                         self._cfg.positionToMilliRadAxisALinearCoeff)
        self.assertEqual(posToMilliRadAOffset,
                         self._cfg.positionToMilliRadAxisAOffsetCoeff)
        self.assertEqual(posToMilliRadBLinear,
                         self._cfg.positionToMilliRadAxisBLinearCoeff)
        self.assertEqual(posToMilliRadBOffset,
                         self._cfg.positionToMilliRadAxisBOffsetCoeff)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()