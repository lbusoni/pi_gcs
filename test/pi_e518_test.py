#!/usr/bin/env python
import unittest

__version__ = "$Id:$"


class PIE518Test(unittest.TestCase):


    def setUp(self):
        hostname= 'host.name.org'
        self.pi518= PhysikInstrumenteE518(hostname)


    def tearDown(self):
        pass


    def testFoo(self):
        self.pi518.connectTCPIP()
        self.assertEqual('foo',
                         self.pi518.foo())


if __name__ == "__main__":
    unittest.main()
