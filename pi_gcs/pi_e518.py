from pi_gcs.gcs2 import GeneralCommandSet2


__version__= "$Id: $"




class PhysikInstrumenteE518Client(object):

    def __init__(self, hostname, generalCommandSet):
        self._hostname= hostname
        self._generalCommandSet= generalCommandSet


    def foo(self):
        return 'foo'


    def connect(self):
        self.connectTCPIP(self._hostname)
