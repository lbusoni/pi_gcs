#!/usr/bin/env python

import unittest
import numpy as np
import time
from pi_gcs.gcs2 import GeneralCommandSet2, PIConnectionError, CHANNEL_ONLINE,\
    CHANNEL_OFFLINE, PIException, WaveformGenerator
import ctypes
from ctypes.util import find_library
from pi_gcs.data_recorder_configuration import DataRecorderConfiguration,\
    RecordOption


__version__ = "$Id:$"


class Barrier:

    @classmethod
    def waitUntil(cls, predicate, timeoutSec, period=0.5, timeModule=time):
        mustEnd = timeModule.time() + timeoutSec

        done= False
        while not done:
            ok= predicate()
            if ok:
                done= True
            elif timeModule.time() >= mustEnd:
                raise Exception("Timeout occurred after %.1f s" %
                                timeoutSec)
            else:
                timeModule.sleep(period)


class CTypesTest(unittest.TestCase):

    def setUp(self):
        self.libc= ctypes.CDLL(find_library("c"))
        self.libm= ctypes.CDLL(find_library("m"))


    def testEasy(self):
        self.assertEqual(12345, self.libc.atoi(b"12345"))


    def testReturnDouble(self):
        self.libc.atof.restype= ctypes.c_double
        self.assertEqual(12345.67, self.libc.atof(b"12345.67"))


    def testPassingIntPerReference(self):
        sign= ctypes.c_int()
        self.libm.lgamma_r(ctypes.c_double(14.5),
                           ctypes.byref(sign))
        self.assertEqual(1, sign.value)


    def testArgDoubleResDouble(self):
        self.libm.lgamma.restype= ctypes.c_double
        self.assertAlmostEqual(23.86276584168909,
                               self.libm.lgamma(ctypes.c_double(14.5)))


    def testFromParamWithDouble(self):
        class DoubleArg():
            def __init__(self, value):
                self._value= value

            def from_param(self):
                return ctypes.c_double(self._value)

        arg= DoubleArg(14.5)
        self.libm.lgamma.argtypes= [DoubleArg]
        self.libm.lgamma.restype= ctypes.c_double
        self.assertAlmostEqual(23.86276584168909,
                               self.libm.lgamma(arg))


    def testArgsUInt16Array(self):
        xsubi1= (ctypes.c_uint16 * 3)(1, 2, 3)
        xsubi2= (ctypes.c_uint16 * 3)(1, 2, 3)
        ret1= self.libc.nrand48(xsubi1)
        ret2= self.libc.nrand48(xsubi2)
        self.assertEqual(ret1, ret2)


    def testFromParamWithUInt16Array(self):
        class UInt16ArrayArg():
            def __init__(self, value):
                self._ret= (ctypes.c_uint16 * len(value))()
                for i in range(len(value)):
                    self._ret[i]= value[i]

            def from_param(self):
                return self._ret

            def array(self):
                return np.array([x for x in self._ret])


        xsubi1= UInt16ArrayArg([1, 2, 4092])
        self.assertTrue(np.allclose(np.array([1, 2, 4092]),
                                    xsubi1.array()))
        xsubi2= UInt16ArrayArg([1, 2, 4092])
        self.libc.nrand48.argtypes= [UInt16ArrayArg]
        ret1= self.libc.nrand48(xsubi1)
        ret2= self.libc.nrand48(xsubi2)
        self.assertEqual(ret1, ret2)
        self.assertFalse(np.allclose(np.array([1, 2, 4092]),
                                     xsubi1.array()))


    def testArgsConstCharPtrResCharPtr(self):
        self.libc.strchr.restype= ctypes.c_char_p
        self.libc.strchr.argtypes= [ctypes.c_char_p, ctypes.c_int]
        res= self.libc.strchr(b"hello, world", ord('l'))
        self.assertEqual(b"llo, world", res)


    def testUseArgTypes(self):
        self.libm.floor.argtypes= [ctypes.c_double]
        self.libm.floor.restype= ctypes.c_double
        self.assertEqual(3, self.libm.floor(3.3))


