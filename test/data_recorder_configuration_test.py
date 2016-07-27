#!/usr/bin/env python
import unittest
from pi_gcs.data_recorder_configuration import DataRecorderConfiguration,\
    RecordOption

__version__ = "$Id:$"


class DataRecorderConfigurationTest(unittest.TestCase):


    def testSetAndGet(self):
        cfg= DataRecorderConfiguration()
        cfg.setTable(42, "foo", RecordOption.CONTROL_OUTPUT)
        cfg.setTable(3.14, 111, RecordOption.CONTROL_VOLTAGE)
        self.assertEqual("foo", cfg.getRecordSource(42))
        self.assertEqual(RecordOption.CONTROL_OUTPUT,
                         cfg.getRecordOption(42))
        self.assertEqual(111, cfg.getRecordSource(3.14))
        self.assertRaises(KeyError, cfg.getRecordSource, 43)
        self.assertEqual([42, 3.14], cfg.getTableIds())


    def testRaiseIfUnknownOption(self):
        cfg= DataRecorderConfiguration()
        self.assertRaises(
            Exception,
            cfg.setTable, 0, "bar", "UNKNOWN_OPTION")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()