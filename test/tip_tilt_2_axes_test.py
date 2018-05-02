import unittest
import numpy as np
from pi_gcs.tip_tilt_2_axes import TipTilt2Axis
from pi_gcs.fake_gcs2 import FakeGeneralCommandSet
from pi_gcs.tip_tilt_configuration import TipTiltConfiguration
from pi_gcs.gcs2 import PIException


class TipTilt2AxisTest(unittest.TestCase):


    def setUp(self):
        self._ctrl= FakeGeneralCommandSet()
        self._createConfiguration()
        self._tt= TipTilt2Axis(self._ctrl, self._cfg)
        self._tt.setUp()


    def _createConfiguration(self):
        self._cfg= TipTiltConfiguration()
        self._posToMilliRadALinear= 12.2
        self._posToMilliRadAOffset= -123.
        self._posToMilliRadBLinear= 33e-3
        self._posToMilliRadBOffset= 4.4
        self._cfg.positionToMilliRadAxisALinearCoeff= \
            self._posToMilliRadALinear
        self._cfg.positionToMilliRadAxisAOffsetCoeff= \
            self._posToMilliRadAOffset
        self._cfg.positionToMilliRadAxisBLinearCoeff= \
            self._posToMilliRadBLinear
        self._cfg.positionToMilliRadAxisBOffsetCoeff= \
            self._posToMilliRadBOffset


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


    def _savePlot(self, data, filename):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        plt.plot(data)
        plt.savefig(filename)


    def testStartStopSinusoidalModulation(self):
        radiiInMilliRad= [12.4, 14]
        frequencyInHz= 100.
        centerInMilliRad= [-10, 15]
        phasesInRadians= [0, np.pi/ 2]
        self._tt.setTargetPosition(centerInMilliRad)
        self._tt.startSinusoidalModulation(radiiInMilliRad,
                                           frequencyInHz,
                                           phasesInRadians,
                                           centerInMilliRad)
        self.assertTrue(
            np.allclose(
                [1, 1, 0],
                self._ctrl.getWaveGeneratorStartStopMode()))
        waveform= self._ctrl.getWaveform(1)
        wants= self._tt._milliRadToGcsUnitsOneAxis(-10, self._tt.AXIS_A)
        got= np.mean(waveform)
        self.assertAlmostEqual(
            wants, got, msg="wants %g, got %g" % (wants, got))
        wants= self._tt._milliRadToGcsUnitsOneAxis(-10 + 12.4, self._tt.AXIS_A)
        got= np.max(waveform)
        self.assertAlmostEqual(
            wants, got, msg="wants %g, got %g" % (wants, got))

        waveform= self._ctrl.getWaveform(2)
        wants= self._tt._milliRadToGcsUnitsOneAxis(15, self._tt.AXIS_B)
        got= np.mean(waveform)
        self.assertAlmostEqual(
            wants, got, msg="wants %g, got %g" % (wants, got))
        wants= self._tt._milliRadToGcsUnitsOneAxis(15 + 14, self._tt.AXIS_B)
        got= np.max(waveform)
        self.assertAlmostEqual(
            wants, got, msg="wants %g, got %g" % (wants, got))

        self._tt.stopModulation()
        self.assertTrue(
            np.allclose(centerInMilliRad, self._tt.getTargetPosition()))


    def testRecordingData(self):
        self._tt.startFreeformModulation(np.arange(10),
                                         np.arange(10))

        howManySamples= 100
        nRecorderTables= self._ctrl.getNumberOfRecorderTables()
        cntr= self._ctrl.triggerStartRecordingInSyncWithWaveGenerator

        recData= self._tt.getRecordedData(howManySamples)
        self.assertEqual((nRecorderTables + 1, howManySamples), recData.shape)
        self.assertEqual(
            cntr + 1,
            self._ctrl.triggerStartRecordingInSyncWithWaveGenerator)


    def testConvertFromGCSUnitToMilliRad(self):
        gcsX= 12.5
        gcsY= -23.5
        self._ctrl.setTargetPosition(self._tt.ALL_AXES, np.array([gcsX, gcsY]))

        mRadA= self._tt.getPosition()[0]
        mRadB= self._tt.getPosition()[1]

        wantA= gcsX * self._posToMilliRadALinear + self._posToMilliRadAOffset
        wantB= gcsY * self._posToMilliRadBLinear + self._posToMilliRadBOffset

        self.assertEqual(wantA, mRadA, "wanted %s got %s" % (wantA, mRadA))
        self.assertEqual(wantB, mRadB, "wanted %s got %s" % (wantB, mRadB))

        mRadA= self._tt.getTargetPosition()[0]
        mRadB= self._tt.getTargetPosition()[1]

        self.assertEqual(wantA, mRadA, "wanted %s got %s" % (wantA, mRadA))
        self.assertEqual(wantB, mRadB, "wanted %s got %s" % (wantB, mRadB))



    def testStartStopFreeformModulation(self):
        centerInMilliRad= [-10, 15]
        nPoints= 1000

        axisATrajectoryInMilliRad= np.linspace(-10, 2, num=nPoints)
        axisBTrajectoryInMilliRad= np.linspace(15, 5, num=nPoints)
        self._tt.setTargetPosition(centerInMilliRad)
        self._tt.startFreeformModulation(axisATrajectoryInMilliRad,
                                         axisBTrajectoryInMilliRad)

        self.assertTrue(
            np.allclose(
                [1, 1, 0],
                self._ctrl.getWaveGeneratorStartStopMode()))
        waveform= self._ctrl.getWaveform(1)
        wants= self._tt._milliRadToGcsUnitsOneAxis(-4, self._tt.AXIS_A)
        got= np.mean(waveform)
        self.assertAlmostEqual(
            wants, got, msg="wants %g, got %g" % (wants, got))
        wants= self._tt._milliRadToGcsUnitsOneAxis(2, self._tt.AXIS_A)
        got= np.max(waveform)
        self.assertAlmostEqual(
            wants, got, msg="wants %g, got %g" % (wants, got))

        waveform= self._ctrl.getWaveform(2)
        wants= self._tt._milliRadToGcsUnitsOneAxis(10, self._tt.AXIS_B)
        got= np.mean(waveform)
        self.assertAlmostEqual(
            wants, got, msg="wants %g, got %g" % (wants, got))
        wants= self._tt._milliRadToGcsUnitsOneAxis(15, self._tt.AXIS_B)
        got= np.max(waveform)
        self.assertAlmostEqual(
            wants, got, msg="wants %g, got %g" % (wants, got))

        self._tt.stopModulation()
        self.assertTrue(
            np.allclose(centerInMilliRad, self._tt.getTargetPosition()))


    def testGetRecordedDataTimeStep(self):
        ts= self._tt.getRecordedDataTimeStep()
        self.assertEqual(40e-6, ts)


    def testSetOpenLoopValue(self):
        self._tt.stopModulation()
        self._tt.disableControlLoop()
        self._tt.setOpenLoopValue([50, 60])
        self.assertTrue(
            np.allclose([50, 60], self._tt.getOpenLoopValue()))


    def testSetOpenLoopValueRaisesIfInClosedLoop(self):
        self._tt.stopModulation()
        self._tt.enableControlLoop()
        self.assertRaises(PIException, self._tt.setOpenLoopValue, [50, 60])



if __name__ == "__main__":
    unittest.main()
