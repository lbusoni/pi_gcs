
__version__= "$Id: $"


class TipTiltConfiguration():

    LOWER_VOLTAGE_LIMIT= 'lowerVoltageLimit'
    UPPER_VOLTAGE_LIMIT= 'upperVoltageLimit'
    PIVOT_VALUE= 'pivotValue'


    def __init__(self):
        self._calib= {}
        self._calib[self.LOWER_VOLTAGE_LIMIT]= [0, 0, 0]
        self._calib[self.UPPER_VOLTAGE_LIMIT]= [100, 100, 100]
        self._calib[self.PIVOT_VALUE]= 100


    def calibration(self):
        return self._calib


    @property
    def lowerVoltageLimit(self):
        return self._calib[self.LOWER_VOLTAGE_LIMIT]


    @property
    def upperVoltageLimit(self):
        return self._calib[self.UPPER_VOLTAGE_LIMIT]


    @property
    def pivotValue(self):
        return self._calib[self.PIVOT_VALUE] 