#!/usr/bin/env python
import unittest
from pi_gcs.pi_e518 import PhysikInstrumenteE518

__version__ = "$Id:$"


class PhysikInstrumenteE518Test(unittest.TestCase):


    def setUp(self):
        hostname= 'host.name.org'
        self.pi518= PhysikInstrumenteE518(hostname)


    def tearDown(self):
        pass


    @unittest.skip("skipped")
    def testFoo(self):
        self.pi518.connectTCPIP()
        self.assertEqual('foo',
                         self.pi518.foo())







if __name__ == "__main__":
    unittest.main()
