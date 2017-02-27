import numpy as np
from pi_gcs.gcs2 import WaveformGenerator, PIException
from pi_gcs.data_recorder_configuration import DataRecorderConfiguration,\
    RecordOption

__version__= "$Id: $"


class TipTilt2Axis(object):

    AXIS_A= "A"
    AXIS_B= "B"
    ALL_AXES= "A B"
    ALL_CHANNELS= [1, 2, 3]

    def __init__(self, piController, tipTiltConfiguration):
        self._ctrl= piController
        self._cfg= tipTiltConfiguration

        self._origTargetPosition= None
        self._modulationEnabled= False



    def setUp(self):
        self._connectController()
        self._checkNumberOfChannels()
        self._enableRemoteControlMode()
        self._stopWaveformGenerators()
        self._setVoltageLimits()
        self.disableControlLoop()
        self._configure3rdAxisAsPivot()
        self.enableControlLoop()


    def _connectController(self):
        self._ctrl.connectTCPIP(self._cfg.hostname)


    def _checkNumberOfChannels(self):
        assert 3 == self._ctrl.getNumberOfInputSignalChannels()
        assert 3 == self._ctrl.getNumberOfOutputSignalChannels()


    def _enableRemoteControlMode(self):
        self._ctrl.enableControlMode(self.ALL_CHANNELS)


    def _stopWaveformGenerators(self):
        self._ctrl.setWaveGeneratorStartStopMode([0, 0, 0])


    def _setVoltageLimits(self):
        self._ctrl.setLowerVoltageLimit(
            self.ALL_CHANNELS, self._cfg.lowerVoltageLimit)
        self._ctrl.setUpperVoltageLimit(
            self.ALL_CHANNELS, self._cfg.upperVoltageLimit)


    def _configure3rdAxisAsPivot(self):
        pivotAxis= self._ctrl.getAxesIdentifiers()[2]
        self._ctrl.setServoControlMode(pivotAxis, [False])
        self._ctrl.setOpenLoopAxisValue(pivotAxis, self._cfg.pivotValue)


    def enableControlLoop(self):
        self._ctrl.setServoControlMode(self.ALL_AXES, [True, True])


    def disableControlLoop(self):
        self._ctrl.setServoControlMode(self.ALL_AXES, [False, False])


    def isControlLoopEnabled(self):
        return np.all(self._ctrl.getServoControlMode(self.ALL_AXES))


    def _positionConversionCoefficients(self, axisName):
        if axisName == self.AXIS_A:
            offset= self._cfg.positionToMilliRadAxisAOffsetCoeff
            linear= self._cfg.positionToMilliRadAxisALinearCoeff
        elif axisName == self.AXIS_B:
            offset= self._cfg.positionToMilliRadAxisBOffsetCoeff
            linear= self._cfg.positionToMilliRadAxisBLinearCoeff
        else:
            raise KeyError("unknown axis %s")
        return offset, linear


    def _gcsUnitsToMilliRadOneAxis(self, posInGcsUnits, axisName):
        offset, linear= self._positionConversionCoefficients(axisName)
        return linear * posInGcsUnits + offset


    def _gcsUnitsToMilliRad(self, positionInGcsUnits):
        mradA= self._gcsUnitsToMilliRadOneAxis(positionInGcsUnits[0],
                                               self.AXIS_A)
        mradB= self._gcsUnitsToMilliRadOneAxis(positionInGcsUnits[1],
                                               self.AXIS_B)
        return np.array([mradA, mradB])


    def _milliRadToGcsUnitsOneAxis(self, posInMilliRad, axisName):
        offset, linear= self._positionConversionCoefficients(axisName)
        return (posInMilliRad - offset) / linear


    def _milliRadToGcsUnits(self, positionInMilliRad):
        posA= self._milliRadToGcsUnitsOneAxis(positionInMilliRad[0],
                                              self.AXIS_A)
        posB= self._milliRadToGcsUnitsOneAxis(positionInMilliRad[1],
                                              self.AXIS_B)
        return np.array([posA, posB])


    def getPosition(self):
        return self._gcsUnitsToMilliRad(self._ctrl.getPosition(self.ALL_AXES))


    def getTargetPosition(self):
        return self._gcsUnitsToMilliRad(
            self._ctrl.getTargetPosition(self.ALL_AXES))


    def setTargetPosition(self, positionInMilliRad):
        return self._ctrl.setTargetPosition(
            self.ALL_AXES,
            self._milliRadToGcsUnits(positionInMilliRad))


    def getVoltages(self):
        return self._ctrl.getVoltages(self.ALL_CHANNELS)


    def startSinusoidalModulation(self,
                                  radiusInMilliRad,
                                  frequencyInHz,
                                  phasesInRadians,
                                  centerInMilliRad):
        self._origTargetPosition= centerInMilliRad
        self.stopModulation()

        assert np.ptp(self._ctrl.getWaveGeneratorTableRate()) == 0, \
            "wave generator table rate must be the same for every table"
        wgtr= self._ctrl.getWaveGeneratorTableRate()[0]
        timestep= self._ctrl.getServoUpdateTimeInSeconds() * wgtr

