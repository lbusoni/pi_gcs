

__version__= "$Id: $"


class RecordOption(object):
    TARGET_POSITION= 1
    CURRENT_POSITION= 2
    POSITION_ERROR= 3
    CONTROL_OUTPUT= 15
    CONTROL_VOLTAGE= 7

    ALL_OPTIONS= [TARGET_POSITION,
                  CURRENT_POSITION,
                  POSITION_ERROR,
                  CONTROL_OUTPUT,
                  CONTROL_VOLTAGE]


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
        return self._table.keys()