class GeneralCommandSet2TestWithE517(unittest.TestCase):

    def setUp(self):
        self._hostname= '192.168.29.117'
        self._gcs= GeneralCommandSet2()
        self._gcs.connectTCPIP(self._hostname)


    def tearDown(self):
        self._gcs.closeConnection()


    def _acceptMultipleConnectTCPIPInvocation(self):
        #self._gcs.connectTCPIP(self._hostname)
        pass


    @unittest.skip("not implemented in e518. cannot test it")
    def testEcho(self):
        self.assertEqual("pippo",
                         self._gcs.echo("pippo"))


    def _testRaisesIfItCantConnect(self):
        fake= GeneralCommandSet2()
        self.assertRaises(PIConnectionError,
                          fake.connectTCPIP, 'foo.bar.com')


    def _enableControlMode(self):
        channels= np.array([1, 2, 3])
        self._gcs.setControlMode(
            channels,
            [CHANNEL_OFFLINE, CHANNEL_OFFLINE, CHANNEL_ONLINE])
        controlMode= self._gcs.getControlMode(channels)
        self.assertTrue(
            np.allclose(
                np.array([CHANNEL_OFFLINE, CHANNEL_OFFLINE, CHANNEL_ONLINE]),
                controlMode))

        self._gcs.enableControlMode(channels)
        controlMode= self._gcs.getControlMode(channels)
        self.assertTrue(
            np.allclose(
                np.array([CHANNEL_ONLINE, CHANNEL_ONLINE, CHANNEL_ONLINE]),
                controlMode))

        self._gcs.disableControlMode([2])
        controlMode= self._gcs.getControlMode(channels)
        self.assertTrue(
            np.allclose(
                np.array([CHANNEL_ONLINE, CHANNEL_OFFLINE, CHANNEL_ONLINE]),
                controlMode))

        self._gcs.enableControlMode([1, 2, 3])



    def _enableServoControlMode(self):
        self._gcs.setServoControlMode("A B C", [False, False, False])
        self.assertTrue(
            np.allclose(
                np.array([False, False, False]),
                self._gcs.getServoControlMode("A B C")))

        self._gcs.setServoControlMode("A", True)
        self.assertTrue(
            np.allclose(
                np.array([True]),
                self._gcs.getServoControlMode("A")))

        self._gcs.setServoControlMode("A B C", [True, True, False])
        self.assertTrue(
            np.allclose(
                np.array([True, True, False]),
                self._gcs.getServoControlMode("A B C")))


    def _testVersion(self):
        self.assertTrue('libpi_pi_gcs2' in self._gcs.getVersion())


    def _testGcsCommand(self):
        self.assertEqual(self._gcs.gcsCommand('VER?'),
                         self._gcs.getVersion())


    def _queryConfiguration(self):
        self.assertItemsEqual(['A', 'B', 'C'],
                              self._gcs.getAxesIdentifiers())
        self.assertEqual(3, self._gcs.getNumberOfInputSignalChannels())
        self.assertEqual(3, self._gcs.getNumberOfOutputSignalChannels())


    def _setVoltageLimits(self):
        self._gcs.setLowerVoltageLimit([1, 2, 3], [20, 10, 10])
        self.assertItemsEqual([20, 10, 10],
                              self._gcs.getLowerVoltageLimit([1, 2, 3]))
        self._gcs.setLowerVoltageLimit([1, 2, 3], [10, 10, 10])
        self.assertItemsEqual([10, 10, 10],
                              self._gcs.getLowerVoltageLimit([1, 2, 3]))
        self._gcs.setUpperVoltageLimit([1, 2, 3], [95.5, 98, 100])
        self.assertItemsEqual([95.5, 98, 100],
                              self._gcs.getUpperVoltageLimit([1, 2, 3]))

        self._gcs.setLowerVoltageLimit([1, 2, 3], [10, 10, 10])
        self._gcs.setUpperVoltageLimit([1, 2, 3], [100, 100, 100])


    def _getPosition(self):
        pos= self._gcs.getPosition('A B C')
        self.assertEqual(3, len(pos))
        vol= self._gcs.getVoltages([1, 2, 3])
        self.assertEqual(3, len(vol))


    def _setOpenLoopAxisValue(self):
        self._gcs.setOpenLoopAxisValue('a b c', [50, 50, 90])
        self.assertItemsEqual([50, 50, 90],
                              self._gcs.getOpenLoopAxisValue('a b c'))
        self._gcs.setRelativeOpenLoopAxisValue('a', -10)
        self.assertItemsEqual([40, 50, 90],
                              self._gcs.getOpenLoopAxisValue('a b c'))
        self._gcs.setOpenLoopAxisValue('a b c', [50, 50, 90])



    def _resetE517ToSafe(self):
        self._gcs.enableControlMode([1, 2, 3])
        self._gcs.setServoControlMode('a b c', [False, False, False])
        self._gcs.setLowerVoltageLimit([1, 2, 3], [10, 10, 10])
        self._gcs.setUpperVoltageLimit([1, 2, 3], [100, 100, 100])


    @unittest.skip("skipped")
    def testGCSWithE517(self):
        self._acceptMultipleConnectTCPIPInvocation()
        self._testRaisesIfItCantConnect()
        self._testVersion()
        self._queryConfiguration()
        self._testGcsCommand()
        self._resetE517ToSafe()
        self._enableControlMode()
        self._setVoltageLimits()
        self._setOpenLoopAxisValue()
        self._enableServoControlMode()
        self._getPosition()
        self._resetE517ToSafe()


    def _checkVoltages(self, channels, wanted, delta=0):
        def pippo():
            return np.allclose(np.atleast_1d(wanted),
                               self._gcs.getVoltages(channels),
                               atol=delta)

        Barrier.waitUntil(pippo, timeoutSec=3, period=0.1)


    def _checkPositions(self, axes, wanted, delta=0):
        def pippo():
            return np.allclose(np.atleast_1d(wanted),
                               self._gcs.getPosition(axes),
                               atol=delta)

        Barrier.waitUntil(pippo, timeoutSec=3, period=0.1)



    @unittest.skip("skipped")
    def testExample1(self):
        self._resetE517ToSafe()
        self._gcs.enableControlMode([1])
        self.assertEqual(False, self._gcs.getServoControlMode('a'))
        self._gcs.setOpenLoopAxisValue("a", 80)
        self._checkVoltages(1, 80, delta=20)
        self.assertRaises(PIException,
                          self._gcs.setOpenLoopAxisValue, "a", 150)
        self._checkVoltages(1, 80, delta=20)
        self.assertEqual(80, self._gcs.getOpenLoopAxisValue("a"))
        self.assertEqual(100, self._gcs.getUpperVoltageLimit(1))
        self._gcs.setUpperVoltageLimit([1], 90)
        self._gcs.setLowerVoltageLimit([1], 10)
        self._gcs.setOpenLoopAxisValue("a", 85)
        self._checkVoltages(1, 85, delta=20)
        self.assertRaises(PIException,
                          self._gcs.setOpenLoopAxisValue, "a", 100)
        self._checkVoltages(1, 85, delta=20)
        self.assertEqual(85, self._gcs.getOpenLoopAxisValue("a"))
        self._gcs.setUpperVoltageLimit([1], 100)
        self._gcs.setOpenLoopAxisValue("a", 100)
        self.assertEqual(100, self._gcs.getOpenLoopAxisValue("a"))
        self._checkVoltages(1, 100, delta=20)
        self._checkPositions("a", 100, delta=20)
        self._gcs.setRelativeOpenLoopAxisValue("a", -20)
        self._checkVoltages(1, 80, delta=20)
        self._checkPositions("a", 80, delta=20)
        self._resetE517ToSafe()



    @unittest.skip("skipped")
    def testExample2(self):
        self._resetE517ToSafe()
        self._gcs.enableControlMode([1, 2, 3])
        self._gcs.setServoControlMode("a b c", [True, True, False])
        #DCO
        self._gcs.setTargetPosition("a", 30.5)
        self._checkPositions("a", 30.5, delta=1)
        self._gcs.setTargetPosition("b", 80)
        self._checkPositions("a b", [30.5, 80], delta=1)
        self._gcs.setTargetRelativeToCurrentPosition("a b", [-2, 3])
        self._checkPositions("a b", [28.5, 83], delta=1)
        self._resetE517ToSafe()


    def testRecorder(self):
        self._resetE517ToSafe()
        print("%s" % self._gcs.getAllDataRecorderOptions())
        originalCfg= self._gcs.getDataRecorderConfiguration()

        nRecorders= self._gcs.getNumberOfRecorderTables()
        self.assertEqual(8, nRecorders)

        dataRecorderCfg= DataRecorderConfiguration()
        dataRecorderCfg.setTable(1, "A", RecordOption.REAL_POSITION_OF_AXIS)
        dataRecorderCfg.setTable(2, "B", RecordOption.REAL_POSITION_OF_AXIS)
        dataRecorderCfg.setTable(3, "1", RecordOption.VOLTAGE_OF_PIEZO_CHANNEL)
        self._gcs.setDataRecorderConfiguration(dataRecorderCfg)
        retrievedCfg= self._gcs.getDataRecorderConfiguration()
        self.assertEqual(RecordOption.REAL_POSITION_OF_AXIS,
                         retrievedCfg.getRecordOption(1))
        self.assertEqual(RecordOption.REAL_POSITION_OF_AXIS,
                         retrievedCfg.getRecordOption(2))
        self.assertEqual(RecordOption.VOLTAGE_OF_PIEZO_CHANNEL,
                         retrievedCfg.getRecordOption(3))
        self.assertEqual("A", retrievedCfg.getRecordSource(1))
        self.assertEqual("B", retrievedCfg.getRecordSource(2))
        self.assertEqual("1", retrievedCfg.getRecordSource(3))


        startFromPoint= 1
        howMany= 10
        self._gcs.startRecordingInSyncWithWaveGenerator()
        record= self._gcs.getRecordedDataValues(howMany, startFromPoint)
        self.assertEqual((nRecorders, howMany), record.shape)

        self._gcs.setDataRecorderConfiguration(originalCfg)
        self._resetE517ToSafe()


    def testWaveGenerator(self):
        self._resetE517ToSafe()
        self.assertEqual(3, self._gcs.getNumberOfWaveGenerators())
        self._gcs.setConnectionOfWaveTableToWaveGenerator(
            [1, 2, 3], [3, 1, 2])
        self.assertTrue(
            np.allclose(
                [3, 1, 2],
                self._gcs.getConnectionOfWaveTableToWaveGenerator([1, 2, 3])))

        self._gcs.setWaveGeneratorStartStopMode([0, 0, 0])
        res= self._gcs.getWaveGeneratorStartStopMode()
        self.assertEqual(0, res[0])
        self.assertEqual(0, res[1])
        self.assertEqual(0, res[2])

        lengthInPoints= 1000
        amplitudeOfTheSineCurve= 10.
        offsetOfTheSineCurve= 45.
        wavelengthOfTheSineCurveInPoints= 1000
        startPoint= 0
        curveCenterPoint= 500
        self._gcs.setSinusoidalWaveform(
            1, WaveformGenerator.CLEAR, lengthInPoints,
            amplitudeOfTheSineCurve, offsetOfTheSineCurve,
            wavelengthOfTheSineCurveInPoints, startPoint, curveCenterPoint)
        self._gcs.setConnectionOfWaveTableToWaveGenerator([1, 2, 3], [1, 2, 3])

        self._gcs.setWaveGeneratorStartStopMode([1, 0, 0])
        res= self._gcs.getWaveGeneratorStartStopMode()
        self.assertEqual(1, res[0])
        self.assertEqual(0, res[1])
        self.assertEqual(0, res[2])

        self._gcs.setWaveGeneratorStartStopMode([0, 0, 0])
        self._gcs.clearWaveTableData([1, 2, 3])
        self._resetE517ToSafe()


if __name__ == "__main__":
    unittest.main()
