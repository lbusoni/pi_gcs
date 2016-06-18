from ctypes.util import find_library
import ctypes
import numpy as np


__version__= "$Id: $"


class PIException(Exception):
    pass


class ConnectionError(PIException):
    pass


class GeneralCommandSet2(object):

    def __init__(self):
        self._hostname= None
        self._port= None
        self._lib= None
        self._id= None
        self._axes= ctypes.c_char_p("A B C")
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
        return s.value

        ret= self._lib.PI_TranslateError(
            errorCode, ctypes.byref(s), bufSize)
        if ret != 1:
            return "Unknown error (%d)" % errorCode
        return "%s (%d)" % (ret.value, errorCode)


    def _convertErrorToException(self, returnValue, expectedReturn=1):
        if returnValue != expectedReturn:
            errorId= self._lib.PI_GetError(self._id)
            if errorId != 0:
                raise PIException("%s" % self._errAsString(errorId))


    def _convertCBoolArrayToNumpyArray(self, cBoolArray):
        return np.array([x for x in cBoolArray])


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
        return self._convertCBoolArrayToNumpyArray(svo)

