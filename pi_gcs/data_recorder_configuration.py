

__version__= "$Id: $"


class RecordOption(object):
    UNKNOWN_OPTION= 0
    TARGET_POSITION_OF_AXIS= 1
    REAL_POSITION_OF_AXIS= 2
    POSITION_ERROR_OF_AXIS= 3
    VOLTAGE_OF_PIEZO_CHANNEL= 7
    CONTROL_OUTPUT_OF_AXIS= 15
    DAC_OF_PIEZO_CHANNEL= 16
    SENSOR_VALUE= 17
    SENSOR_FILTERED= 18
    TARGET_POSITION_SLEW_RATE_LIMITED= 22
    DRIFT_COMPENSATION_OFFSET= 32
    ADC_OF_ANALOG_INPUT= 81


    ALL_OPTIONS= [UNKNOWN_OPTION,
                  TARGET_POSITION_OF_AXIS,
                  REAL_POSITION_OF_AXIS,
                  POSITION_ERROR_OF_AXIS,
                  VOLTAGE_OF_PIEZO_CHANNEL,
                  CONTROL_OUTPUT_OF_AXIS,
                  DAC_OF_PIEZO_CHANNEL,
                  SENSOR_VALUE,
                  SENSOR_FILTERED,
                  TARGET_POSITION_SLEW_RATE_LIMITED,
                  DRIFT_COMPENSATION_OFFSET,
                  ADC_OF_ANALOG_INPUT]


class DataRecorderConfiguration(object):



    def __init__(self):
        self._table= {}


    def setTable(self, recordTable, source, recordOption):
        assert recordOption in RecordOption.ALL_OPTIONS,\
            'unknown record option %d. Valid values %s' % (
                recordOption, str(RecordOption.ALL_OPTIONS))

        self._table[recordTable]= (source, recordOption)


    def getRecordSource(self, recordTable):
        return self._table[recordTable][0]


    def getRecordOption(self, recordTable):
        return self._table[recordTable][1]


    def getTableIds(self):
        return list(self._table.keys())
