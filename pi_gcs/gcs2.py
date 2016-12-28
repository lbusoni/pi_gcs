from ctypes.util import find_library
import ctypes
from ctypes import c_int, c_bool, c_char, c_char_p, c_double, c_uint
import numpy as np
from pi_gcs.data_recorder_configuration import DataRecorderConfiguration
from pi_gcs.abstract_gcs2 import AbstractGeneralCommandSet


__version__= "$Id: $"

CHANNEL_OFFLINE= 0
CHANNEL_ONLINE= 1


class PIException(Exception):
    pass


class PIConnectionError(PIException):
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
        CTypeArray.__init__(self, c_int, np.array(array, dtype=np.int))


class CUnsignedIntArray(CTypeArray):
    def __init__(self, array):
        CTypeArray.__init__(self, c_uint, array)


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



class WaveformGenerator(object):
    CLEAR= 0
    APPEND= 1
    ADD= 2

    ALL= [CLEAR, APPEND, ADD]


class GeneralCommandSet2(AbstractGeneralCommandSet):

    GCS_TRUE= 1
    GCS_FALSE= 0

    def __init__(self):
        self._hostname= None
        self._port= None
        self._lib= None
        self._id= None
        self._axes= ctypes.c_char_p(b"A B C")
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
        s=ctypes.create_string_buffer(b'\000' * bufSize)

        ret= self._lib.PI_TranslateError(
            errorCode, s, bufSize)
        if ret != 1:
            return "Unknown error (%d)" % errorCode
        return "%s (%d)" % (s.value.decode(), errorCode)


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
            gcsFunction(self._id, axesString.encode(), value))
        return value.toNumpyArray()


    def _setterAxes(self, axesString, value, gcsFunction, valueArrayClass):
        nCh= len(axesString.split())
        valueArray= np.atleast_1d(value)
        assert nCh == len(valueArray)
        gcsFunction.argtypes= [c_int, c_char_p, valueArrayClass]
        self._convertErrorToException(
            gcsFunction(self._id, axesString.encode(),
                        valueArrayClass(valueArray)))


    def _getterReturnString(self, gcsFunction, bufSize):
        s=ctypes.create_string_buffer(b'\000', bufSize)
        self._convertErrorToException(
            gcsFunction(self._id, s, bufSize))
        return s.value.decode()


    def _isConnected(self):
        return self._toBool(self._lib.PI_IsConnected(self._id))


    def connectTCPIP(self, hostname, port=50000):
        ide= self._lib.PI_ConnectTCPIP(hostname.encode(), port)
        if ide == -1:
            errorId= self._lib.PI_GetError(ide)
            raise PIConnectionError("%s" % self._errAsString(errorId))
        self._id= ide
        self._hostname= hostname
        self._port= port


    def closeConnection(self):
        try:
            self._lib.PI_CloseConnection(self._id)
        except Exception:
            pass


    def _trickToCheckForSyntaxError(self):
        import time
        time.sleep(0.1)
        self._convertErrorToException(0, 1)


    def gcsCommand(self, commandAsString):
        self._lib.PI_GcsCommandset.argtypes= [c_int, c_char_p]
        self._lib.PI_GcsGetAnswer.argtypes= [c_int, c_char_p, c_int]
        self._convertErrorToException(
            self._lib.PI_GcsCommandset(self._id, commandAsString.encode()))
        self._trickToCheckForSyntaxError()
        retSize= c_int()
        res= ''
        self._convertErrorToException(
            self._lib.PI_GcsGetAnswerSize(self._id, ctypes.byref(retSize)))
        while retSize.value != 0:
            buf= ctypes.create_string_buffer(b'\000', retSize.value)
            self._convertErrorToException(
                self._lib.PI_GcsGetAnswer(self._id, buf, retSize.value))
            res+= buf.value.decode()
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
        return self._getterAxes(
            axesString, self._lib.PI_qSVO, CIntArray).astype(np.bool)


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
        return cRet.value.decode()


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


    def getVolatileMemoryParameters(self, itemId, parameterId):
        self._lib.PI_qSPA.argtypes= [c_int,
                                     c_char_p,
                                     CUnsignedIntArray,
                                     CDoubleArray,
                                     c_char_p,
                                     c_int]
        retValue= CDoubleArray([0.])
        bufSize= 256
        retString= ctypes.create_string_buffer(b'\000', bufSize)

        self._convertErrorToException(
            self._lib.PI_qSPA(
                self._id,
                str(itemId).encode(),
                CUnsignedIntArray([parameterId]),
                retValue,
                retString,
                bufSize))
        return retValue.toNumpyArray()


    def getAllDataRecorderOptions(self):
        bufSize= 1024
        return self._getterReturnString(self._lib.PI_qHDR, bufSize).split('\n')


    def getNumberOfRecorderTables(self):
        return int(self.getVolatileMemoryParameters(1, 0x16000300))


    def setDataRecorderConfiguration(self, dataRecorderConfiguration):
        assert isinstance(dataRecorderConfiguration,
                          DataRecorderConfiguration), \
            "argument must be of type DataRecorderConfiguration"

        self._lib.PI_DRC.argtypes= [c_int, CIntArray, c_char_p, CIntArray]

        for tableId in dataRecorderConfiguration.getTableIds():
            source= dataRecorderConfiguration.getRecordSource(tableId)
            option= dataRecorderConfiguration.getRecordOption(tableId)
            self._convertErrorToException(
                self._lib.PI_DRC(self._id,
                                 CIntArray([tableId]),
                                 source.encode(),
                                 CIntArray([option])))


    def getDataRecorderConfiguration(self):
        nRecorders= self.getNumberOfRecorderTables()
        sourceBufSize= 256
        source= ctypes.create_string_buffer(b'\000', sourceBufSize)
        option= CIntArray(np.zeros(nRecorders, dtype=np.int32))
        table=CIntArray(np.arange(1, nRecorders + 1))

        self._lib.PI_qDRC.argtypes= [c_int, CIntArray, c_char_p,
                                     CIntArray, c_int, c_int]

        self._convertErrorToException(
            self._lib.PI_qDRC(self._id, table, source,
                              option, sourceBufSize, nRecorders))

        sources= [x.strip() for x in source.value.decode().split('\n')]
        cfg= DataRecorderConfiguration()
        for i in range(nRecorders):
            cfg.setTable(table.toNumpyArray()[i],
                         sources[i],
                         option.toNumpyArray()[i])
        return cfg


    def getRecordedDataValues(self, howManyPoints, startFromPoint=1):
        nRecorders= self.getNumberOfRecorderTables()
        value= CDoubleArray(np.zeros(howManyPoints))
        retBuf= np.zeros((nRecorders, howManyPoints))
        self._lib.PI_qDRR_SYNC.argtypes=[c_int, c_int, c_int,
                                         c_int, CDoubleArray]

        for i in range(nRecorders):
            self._convertErrorToException(
                self._lib.PI_qDRR_SYNC(
                    self._id, i + 1, startFromPoint,
                    len(value.toNumpyArray()), value))
            retBuf[i, :]= value.toNumpyArray()

        return retBuf


    def startRecordingInSyncWithWaveGenerator(self):
        self._convertErrorToException(
            self._lib.PI_WGR(self._id))


    def getNumberOfWaveGenerators(self):
        return 3


    def getWaveGeneratorStartStopMode(self):
        nWaveGenerators= self.getNumberOfWaveGenerators()
        self._lib.PI_qWGO.argtypes= [c_int, CIntArray, CIntArray, c_int]
        wgIds= CIntArray(np.arange(1, nWaveGenerators+ 1))
        values= CIntArray(np.zeros(nWaveGenerators))
        self._convertErrorToException(
            self._lib.PI_qWGO(self._id, wgIds, values, nWaveGenerators))
        return values.toNumpyArray()


    def setWaveGeneratorStartStopMode(self, startModeArray):
        nWaveGenerators= self.getNumberOfWaveGenerators()
        self._lib.PI_WGO.argtypes= [c_int, CIntArray, CIntArray, c_int]
        wgIds= CIntArray(np.arange(1, nWaveGenerators+ 1))
        values= CIntArray(startModeArray)
        self._convertErrorToException(
            self._lib.PI_WGO(self._id, wgIds, values, nWaveGenerators))


    def clearWaveTableData(self, waveTableIdsArray):
        self._lib.PI_WCL.argtypes= [c_int, CIntArray, c_int]
        table= CIntArray(waveTableIdsArray)
        self._convertErrorToException(
            self._lib.PI_WCL(self._id, table, len(waveTableIdsArray)))


    def getConnectionOfWaveTableToWaveGenerator(self, waveGeneratorsArray):
        self._lib.PI_qWSL.argtypes= [c_int, CIntArray, CIntArray, c_int]
        nItems= len(waveGeneratorsArray)
        waveGenerators= CIntArray(waveGeneratorsArray)
        waveTable= CIntArray(np.zeros(nItems))
        self._convertErrorToException(
            self._lib.PI_qWSL(self._id,
                              waveGenerators,
                              waveTable,
                              nItems))
        return waveTable.toNumpyArray()


    def setConnectionOfWaveTableToWaveGenerator(self,
                                                waveGeneratorsArray,
                                                waveTableIdsArray):
        assert len(waveGeneratorsArray) == len(waveTableIdsArray)
        self._lib.PI_WSL.argtypes= [c_int, CIntArray, CIntArray, c_int]
        waveGenerators= CIntArray(waveGeneratorsArray)
        waveTable= CIntArray(waveTableIdsArray)
        self._convertErrorToException(
            self._lib.PI_WSL(self._id,
                             waveGenerators,
                             waveTable,
                             len(waveTableIdsArray)))




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
        assert append in WaveformGenerator.ALL

        self._lib.PI_WAV_SIN_P.argtypes= [c_int, c_int, c_int, c_int, c_int,
                                          c_int, c_double, c_double, c_int]
        self._convertErrorToException(
            self._lib.PI_WAV_SIN_P(self._id,
                                   waveTableId,
                                   int(startPoint),
                                   int(wavelengthOfTheSineCurveInPoints),
                                   append,
                                   int(curveCenterPoint),
                                   amplitudeOfTheSineCurve,
                                   offsetOfTheSineCurve,
                                   int(lengthInPoints)))



    def setRecordTableRate(self, recordTableRateInServoLoopCycles=1):
        self._lib.PI_RTR.argtypes= [c_int, c_int]
        self._convertErrorToException(
            self._lib.PI_RTR(self._id, int(recordTableRateInServoLoopCycles)))


    def getRecordTableRate(self):
        rtr= c_int()
        self._convertErrorToException(
            self._lib.PI_qRTR(self._id, ctypes.byref(rtr)))
        return rtr


    def getServoUpdateTimeInSeconds(self):
        return self.getVolatileMemoryParameters(1, 0x0E000200)




    def setWaveGeneratorTableRate(self,
                                  waveGeneratorTableRateInServoLoopCycles):
        self._lib.PI_WTR.argtypes= [c_int, CIntArray, CIntArray,
                                    CIntArray, c_int]
        nWaveGenerators= self.getNumberOfWaveGenerators()
        wgIds= CIntArray(np.arange(1, nWaveGenerators+ 1))
        tableRate= CIntArray(waveGeneratorTableRateInServoLoopCycles)
        interpolation= CIntArray(np.zeros(nWaveGenerators))

        self._convertErrorToException(
            self._lib.PI_WTR(self._id,
                             wgIds,
                             tableRate,
                             interpolation,
                             nWaveGenerators))


    def getWaveGeneratorTableRate(self):
        self._lib.PI_qWTR.argtypes= [c_int, CIntArray, CIntArray,
                                     CIntArray, c_int]

        nWaveGenerators= self.getNumberOfWaveGenerators()
        wgIds= CIntArray(np.arange(1, nWaveGenerators+ 1))
        tableRate= CIntArray(np.zeros(nWaveGenerators))
        interpolation= CIntArray(np.zeros(nWaveGenerators))
        self._convertErrorToException(
            self._lib.PI_qWTR(self._id,
                              wgIds,
                              tableRate,
                              interpolation,
                              nWaveGenerators))
        return tableRate.toNumpyArray()


    def getOverflowState(self, axesString):
        return self._getterAxes(
            axesString, self._lib.PI_qOVF, CIntArray).astype(np.bool)


    def setDataRecoderTriggerSource(self, source, value):
        pass


    def getDataRecorderTriggerSource(self):
        pass
