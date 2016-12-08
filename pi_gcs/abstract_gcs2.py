import abc


__version__= "$Id: $"



class AbstractGeneralCommandSet(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def connectTCPIP(self, hostname, port=50000):
        assert False


    @abc.abstractmethod
    def closeConnection(self):
        assert False


    @abc.abstractmethod
    def gcsCommand(self, commandAsString):
        assert False


    @abc.abstractmethod
    def getVersion(self):
        assert False


    @abc.abstractmethod
    def getAxesIdentifiers(self):
        assert False


    @abc.abstractmethod
    def getNumberOfInputSignalChannels(self):
        assert False


    @abc.abstractmethod
    def getNumberOfOutputSignalChannels(self):
        assert False


    @abc.abstractmethod
    def getServoControlMode(self, axesString):
        assert False


    @abc.abstractmethod
    def setServoControlMode(self, axesString, controlMode):
        assert False


    @abc.abstractmethod
    def getControlMode(self, channels):
        assert False


    @abc.abstractmethod
    def setControlMode(self, channels, controlMode):
        assert False


    @abc.abstractmethod
    def enableControlMode(self, channels):
        assert False


    @abc.abstractmethod
    def disableControlMode(self, channels):
        assert False


    @abc.abstractmethod
    def echo(self, message):
        assert False


    @abc.abstractmethod
    def getLowerVoltageLimit(self, channels):
        assert False


    @abc.abstractmethod
    def setLowerVoltageLimit(self, channels, lowerVoltage):
        assert False


    @abc.abstractmethod
    def getUpperVoltageLimit(self, channels):
        assert False


    @abc.abstractmethod
    def setUpperVoltageLimit(self, channels, upperVoltage):
        assert False


    @abc.abstractmethod
    def getPosition(self, axesString):
        assert False


    @abc.abstractmethod
    def getVoltages(self, channels):
        assert False


    @abc.abstractmethod
    def getOpenLoopAxisValue(self, axesString):
        assert False


    @abc.abstractmethod
    def setOpenLoopAxisValue(self, axesString, amplitudeInVolt):
        assert False


    @abc.abstractmethod
    def setRelativeOpenLoopAxisValue(self, axesString, offsetInVolt):
        assert False


    @abc.abstractmethod
    def getTargetPosition(self, axesString):
        assert False


    @abc.abstractmethod
    def setTargetPosition(self, axesString, position):
        assert False


    @abc.abstractmethod
    def setTargetRelativeToCurrentPosition(self, axesString, offset):
        assert False


    @abc.abstractmethod
    def getVolatileMemoryParameters(self, itemId, parameterId):
        assert False


    @abc.abstractmethod
    def getAllDataRecorderOptions(self):
        assert False


    @abc.abstractmethod
    def getNumberOfRecorderTables(self):
        assert False


    @abc.abstractmethod
    def setDataRecorderConfiguration(self, dataRecorderConfiguration):
        assert False


    @abc.abstractmethod
    def getDataRecorderConfiguration(self):
        assert False


    @abc.abstractmethod
    def getRecordedDataValues(self, howManyPoints, startFromPoint=1):
        assert False


    @abc.abstractmethod
    def startRecordingInSyncWithWaveGenerator(self):
        assert False


    @abc.abstractmethod
    def getNumberOfWaveGenerators(self):
        assert False


    @abc.abstractmethod
    def getWaveGeneratorStartStopMode(self):
        assert False


    @abc.abstractmethod
    def setWaveGeneratorStartStopMode(self, startModeArray):
        assert False


    @abc.abstractmethod
    def clearWaveTableData(self, waveTableIdsArray):
        assert False


    @abc.abstractmethod
    def getConnectionOfWaveTableToWaveGenerator(self, waveGeneratorsArray):
        assert False


    @abc.abstractmethod
    def setConnectionOfWaveTableToWaveGenerator(self,
                                                waveGeneratorsArray,
                                                waveTableIdsArray):
        assert False

    @abc.abstractmethod
    def setSinusoidalWaveform(self,
                              waveTableId,
                              append,
                              lengthInPoints,
                              amplitudeOfTheSineCurve,
                              offsetOfTheSineCurve,
                              wavelengthOfTheSineCurveInPoints,
                              startPoint,
                              curveCenterPoint):
        assert False



    @abc.abstractmethod
    def setRecordTableRate(self, recordTableRateInServoLoopCycles=1):
        assert False


    @abc.abstractmethod
    def getRecordTableRate(self):
        assert False


    @abc.abstractmethod
    def getServoUpdateTimeInSeconds(self):
        assert False



    @abc.abstractmethod
    def setWaveGeneratorTableRate(self,
                                  waveGeneratorTableRateInServoLoopCycles):
        assert False


    @abc.abstractmethod
    def getWaveGeneratorTableRate(self):
        assert False


    @abc.abstractmethod
    def getOverflowState(self):
        assert False


    @abc.abstractmethod
    def setDataRecoderTriggerSource(self, source, value):
        assert False


    @abc.abstractmethod
    def getDataRecorderTriggerSource(self):
        assert False


