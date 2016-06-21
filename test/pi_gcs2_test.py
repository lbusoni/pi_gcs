#!/usr/bin/env python

import unittest
import numpy as np
from pi_gcs.gcs2 import GeneralCommandSet2, ConnectionError, CHANNEL_ONLINE,\
    CHANNEL_OFFLINE
import ctypes
from ctypes.util import find_library


__version__ = "$Id:$"


class CTypesTest(unittest.TestCase):

    def setUp(self):
        self.libc= ctypes.CDLL(find_library("c"))
        self.libm= ctypes.CDLL(find_library("m"))


    def testEasy(self):
        self.assertEqual(12345, self.libc.atoi("12345"))


    def testReturnDouble(self):
        self.libc.atof.restype= ctypes.c_double
        self.assertEqual(12345.67, self.libc.atof("12345.67"))


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
        res= self.libc.strchr("hello, world", ord('l'))
        self.assertEqual("llo, world", res)


    def testUseArgTypes(self):
        self.libm.floor.argtypes= [ctypes.c_double]
        self.libm.floor.restype= ctypes.c_double
        self.assertEqual(3, self.libm.floor(3.3))


class GeneralCommandSet2Test(unittest.TestCase):

    def setUp(self):
        self._hostname= '193.206.155.117'
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


    #@unittest.skip("missing real hardware")
    def testRaisesIfItCantConnect(self):
        fake= GeneralCommandSet2()
        self.assertRaises(ConnectionError,
                          fake.connectTCPIP, 'foo.bar.com')


    #@unittest.skip("missing real hardware")
    def testAcceptMultipleConnectTCPIPInvocation(self):
        self._acceptMultipleConnectTCPIPInvocation()


    #@unittest.skip("missing real hardware")
    def testControlMode(self):
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


    def testVersion(self):
        self.assertTrue('libpi_pi_gcs2'in self._gcs.getVersion())



if __name__ == "__main__":
    unittest.main()
