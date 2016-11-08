import unittest
import numpy as np
from pi_gcs.tip_tilt_2_axes import TipTilt2Axis
from pi_gcs.fake_gcs2 import FakeGeneralCommandSet
from pi_gcs.tip_tilt_configuration import TipTiltConfiguration


class TipTilt2AxisTest(unittest.TestCase):


    def setUp(self):
        self._ctrl= FakeGeneralCommandSet()
        self._cfg= TipTiltConfiguration()
        self._tt= TipTilt2Axis(self._ctrl, self._cfg)
        self._tt.setUp()


    def testVoltageLimitsAreSetAtStartUp(self):
        wanted= self._cfg.lowerVoltageLimit
        actual= self._ctrl.getLowerVoltageLimit(self._tt.ALL_CHANNELS)
        self.assertTrue(
            np.alltrue(wanted == actual),
            "%s %s" % (wanted, actual))

        wanted= self._cfg.upperVoltageLimit
        actual= self._ctrl.getUpperVoltageLimit(self._tt.ALL_CHANNELS)
        self.assertTrue(
            np.alltrue(wanted == actual),
            "%s %s" % (wanted, actual))


    def test3rdAxisIsSetAsPivotAtStartUp(self):
        pivot= self._ctrl.getAxesIdentifiers()[2]
        wanted= self._cfg.pivotValue
        actual= self._ctrl.getOpenLoopAxisValue(pivot)
        self.assertTrue(
            np.alltrue(wanted == actual),
            "%s %s" % (wanted, actual))


    def testSetGetAxesInClosedLoop(self):
        self._tt.enableControlLoop()
        self.assertTrue(self._tt.isControlLoopEnabled())
        self._tt.disableControlLoop()
        self.assertFalse(self._tt.isControlLoopEnabled())


    def testSetGetTargetPosition(self):
        self._tt.setTargetPosition([2.5, 5])
        self.assertTrue(
            np.allclose([2.5, 5], self._tt.getTargetPosition()))


    def testStartStopModulation(self):
        self._tt.startModulation(10., 100., [44, 55])
        self.assertTrue(
            np.allclose(
                [1, 1, 0],
                self._ctrl.getWaveGeneratorStartStopMode()))
        self._tt.stopModulation()
        self.assertTrue(
            np.allclose([44, 55], self._tt.getTargetPosition()))


    def testRecordingData(self):
        howManySamples= 100
        nRecorderTables= self._ctrl.getNumberOfRecorderTables()
        cntr= self._ctrl.triggerStartRecordingInSyncWithWaveGenerator

        recData= self._tt.getRecordedData(howManySamples)
        self.assertEqual((nRecorderTables + 1, howManySamples), recData.shape)
        self.assertEqual(
            cntr + 1,
            self._ctrl.triggerStartRecordingInSyncWithWaveGenerator)

if __name__ == "__main__":
    unittest.main()
