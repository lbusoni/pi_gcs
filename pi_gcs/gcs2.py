from ctypes.util import find_library
import ctypes
from ctypes import c_int, c_bool, c_char
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


class CBoolArray(CTypeArray):
    def __init__(self, array):
        CTypeArray.__init__(self, c_bool, array)


class CCharArray(CTypeArray):
    def __init__(self, array):
        CTypeArray.__init__(self, c_char, array)



class Channels(CIntArray):
    def __init__(self, channels):
        CIntArray.__init__(self, channels)


class Axes(CCharArray):
    def __init__(self, axes):
        CCharArray.__init__(self, axes)


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


    def _convertErrorToException(self, returnValue, expectedReturn=TRUE):
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


    def getServoControlMode(self, axes):
        svo= CBoolArray([False]* len(axes))
        self._lib.PI_qSVO.argtypes= [c_int, Axes, CBoolArray]
        self._convertErrorToException(
            self._lib.PI_qSVO(self._id, Axes(axes), svo))
        return svo.toNumpyArray()



    def getControlMode(self, channels):
        retArray= CIntArray([CHANNEL_OFFLINE]* len(channels))
        self._lib.PI_qONL.argtypes= [c_int, Channels, CIntArray, c_int]
        self._convertErrorToException(
            self._lib.PI_qONL(self._id,
                              Channels(channels),
                              retArray,
                              len(channels)))
        return retArray.toNumpyArray()


    def setControlMode(self, channels, controlMode):
        assert len(channels) == len(controlMode)
        ctrl= CIntArray(controlMode)
        self._lib.PI_ONL.argtypes= [c_int, Channels, CIntArray, c_int]
        self._convertErrorToException(
            self._lib.PI_ONL(self._id,
                             Channels(channels),
                             ctrl,
                             len(channels)))


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
