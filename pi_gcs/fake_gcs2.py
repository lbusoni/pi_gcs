import numpy as np
from pi_gcs.abstract_gcs2 import AbstractGeneralCommandSet
from pi_gcs.gcs2 import WaveformGenerator
from pi_gcs.data_recorder_configuration import DataRecorderConfiguration,\
    RecordOption


__version__= "$Id: $"


class FakeGeneralCommandSet(AbstractGeneralCommandSet):

    def __init__(self):
        self._channelsInCloseLoop= {}
        self._lowerVoltageLimits= {}
        self._upperVoltageLimits= {}
        self._numberOfInputSignalChannels= 3
        self._numberOfOutputSignalChannels= 3
        self._axesIdentifiers= ['A', 'B', 'C']
        self._openLoopAxisValue= {}
        self._targetPosition= {}
        self._position= {}
        self._waveGeneratorStartStopMode= {}
        self._rtr= 1
        self._wtr= np.ones(3)
        self.triggerStartRecordingInSyncWithWaveGenerator= 0
        self._waveform= {}
        self._dataRecorderConfig= self._defaultDataRecorderConfiguration()


    def _dictToArray(self, dicto, keys):
        ret= []
        for k in keys:
            ret.append(dicto[k])
        return np.array(ret)


    def _arrayToDict(self, dicto, keys, values):
        valueArray= np.atleast_1d(values)
        assert len(keys) == len(valueArray), \
            "%d %d" % (len(keys), len(valueArray))
        for i in range(len(keys)):
            dicto[keys[i]]= valueArray[i]


    def _axesString2Array(self, axesString):
        return [x.strip() for x in axesString.split(' ')]


    def connectTCPIP(self, hostname, port=50000):
        pass



    def closeConnection(self):
        pass



    def gcsCommand(self, commandAsString):
        pass



    def getVersion(self):
        pass



    def getAxesIdentifiers(self):
        return self._axesIdentifiers


    def getNumberOfInputSignalChannels(self):
        return self._numberOfInputSignalChannels


    def getNumberOfOutputSignalChannels(self):
        return self._numberOfOutputSignalChannels


    def getServoControlMode(self, axesString):
        axes= self._axesString2Array(axesString)
        return self._dictToArray(self._channelsInCloseLoop, axes)


    def setServoControlMode(self, axesString, controlMode):
        axes= self._axesString2Array(axesString)
        self._arrayToDict(self._channelsInCloseLoop, axes, controlMode)


    def getControlMode(self, channels):
        pass



    def setControlMode(self, channels, controlMode):
        pass



    def enableControlMode(self, channels):
        pass



    def disableControlMode(self, channels):
        pass



    def echo(self, message):
        pass



    def getLowerVoltageLimit(self, channels):
        return self._dictToArray(self._lowerVoltageLimits, channels)


    def setLowerVoltageLimit(self, channels, lowerVoltage):
        self._arrayToDict(self._lowerVoltageLimits, channels, lowerVoltage)


    def getUpperVoltageLimit(self, channels):
        return self._dictToArray(self._upperVoltageLimits, channels)


    def setUpperVoltageLimit(self, channels, upperVoltage):
        self._arrayToDict(self._upperVoltageLimits, channels, upperVoltage)


    def getPosition(self, axesString):
        return self.getTargetPosition(axesString)


    def getVoltages(self, channels):
        pass


    def getOpenLoopAxisValue(self, axesString):
        axes= [x.strip() for x in axesString.split(' ')]
        return self._dictToArray(self._openLoopAxisValue, axes)


    def setOpenLoopAxisValue(self, axesString, amplitudeInVolt):
        axes= [x.strip() for x in axesString.split(' ')]
        self._arrayToDict(self._openLoopAxisValue, axes, amplitudeInVolt)


    def setRelativeOpenLoopAxisValue(self, axesString, offsetInVolt):
        pass


    def getTargetPosition(self, axesString):
        axes= [x.strip() for x in axesString.split(' ')]
        return self._dictToArray(self._targetPosition, axes)


    def setTargetPosition(self, axesString, position):
        axes= [x.strip() for x in axesString.split(' ')]
        self._arrayToDict(self._targetPosition, axes, position)


    def setTargetRelativeToCurrentPosition(self, axesString, offset):
        pass


    def getVolatileMemoryParameters(self, itemId, parameterId):
        pass


    def getAllDataRecorderOptions(self):
        pass



    def getNumberOfRecorderTables(self):
        return 11


    def setDataRecorderConfiguration(self, dataRecorderConfiguration):
        self._dataRecorderConfig= dataRecorderConfiguration


    def getDataRecorderConfiguration(self):
        return self._dataRecorderConfig


    def _defaultDataRecorderConfiguration(self):
        dataRecorderCfg= DataRecorderConfiguration()
        dataRecorderCfg.setTable(1, "A", RecordOption.REAL_POSITION_OF_AXIS)
        dataRecorderCfg.setTable(2, "B", RecordOption.REAL_POSITION_OF_AXIS)
        dataRecorderCfg.setTable(3, "A", RecordOption.POSITION_ERROR_OF_AXIS)
        dataRecorderCfg.setTable(4, "B", RecordOption.POSITION_ERROR_OF_AXIS)
        dataRecorderCfg.setTable(5, "A", RecordOption.TARGET_POSITION_OF_AXIS)
        dataRecorderCfg.setTable(6, "B", RecordOption.TARGET_POSITION_OF_AXIS)
        return dataRecorderCfg


    def getRecordedDataValues(self, howManyPoints, startFromPoint=1):
        nRecorders= self.getNumberOfRecorderTables()
        return np.arange(howManyPoints * nRecorders).\
            reshape((nRecorders, howManyPoints))


    def startRecordingInSyncWithWaveGenerator(self):
        self.triggerStartRecordingInSyncWithWaveGenerator+= 1


    def getNumberOfWaveGenerators(self):
        pass


    def getWaveGeneratorStartStopMode(self):
        return self._dictToArray(self._waveGeneratorStartStopMode,
                                 [1, 2, 3])


    def setWaveGeneratorStartStopMode(self, startModeArray):
        self._arrayToDict(self._waveGeneratorStartStopMode,
                          [1, 2, 3],
                          startModeArray)


    def clearWaveTableData(self, waveTableIdsArray):
        pass


    def getConnectionOfWaveTableToWaveGenerator(self, waveGeneratorsArray):
        pass


    def setConnectionOfWaveTableToWaveGenerator(self,
                                                waveGeneratorsArray,
                                                waveTableIdsArray):
        pass


    def setSinusoidalWaveform(self,
                              waveTableId,
                              append,
                              lengthInPoints,
                              amplitudeOfTheSineCurve,
                              offsetOfTheSineCurve,
                              wavelengthOfTheSineCurveInPoints,
                              startPoint,
                              curveCenterPoint):
        '''
        See description of PI_WAV_SIN_P in PI GCS 2.0 DLL doc
        '''
        curveCenterPoint= int(round(curveCenterPoint))
        wavelengthOfTheSineCurveInPoints= \
            int(round(wavelengthOfTheSineCurveInPoints))
        startPoint= int(round(startPoint))
        lengthInPoints= int(round(lengthInPoints))
        assert append == WaveformGenerator.CLEAR, 'only CLEAR implemented'
        assert startPoint >= 0
        assert startPoint < lengthInPoints
        assert curveCenterPoint >= 0
        assert startPoint + curveCenterPoint < lengthInPoints, \
            'startPoint + curveCenterPoint >= lenghtInPoints (%d+%d>=%d)' % (
                startPoint, curveCenterPoint, lengthInPoints)

        ccUp= 0.5* curveCenterPoint
        rampUp= 0.5 * amplitudeOfTheSineCurve* (1 + np.sin(
            np.arange(-ccUp, ccUp) / ccUp * np.pi / 2))
        ccDown= 0.5* (wavelengthOfTheSineCurveInPoints - curveCenterPoint)
        rampDown= 0.5 * amplitudeOfTheSineCurve* (1 - np.sin(
            np.arange(-ccDown, ccDown) / ccDown * np.pi / 2))
        waveform= np.zeros(lengthInPoints) + offsetOfTheSineCurve
        waveform[0: curveCenterPoint]= offsetOfTheSineCurve + rampUp
        waveform[curveCenterPoint: wavelengthOfTheSineCurveInPoints]= \
            offsetOfTheSineCurve + rampDown
        waveform= np.roll(waveform, startPoint)
        self._waveform[waveTableId]= waveform


    def getWaveform(self, waveTableId):
        return self._waveform[waveTableId]


    def setRecordTableRate(self, recordTableRateInServoLoopCycles=1):
        self._rtr= recordTableRateInServoLoopCycles


    def getRecordTableRate(self):
        return self._rtr


    def getServoUpdateTimeInSeconds(self):
        return 40e-6


    def setWaveGeneratorTableRate(self,
                                  waveGeneratorTableRateInServoLoopCycles):
        self._wtr= np.ones(3) * waveGeneratorTableRateInServoLoopCycles


    def getWaveGeneratorTableRate(self):
        return self._wtr


    def getOverflowState(self):
        pass


    def setDataRecoderTriggerSource(self, source, value):
        pass


    def getDataRecorderTriggerSource(self):
        pass


    def startStepAndResponseMeasurement(self, axisString, amplitude):
        pass


    def startImpulseAndResponseMeasurement(self, axisString, amplitude):
        pass

