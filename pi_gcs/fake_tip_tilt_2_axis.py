import numpy as np
from pi_gcs.abstract_tip_tilt_2_axes import AbstractTipTilt2Axis
from pygo.decorator import override
from pi_gcs.gcs2 import PIException


__version__= "$Id: $"


class FakeTipTilt2Axis(AbstractTipTilt2Axis):

    def __init__(self):
        self._origTargetPosition= None
        self._position= np.zeros(2)
        self._voltages= np.ones(3)* 50
        self._modulationEnabled= False
        self._controlLoopEnabled= True
        self._recordedDataTimeStep= 40e-6
        self._axisBTrajectory= None
        self._axisBTrajectory= None
        self._openLoopValue= None


    @override
    def enableControlLoop(self):
        self._controlLoopEnabled= True


    @override
    def disableControlLoop(self):
        self._controlLoopEnabled= False


    @override
    def isControlLoopEnabled(self):
        return self._controlLoopEnabled


    @override
    def getDataRecorderConfiguration(self):
        pass

    @override
    def getPosition(self):
        return self._position


    @override
    def getTargetPosition(self):
        return self._origTargetPosition


    @override
    def setTargetPosition(self, positionInMilliRad):
        self._origTargetPosition= positionInMilliRad


    @override
    def getVoltages(self):
        return self._voltages



    def _sine(self, radiusInMilliRad, frequencyInHz,
              phaseInRadians, centerInMilliRad, dt):
        t= np.linspace(0, dt* 4000, 4000, endpoint=False)
        x= radiusInMilliRad * np.sin(
            t* frequencyInHz* 2* np.pi + phaseInRadians) + centerInMilliRad
        return x


    @override
    def startSinusoidalModulation(self, radii, freq, phases, center):
        self._axisATrajectory= self._sine(radii[0], freq,
                                          phases[0], center[0],
                                          self._recordedDataTimeStep)

        self._axisBTrajectory= self._sine(radii[1], freq,
                                          phases[1], center[1],
                                          self._recordedDataTimeStep)
        self._modulationEnabled= True


    @override
    def stopModulation(self):
        self._modulationEnabled= False


    @override
    def isModulationEnabled(self):
        return self._modulationEnabled


    def _repeatVectorTo(self, vector, nPoints):
        return np.tile(vector, nPoints // len(vector) + 1)[0: nPoints]


    def _getRecordedDataValues(self, howManyPoints, startFromPoint=1):
        nRecorders= 8
        retArray=np.zeros((nRecorders, howManyPoints))
        retArray[0]= self._repeatVectorTo(self._axisATrajectory, howManyPoints)
        retArray[1]= self._repeatVectorTo(self._axisBTrajectory, howManyPoints)
        retArray[4]= self._repeatVectorTo(self._axisATrajectory, howManyPoints)
        retArray[5]= self._repeatVectorTo(self._axisBTrajectory, howManyPoints)
        return retArray



    @override
    def getRecordedData(self, howManyPoints, dataRecorderCfg=None):
        timeValues= np.arange(howManyPoints) * self.getRecordedDataTimeStep()
        recDataMilliRad= self._getRecordedDataValues(howManyPoints, 1)
        return np.vstack((timeValues, recDataMilliRad))


    @override
    def getRecordedDataTimeStep(self):
        return self._recordedDataTimeStep


    @override
    def status(self):
        status={}
        status['POSITION']= self.getPosition()
        status['TARGET']= self.getTargetPosition()
        status['OUTPUT_VOLTAGE']= self.getVoltages()
        status['CONTROL_LOOP_CLOSED']= self.isControlLoopEnabled()
        status['OVERFLOW']= np.array([False, False])
        return status


    @override
    def startFreeformModulation(self, axisATrajectory, axisBTrajectory):
        self._axisATrajectory= axisATrajectory
        self._axisBTrajectory= axisBTrajectory
        self._modulationEnabled= True


    @override
    def setOpenLoopValue(self, valueInPercentage):
        if self.isControlLoopEnabled():
            raise PIException("Open-loop motion attempted when servo ON (303)")
        self._openLoopValue= valueInPercentage


    @override
    def getOpenLoopValue(self):
        return self._openLoopValue
