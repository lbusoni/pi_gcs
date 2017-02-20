#!/usr/bin/env python
import unittest
import numpy as np
from pi_gcs.fake_gcs2 import FakeGeneralCommandSet
from pi_gcs.gcs2 import WaveformGenerator

__version__ = "$Id:$"


class FakeGeneralCommandSetTest(unittest.TestCase):


    def setUp(self):
        self._ctrl= FakeGeneralCommandSet()


    def testSinusoidalWaveform(self):
        waveTableId= 1
        radiusInMilliRad= 12.5
        frequencyInHz= 100
        centerInMilliRad= -10

        timestep= 40e-6
        periodInSec= 1./ frequencyInHz
        lengthInPoints= periodInSec/ timestep
        amplitudeOfTheSineCurve= 2* radiusInMilliRad
        offsetOfTheSineCurve= centerInMilliRad - \
            0.5 * amplitudeOfTheSineCurve
        wavelengthOfTheSineCurveInPoints= periodInSec/ timestep
        startPoint= 0
        curveCenterPoint= 0.5* wavelengthOfTheSineCurveInPoints

        self._ctrl.setSinusoidalWaveform(
            waveTableId, WaveformGenerator.CLEAR, lengthInPoints,
            amplitudeOfTheSineCurve, offsetOfTheSineCurve,
            wavelengthOfTheSineCurveInPoints, startPoint, curveCenterPoint)

        waveform= self._ctrl.getWaveform(waveTableId)
        self.assertAlmostEqual(wavelengthOfTheSineCurveInPoints, len(waveform))


    def testSinusoidalWaveformEasy(self):
        waveTableId= 1
        lengthInPoints= 100
        amplitudeOfTheSineCurve= 120
        offsetOfTheSineCurve= -5
        wavelengthOfTheSineCurveInPoints= 70
        startPoint= 10
        curveCenterPoint= 40
        self._ctrl.setSinusoidalWaveform(
            waveTableId, WaveformGenerator.CLEAR, lengthInPoints,
            amplitudeOfTheSineCurve, offsetOfTheSineCurve,
            wavelengthOfTheSineCurveInPoints, startPoint, curveCenterPoint)

        waveform= self._ctrl.getWaveform(waveTableId)
        self.assertEqual(lengthInPoints, len(waveform))
        self.assertEqual(offsetOfTheSineCurve, waveform[0])
        self.assertEqual(offsetOfTheSineCurve, waveform[startPoint- 1])
        self.assertEqual(offsetOfTheSineCurve, waveform[-1])
        self.assertEqual(
            offsetOfTheSineCurve,
            waveform[startPoint+ wavelengthOfTheSineCurveInPoints])
        self.assertEqual(
            offsetOfTheSineCurve + amplitudeOfTheSineCurve,
            waveform[startPoint+ curveCenterPoint])
        self.assertEqual(
            offsetOfTheSineCurve + 0.5* amplitudeOfTheSineCurve,
            waveform[int(startPoint+ 0.5* curveCenterPoint)])
        self.assertEqual(
            offsetOfTheSineCurve + 0.5* amplitudeOfTheSineCurve,
            waveform[int(startPoint+ 0.5*
                     (curveCenterPoint + wavelengthOfTheSineCurveInPoints))])


    def testTargetPosition(self):
        target= [12, 34]
        self._ctrl.setTargetPosition('P F', target)
        self.assertEqual(12, self._ctrl.getTargetPosition('P'))
        self.assertEqual(34, self._ctrl.getTargetPosition('F'))
        self.assertTrue(np.allclose(target,
                                    self._ctrl.getTargetPosition('P F')))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()