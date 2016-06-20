from ctypes.util import find_library
import ctypes
from ctypes import c_int, c_char_p
import numpy as np


__version__= "$Id: $"

CHANNEL_OFFLINE= 0
CHANNEL_ONLINE= 1
TRUE= 1
FALSE= 0


class PIException(Exception):
    pass


class ConnectionError(PIException):
    pass


class CTypeArray():

    def __init__(self, ctype, array):
        assert isinstance(array, (np.ndarray, list, tuple))
        self._ctype= ctype
        self._array= array

    def from_param(self):
        ret= (self._ctype * len(self._array))()
        for i in range(len(self._array)):
            ret[i]= self._array[i]
        return ret


class CIntArray(CTypeArray):
    def __init__(self, array):
        CTypeArray.__init__(self, c_int, array)


class Channels(CIntArray):
    def __init__(self, channels):
        CIntArray.__init__(self, channels)




class Axis():
    pass


class GeneralCommandSet2(object):


    def __init__(self):
        self._hostname= None
        self._port= None
        self._lib= None
        self._id= None
        self._axes= ctypes.c_char_p("A B C")
        self._channels= (ctypes.c_int * 3)(1, 2, 3)

        self._importLibrary()


    def _importLibrary(self):
        piLibName= 'pi_pi_gcs2-3.5.1'
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


    def _convertErrorToException(self, returnValue, expectedReturn=TRUE):
        if returnValue != expectedReturn:
            errorId= self._lib.PI_GetError(self._id)
            if errorId != 0:
                raise PIException("%s" % self._errAsString(errorId))


    def _convertCArrayToNumpyArray(self, cArray):
        return np.array([x for x in cArray])


    def _toBool(self, value):
        assert value in [0, 1]
        return True if value == 1 else False


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


    def getVersion(self):
        bufSize= 256
        s=ctypes.create_string_buffer('\000' * bufSize)
        self._convertErrorToException(
            self._lib.PI_qVER(self._id, ctypes.byref(s), bufSize))
        return s.value


    def getPosition(self):
        pass


    def getServoControlMode(self):
        cBoolArray= ctypes.c_bool * 3
        svo=cBoolArray(False, False, False)
        self._convertErrorToException(
            self._lib.PI_qSVO(self._id, self._axes, svo))
        return self._convertCArrayToNumpyArray(svo)



    def enableControlMode(self, channels):
        enable= CIntArray([CHANNEL_ONLINE]* len(channels))
        self._lib.PI_ONL.argtypes= [c_int, Channels, CIntArray, c_int]
        self._convertErrorToException(
            self._lib.PI_ONL(self._id,
                             Channels(channels),
                             enable,
                             len(channels)))


    def disableControlMode(self, channels):
        disable= CIntArray([CHANNEL_OFFLINE]* len(channels))
        self._lib.PI_ONL.argtypes= [c_int, Channels, CIntArray, c_int]
        self._convertErrorToException(
            self._lib.PI_ONL(self._id,
                             Channels(channels),
                             disable,
                             len(channels)))


    def getControlMode(self, channels):
        retArray= CIntArray([CHANNEL_OFFLINE]* len(channels))
        self._lib.PI_qONL.argtypes= [c_int, Channels, CIntArray, c_int]
        self._convertErrorToException(
            self._lib.PI_qONL(self._id,
                              Channels(channels),
                              retArray,
                              len(channels)))
        return self._convertCArrayToNumpyArray(retArray)


    def echo(self, message):
        cMsg= ctypes.create_string_buffer(message)
        cRet= ctypes.create_string_buffer(0, ctypes.sizeof(cMsg))
        self._convertErrorToException(
            self._lib.PI_qECO(self._id, cMsg, cRet))
        return cRet.value


    def gcsCommand(self, commandAsString):
        self._lib.PI_GcsCommandset.argtypes= [c_int, c_char_p]
        self._lib.PI_GcsGetAnswer.argtypes= [c_int, c_char_p, c_int]
        self._convertErrorToException(
            self._lib.PI_GcsCommandset(self._id, commandAsString))
        retSize= c_int(1)
        res= ''
        while retSize.value != 0:
            self._convertErrorToException(
                self._lib.PI_GcsGetAnswerSize(self._id, ctypes.byref(retSize)))
            buf= ctypes.create_string_buffer(0, retSize.value)
            self._convertErrorToException(
                self._lib.PI_GcsGetAnswer(self._id, buf, retSize.value))
            res+= buf.value
        return res