#         periodInSec= 1./ frequencyInHz
#         lengthInPoints= periodInSec/ timestep
#         peakOfTheSineCurve= self._milliRadToGcsUnits(
#             self.getTargetPosition() + radiusInMilliRad)
#         offsetOfTheSineCurve= self._milliRadToGcsUnits(
#             self.getTargetPosition() - radiusInMilliRad)
#         amplitudeOfTheSineCurve= peakOfTheSineCurve - offsetOfTheSineCurve
#         wavelengthOfTheSineCurveInPoints= periodInSec/ timestep
#         startPoint= np.array([0, 0.25])* wavelengthOfTheSineCurveInPoints
#         curveCenterPoint= 0.5* wavelengthOfTheSineCurveInPoints

        self._ctrl.clearWaveTableData([1, 2, 3])
        self._setSinusoidalWaveform(1, timestep, radiusInMilliRad[0],
                                    frequencyInHz, phasesInRadians[0],
                                    centerInMilliRad[0])
        self._setSinusoidalWaveform(2, timestep, radiusInMilliRad[1],
                                    frequencyInHz, phasesInRadians[1],
                                    centerInMilliRad[1])
#         self._ctrl.setSinusoidalWaveform(
#             1, WaveformGenerator.CLEAR, lengthInPoints,
#             amplitudeOfTheSineCurve[0], offsetOfTheSineCurve[0],
#             wavelengthOfTheSineCurveInPoints, startPoint[0], curveCenterPoint)
#         self._ctrl.setSinusoidalWaveform(
#             2, WaveformGenerator.CLEAR, lengthInPoints,
#             amplitudeOfTheSineCurve[1], offsetOfTheSineCurve[1],
#             wavelengthOfTheSineCurveInPoints, startPoint[1], curveCenterPoint)
        self._ctrl.setConnectionOfWaveTableToWaveGenerator([1, 2], [1, 2])
        self._ctrl.setWaveGeneratorStartStopMode([1, 1, 0])
        self._modulationEnabled= True


    def _getAxisFromWaveTableId(self, waveTableId):
        if waveTableId == 1:
            return self.AXIS_A
        elif waveTableId == 2:
            return self.AXIS_B
        else:
            raise ValueError("Unknown waveTableId %d" % waveTableId)


    def _setSinusoidalWaveform(self, waveTableId, timeStepInSec,
                               amplitudeInMilliRad, frequencyInHz,
                               phaseInRadians, offsetInMilliRad):
        axisName= self._getAxisFromWaveTableId(waveTableId)
        periodInSec= 1./ frequencyInHz
        wgtr= self._ctrl.getWaveGeneratorTableRate()[0]
        timestep= self._ctrl.getServoUpdateTimeInSeconds() * wgtr

        lengthInPoints= periodInSec/ timestep
        peakOfTheSineCurve= self._milliRadToGcsUnitsOneAxis(
            offsetInMilliRad + amplitudeInMilliRad, axisName)
        valleyOfTheSineCurve= self._milliRadToGcsUnitsOneAxis(
            offsetInMilliRad - amplitudeInMilliRad, axisName)
        amplitudeOfTheSineCurve= peakOfTheSineCurve - valleyOfTheSineCurve
        wavelengthOfTheSineCurveInPoints= periodInSec/ timestep
        startPoint= phaseInRadians/ (2* np.pi) * \
            wavelengthOfTheSineCurveInPoints
        curveCenterPoint= 0.5* wavelengthOfTheSineCurveInPoints
        self._ctrl.setSinusoidalWaveform(
            waveTableId, WaveformGenerator.CLEAR, lengthInPoints,
            amplitudeOfTheSineCurve, valleyOfTheSineCurve,
            wavelengthOfTheSineCurveInPoints, startPoint, curveCenterPoint)




    def stopModulation(self):
        self._stopWaveformGenerators()
        self._modulationEnabled= False
        if self._origTargetPosition is not None:
            self.setTargetPosition(self._origTargetPosition)


    def isModulationEnabled(self):
        return self._modulationEnabled


    def _defaultDataRecorderConfiguration(self):
        dataRecorderCfg= DataRecorderConfiguration()
        dataRecorderCfg.setTable(1, "A", RecordOption.REAL_POSITION_OF_AXIS)
        dataRecorderCfg.setTable(2, "B", RecordOption.REAL_POSITION_OF_AXIS)
        dataRecorderCfg.setTable(3, "A", RecordOption.POSITION_ERROR_OF_AXIS)
        dataRecorderCfg.setTable(4, "B", RecordOption.POSITION_ERROR_OF_AXIS)
        dataRecorderCfg.setTable(5, "A", RecordOption.TARGET_POSITION_OF_AXIS)
        dataRecorderCfg.setTable(6, "B", RecordOption.TARGET_POSITION_OF_AXIS)
        return dataRecorderCfg


    def _configureDataRecoders(self, dataRecorderCfg=None):
        if dataRecorderCfg is None:
            dataRecorderCfg= self._defaultDataRecorderConfiguration()
        self._ctrl.setDataRecorderConfiguration(dataRecorderCfg)


    def getDataRecorderConfiguration(self):
        return self._ctrl.getDataRecorderConfiguration()


    def _convertRecordedDataToMilliRad(self, recData):
        ret= recData.copy()
        recordOptionsToConvert= [RecordOption.TARGET_POSITION_OF_AXIS,
                                 RecordOption.POSITION_ERROR_OF_AXIS,
                                 RecordOption.REAL_POSITION_OF_AXIS]
        cfg= self.getDataRecorderConfiguration()
        ids= cfg.getTableIds()
        for i in np.arange(len(ids)):
            source= cfg.getRecordSource(ids[i])
            option= cfg.getRecordOption(ids[i])
            if option in recordOptionsToConvert:
                ret[i]= self._gcsUnitsToMilliRadOneAxis(ret[i], source)
        return ret


    def getRecordedData(self, howManyPoints, dataRecorderCfg=None):
        self._startDataRecorder(dataRecorderCfg)
        return self._retrieveRecordedData(howManyPoints)


    def _startDataRecorder(self, dataRecorderCfg=None):
        self._configureDataRecoders(dataRecorderCfg)
        self._ctrl.startRecordingInSyncWithWaveGenerator()


    def _retrieveRecordedData(self, howManyPoints):
        timestep= self._ctrl.getServoUpdateTimeInSeconds()
        rtr= self._ctrl.getRecordTableRate()
        timeValues= np.arange(howManyPoints) * timestep * rtr
        recDataGcs= self._ctrl.getRecordedDataValues(howManyPoints, 1)
        recDataMilliRad= self._convertRecordedDataToMilliRad(recDataGcs)
        return np.vstack((timeValues, recDataMilliRad))


    def status(self):
        status={}
        status['POSITION']= self.getPosition()
        status['TARGET']= self.getTargetPosition()
        status['OUTPUT_VOLTAGE']= self.getVoltages()
        status['CONTROL_LOOP_CLOSED']= self.isControlLoopEnabled()
        status['OVERFLOW']= self._ctrl.getOverflowState(self.ALL_AXES)
        return status
