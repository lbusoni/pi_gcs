
__version__= "$Id: $"


class TipTiltConfiguration():

    HOSTNAME= 'hostname'
    LOWER_VOLTAGE_LIMIT= 'lowerVoltageLimit'
    PIVOT_VALUE= 'pivotValue'
    UPPER_VOLTAGE_LIMIT= 'upperVoltageLimit'
    POSITION_TO_MILLIRAD_AXIS_A_LINEAR_COEFF= \
        'positionToMilliRadAxisALinearCoeff'
    POSITION_TO_MILLIRAD_AXIS_A_OFFSET_COEFF= \
        'positionToMilliRadAxisAOffsetCoeff'
    POSITION_TO_MILLIRAD_AXIS_B_LINEAR_COEFF= \
        'positionToMilliRadAxisBLinearCoeff'
    POSITION_TO_MILLIRAD_AXIS_B_OFFSET_COEFF= \
        'positionToMilliRadAxisBOffsetCoeff'

    def __init__(self):
        self._calib= {}
        self._calib[self.LOWER_VOLTAGE_LIMIT]= [0, 0, 0]
        self._calib[self.UPPER_VOLTAGE_LIMIT]= [100, 100, 100]
        self._calib[self.PIVOT_VALUE]= 100
        self._calib[self.HOSTNAME]= None
        self._calib[self.POSITION_TO_MILLIRAD_AXIS_A_LINEAR_COEFF]= 1.0
        self._calib[self.POSITION_TO_MILLIRAD_AXIS_A_OFFSET_COEFF]= 0.0
        self._calib[self.POSITION_TO_MILLIRAD_AXIS_B_LINEAR_COEFF]= 1.0
        self._calib[self.POSITION_TO_MILLIRAD_AXIS_B_OFFSET_COEFF]= 0.0


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


    @property
    def hostname(self):
        return self._calib[self.HOSTNAME]


    @hostname.setter
    def hostname(self, value):
        self._calib[self.HOSTNAME]= value


    @property
    def positionToMilliRadAxisALinearCoeff(self):
        return self._calib[self.POSITION_TO_MILLIRAD_AXIS_A_LINEAR_COEFF]


    @positionToMilliRadAxisALinearCoeff.setter
    def positionToMilliRadAxisALinearCoeff(self, value):
        self._calib[self.POSITION_TO_MILLIRAD_AXIS_A_LINEAR_COEFF]= value


    @property
    def positionToMilliRadAxisAOffsetCoeff(self):
        return self._calib[self.POSITION_TO_MILLIRAD_AXIS_A_OFFSET_COEFF]


    @positionToMilliRadAxisAOffsetCoeff.setter
    def positionToMilliRadAxisAOffsetCoeff(self, value):
        self._calib[self.POSITION_TO_MILLIRAD_AXIS_A_OFFSET_COEFF]= value


    @property
    def positionToMilliRadAxisBLinearCoeff(self):
        return self._calib[self.POSITION_TO_MILLIRAD_AXIS_B_LINEAR_COEFF]


    @positionToMilliRadAxisBLinearCoeff.setter
    def positionToMilliRadAxisBLinearCoeff(self, value):
        self._calib[self.POSITION_TO_MILLIRAD_AXIS_B_LINEAR_COEFF]= value


    @property
    def positionToMilliRadAxisBOffsetCoeff(self):
        return self._calib[self.POSITION_TO_MILLIRAD_AXIS_B_OFFSET_COEFF]


    @positionToMilliRadAxisBOffsetCoeff.setter
    def positionToMilliRadAxisBOffsetCoeff(self, value):
        self._calib[self.POSITION_TO_MILLIRAD_AXIS_B_OFFSET_COEFF]= value



