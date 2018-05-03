import abc
from six import with_metaclass

__version__= "$Id: $"


class AbstractTipTilt2Axis(with_metaclass(abc.ABCMeta, object)):


    @abc.abstractmethod
    def enableControlLoop(self):
        assert False

    @abc.abstractmethod
    def disableControlLoop(self):
        assert False

    @abc.abstractmethod
    def isControlLoopEnabled(self):
        assert False

    @abc.abstractmethod
    def getDataRecorderConfiguration(self):
        assert False

    @abc.abstractmethod
    def getPosition(self):
        assert False

    @abc.abstractmethod
    def getTargetPosition(self):
        assert False

    @abc.abstractmethod
    def setTargetPosition(self, positionInMilliRad):
        assert False

    @abc.abstractmethod
    def getVoltages(self):
        assert False

    @abc.abstractmethod
    def startSinusoidalModulation(self):
        assert False

    @abc.abstractmethod
    def stopModulation(self):
        assert False

    @abc.abstractmethod
    def isModulationEnabled(self):
        assert False

    @abc.abstractmethod
    def getRecordedData(self, howManyPoints, dataRecorderCfg=None):
        assert False

    @abc.abstractmethod
    def getRecordedDataTimeStep(self):
        assert False

    @abc.abstractmethod
    def status(self):
        assert False

    @abc.abstractmethod
    def startFreeformModulation(self, axisATrajectory, axisBTrajectory):
        assert False

    @abc.abstractmethod
    def getOpenLoopValue(self):
        assert False

    @abc.abstractmethod
    def setOpenLoopValue(self):
        assert False
