from ctypes.util import find_library
import ctypes
from ctypes import c_int, c_bool, c_char, c_char_p, c_double
import numpy as np
from pi_gcs.data_recorder_configuration import DataRecorderConfiguration
from zmq.backend.cffi._cffi import cfg


__version__= "$Id: $"

CHANNEL_OFFLINE= 0
CHANNEL_ONLINE= 1


class PIException(Exception):
    pass


class ConnectionError(PIException):
    pass


class CTypeArray():

    def __init__(self, ctype, array):
        assert isinstance(array, (np.ndarray, list, tuple))
        self._ctype= ctype
        self._ret= (self._ctype * len(array))()
        for i in range(len(array)):
            self._ret[i]= array[i]


    def from_param(self):
        return self._ret


    def toNumpyArray(self):
        return np.array([x for x in self._ret])


class CIntArray(CTypeArray):
    def __init__(self, array):
        CTypeArray.__init__(self, c_int, array)


class CDoubleArray(CTypeArray):
    def __init__(self, array):
        CTypeArray.__init__(self, c_double, array)


class CBoolArray(CTypeArray):
    def __init__(self, array):
        CTypeArray.__init__(self, c_bool, array)


class CCharArray(CTypeArray):
    def __init__(self, array):
        CTypeArray.__init__(self, c_char, array)



class Channels(CIntArray):
    def __init__(self, channels):
        CIntArray.__init__(self, channels)


