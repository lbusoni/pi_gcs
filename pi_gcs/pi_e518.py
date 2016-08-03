from pi_gcs.gcs2 import GeneralCommandSet2


__version__= "$Id: $"




class PhysikInstrumenteE518(object):

    def __init__(self, hostname):
        self._hostname= hostname
        self._gcs= GeneralCommandSet2()
        self._gcs.connectTCPIP(self._hostname)


    def foo(self):
        return 'foo'


    def set(self):
        pass
