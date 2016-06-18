from pi_gcs import GeneralCommandSet2


__version__= "$Id: $"


class PI_E518(object):

    def __init__(self, hostname):
        self._hostname= hostname
        self._gcs= GeneralCommandSet2()
        self._gcs.connectTCPIP(self._hostname)


    def foo(self):
        return 'foo'




