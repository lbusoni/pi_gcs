#!/usr/bin/env python
import unittest
from pi_gcs.gcs2 import GeneralCommandSet2,\
    ConnectionError

__version__ = "$Id:$"


class GeneralCommandSet2Test(unittest.TestCase):

    def setUp(self):
        self._hostname= '193.206.155.117'
        self._pigcs= GeneralCommandSet2()


    def tearDown(self):
        self._pigcs.closeConnection()


    def _acceptMultipleConnectTCPIPInvocation(self):
        self._pigcs.connectTCPIP(self._hostname)
        self._pigcs.connectTCPIP(self._hostname)


    def testRaisesIfItCantConnect(self):
        fake= GeneralCommandSet2()
        self.assertRaises(ConnectionError,
                          fake.connectTCPIP, 'foo.bar.com')


    def test(self):
        self._acceptMultipleConnectTCPIPInvocation()



if __name__ == "__main__":
    unittest.main()
