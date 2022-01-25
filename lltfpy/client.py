from logging import getLogger
from .lltf import LLTFError
import requests
_DEFAULT_TIMEOUT = 1
_DEFAULT_URL = 'localhost:50000/lltf'


class LLTFClient:
    def __init__(self, address=_DEFAULT_URL, timeout=_DEFAULT_TIMEOUT):
        self.address = address
        self.timeout = timeout

    def get_wavelength(self):
        """
        Client side function: Gets current wavelength

        Returns wavelength or raises error
        """
        w = self.status['wavelength']
        try:
            w = float(w)
            return w
        except ValueError:  #will be an error when w isn't valid
            raise LLTFError(w)

    def set_wavelength(self, x):
        """
        Client side function: sets the wavelength

        Returns true iff successful
        """
        try:
            r = requests.post(self.address, json={'command': 'set_wave', 'data':x}, timeout=self.timeout)
        except requests.exceptions.ConnectionError:
            raise LLTFError('HTTPConnectionError')
        if not r.ok:
            #extract error from r
            error = 'undetermined'
            raise LLTFError(error)
        return True

    def status(self):
        """
        Client side function: returns LLTF status

        Returns:
            dictionary of status information
        """
        try:
            r = requests.post(self.address, json={'command': 'status'}, timeout=self.timeout)
            return r.json()
        except requests.exceptions.ConnectionError:
            raise LLTFError('HTTPConnectionError')