class GeneralCommandSet2(object):

    GCS_TRUE= 1
    GCS_FALSE= 0

    def __init__(self):
        self._hostname= None
        self._port= None
        self._lib= None
        self._id= None
        self._axes= ctypes.c_char_p("A B C")
        self._channels= (ctypes.c_int * 3)(1, 2, 3)

        self._importLibrary()


    def _importLibrary(self):
        piLibName= 'pi_pi_gcs2'
        pilib= find_library(piLibName)
        if pilib is None:
            raise PIException("Library %s not found" % piLibName)
        self._lib= ctypes.CDLL(pilib)


    def _errAsString(self, errorCode):
        bufSize= 256
        s=ctypes.create_string_buffer('\000' * bufSize)

        ret= self._lib.PI_TranslateError(
            errorCode, s, bufSize)
        if ret != 1:
            return "Unknown error (%d)" % errorCode
        return "%s (%d)" % (s.value, errorCode)


    def _convertErrorToException(self, returnValue, expectedReturn=GCS_TRUE):
        if returnValue != expectedReturn:
            errorId= self._lib.PI_GetError(self._id)
            if errorId != 0:
                errMsg= ""
                while errorId != 0:
                    errMsg+= self._errAsString(errorId)+ " "
                    errorId= self._lib.PI_GetError(self._id)
                raise PIException("%s" % errMsg)


    def _convertCArrayToNumpyArray(self, cArray):
        return np.array([x for x in cArray.array()])


    def _toBool(self, value):
        assert value in [0, 1]
        return True if value == 1 else False


    def _getterChannels(self, channels, gcsFunction, valueArrayClass):
        chArray= np.atleast_1d(channels)
        value= valueArrayClass([0] * len(chArray))
        gcsFunction.argtypes= [c_int, CIntArray, valueArrayClass, c_int]
        self._convertErrorToException(
            gcsFunction(self._id,
                        CIntArray(chArray),
                        value,
                        len(chArray)))
        return value.toNumpyArray()


    def _setterChannels(self, channels, value, gcsFunction, valueArrayClass):
        valueArray= np.atleast_1d(value)
        assert len(channels) == len(valueArray)
        gcsFunction.argtypes= [c_int, CIntArray, valueArrayClass, c_int]
        self._convertErrorToException(
            gcsFunction(self._id,
                        CIntArray(channels),
                        valueArrayClass(valueArray),
                        len(channels)))


    def _getterAxes(self, axesString, gcsFunction, valueArrayClass):
        nCh= len(axesString.split())
        value= valueArrayClass([0]* nCh)
        gcsFunction.argtypes= [c_int, c_char_p, valueArrayClass]
        self._convertErrorToException(
            gcsFunction(self._id, axesString, value))
        return value.toNumpyArray()


    def _setterAxes(self, axesString, value, gcsFunction, valueArrayClass):
        nCh= len(axesString.split())
        valueArray= np.atleast_1d(value)
        assert nCh == len(valueArray)
        gcsFunction.argtypes= [c_int, c_char_p, valueArrayClass]
        self._convertErrorToException(
            gcsFunction(self._id, axesString, valueArrayClass(valueArray)))


    def _getterReturnString(self, gcsFunction, bufSize):
        s=ctypes.create_string_buffer('\000', bufSize)
        self._convertErrorToException(
            gcsFunction(self._id, s, bufSize))
        return s.value


    def _isConnected(self):
        return self._toBool(self._lib.PI_IsConnected(self._id))


    def connectTCPIP(self, hostname, port=50000):
        ide= self._lib.PI_ConnectTCPIP(hostname, port)
        if ide == -1:
            errorId= self._lib.PI_GetError(ide)
            raise ConnectionError("%s" % self._errAsString(errorId))
        self._id= ide
        self._hostname= hostname
        self._port= port


    def closeConnection(self):
        try:
            self._lib.PI_CloseConnection(self._id)
        except Exception:
            pass


    def gcsCommand(self, commandAsString):
        self._lib.PI_GcsCommandset.argtypes= [c_int, c_char_p]
        self._lib.PI_GcsGetAnswer.argtypes= [c_int, c_char_p, c_int]
        self._convertErrorToException(
            self._lib.PI_GcsCommandset(self._id, commandAsString))
        retSize= c_int()
        res= ''
        self._convertErrorToException(
            self._lib.PI_GcsGetAnswerSize(self._id, ctypes.byref(retSize)))
        while retSize.value != 0:
            buf= ctypes.create_string_buffer('\000', retSize.value)
            self._convertErrorToException(
                self._lib.PI_GcsGetAnswer(self._id, buf, retSize.value))
            res+= buf.value
            self._convertErrorToException(
                self._lib.PI_GcsGetAnswerSize(self._id, ctypes.byref(retSize)))
        return res


    def getVersion(self):
        bufSize= 256
        return self._getterReturnString(self._lib.PI_qVER, bufSize)


    def getAxesIdentifiers(self):
        return self._getterReturnString(self._lib.PI_qSAI, 256).split()


    def getNumberOfInputSignalChannels(self):
        nChannels= c_int()
        self._convertErrorToException(
            self._lib.PI_qTSC(self._id, ctypes.byref(nChannels)))
        return nChannels.value


    def getNumberOfOutputSignalChannels(self):
        nChannels= c_int()
        self._convertErrorToException(
            self._lib.PI_qTPC(self._id, ctypes.byref(nChannels)))
        return nChannels.value


    def getServoControlMode(self, axesString):
        nCh= len(axesString.split())
        svo= CIntArray([False]* nCh)
        self._lib.PI_qSVO.argtypes= [c_int, c_char_p, CIntArray]
        self._convertErrorToException(
            self._lib.PI_qSVO(self._id, axesString, svo))
        return svo.toNumpyArray().astype('bool')


    def setServoControlMode(self, axesString, controlMode):
        self._setterAxes(
            axesString,
            np.atleast_1d(controlMode).astype('int'),
            self._lib.PI_SVO,
            CIntArray)


    def getControlMode(self, channels):
        return self._getterChannels(channels, self._lib.PI_qONL, CIntArray)


    def setControlMode(self, channels, controlMode):
        self._setterChannels(
            channels, controlMode, self._lib.PI_ONL, CIntArray)


    def enableControlMode(self, channels):
        enable= [CHANNEL_ONLINE]* len(channels)
        self.setControlMode(channels, enable)


    def disableControlMode(self, channels):
        disable= [CHANNEL_OFFLINE]* len(channels)
        self.setControlMode(channels, disable)


    def echo(self, message):
        cMsg= ctypes.create_string_buffer(message)
        cRet= ctypes.create_string_buffer(0, ctypes.sizeof(cMsg))
        self._convertErrorToException(
            self._lib.PI_qECO(self._id, cMsg, cRet))
        return cRet.value


    def getLowerVoltageLimit(self, channels):
        return self._getterChannels(channels, self._lib.PI_qVMI, CDoubleArray)


    def setLowerVoltageLimit(self, channels, lowerVoltage):
        self._setterChannels(
            channels, lowerVoltage, self._lib.PI_VMI, CDoubleArray)


    def getUpperVoltageLimit(self, channels):
        return self._getterChannels(channels, self._lib.PI_qVMA, CDoubleArray)


    def setUpperVoltageLimit(self, channels, upperVoltage):
        self._setterChannels(
            channels, upperVoltage, self._lib.PI_VMA, CDoubleArray)


    def getPosition(self, axesString):
        return self._getterAxes(axesString, self._lib.PI_qPOS, CDoubleArray)


    def getVoltages(self, channels):
        return self._getterChannels(channels, self._lib.PI_qVOL, CDoubleArray)


    def getOpenLoopAxisValue(self, axesString):
        return self._getterAxes(
            axesString, self._lib.PI_qSVA, CDoubleArray)


    def setOpenLoopAxisValue(self, axesString, amplitudeInVolt):
        self._setterAxes(
            axesString, amplitudeInVolt, self._lib.PI_SVA, CDoubleArray)


    def setRelativeOpenLoopAxisValue(self, axesString, offsetInVolt):
        self._setterAxes(
            axesString, offsetInVolt, self._lib.PI_SVR, CDoubleArray)


    def getTargetPosition(self, axesString):
        return self._getterAxes(
            axesString, self._lib.PI_qMOV, CDoubleArray)


    def setTargetPosition(self, axesString, position):
        self._setterAxes(
            axesString, position, self._lib.PI_MOV, CDoubleArray)


    def setTargetRelativeToCurrentPosition(self, axesString, offset):
        self._setterAxes(
            axesString, offset, self._lib.PI_MVR, CDoubleArray)


    def getAllDataRecorderOptions(self):
        bufSize= 1024
        return self._getterReturnString(self._lib.PI_qHDR, bufSize)


    def setDataRecorderConfiguration(self, dataRecorderConfiguration):
        assert isinstance(dataRecorderConfiguration,
                          DataRecorderConfiguration), \
            "argument must be of type DataRecorderConfiguration"

        self._lib.PI_DRC.argtypes= [c_int, CIntArray, c_char_p, CIntArray]

        for tableId in dataRecorderConfiguration.tableIds():
            source= dataRecorderConfiguration.getRecordSource(tableId)
            option= dataRecorderConfiguration.getRecordOption(tableId)
            self._convertErrorToException(
                self._lib.PI_DRC(self._id, tableId, source, option))


    def getDataRecorderConfiguration(self):
        nRecorders= 8
        cfg= DataRecorderConfiguration()

        for i in range(nRecorders):
            source= ctypes.create_string_buffer('\000', 256)
            option= c_int()
            self._convertErrorToException(
                self._lib.PI_qDRC(self._id, i, source, ctypes.byref(option),
                                  1, 1))

            cfg.setTable(i, source, option)
        return cfg


    def getRecordedDataValues(self):
        pass
