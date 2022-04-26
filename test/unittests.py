"""
Unit tests for lltfpy/lltf.py.

"""

import unittest
from ..lltfpy.lltf import LLTF, PE_STATUS


class Test(unittest.TestCase):
    """
    Tests LLTF functions.
    
    """

    def setUp(self):
        """
        Create class instance of LLTF.

        """
        self.conffile = input('Config file: ')
        self.conffile.encode('ASCII')
        self.lltf = LLTF(conffile=self.conffile)


    def tearDown(self):
        """
        Close and destroy system at end.
        
        """
        self.lltf._close()
        
        
    def handle_is_open(self):
        """
        Tests that system is closed if left open without closing.
        Asserts that handles retrieved after opening twice are not equal.
        
        """
        self.lltf._open()
        handle = self.lltf.handle
        self.lltf._open()
        new_handle = self.lltf.handle
        self.assertnotEqual(new_handle, handle)
       
        
    def handle_not_open(self):
        """
        Tests that handle is returned from LLTF._open() when self.handle = None.
        
        """
        self.lltf._open()
        self.assertTrue(self.lltf.handle)
    
        
    def invalid_handle(self):
        """
        Tests that handle is deleted if invalid.
        Also asserts a ValueError is raised.
       
        """
        #Make an invalid handle
        self.lltf.handle = 'HANDLE'
        with self.assertRaises(ValueError) as context:
            self.lltf._open()
        self.assertFalse(self.lltf.handle)
        self.assertEqual(str(context.exception), 'Invalid handle: PE_STATUS.PE_INVALID_HANDLE')
        
        
    def close_with_no_handle(self):
        """
        Tests that proper logging message is retrieved upon closing with no handle.
    
        """
        with self.assertLogs(level='DEBUG') as captured:
            self.lltf._close()
        self.assertEqual(captured.records[0].getMessage(), 'Already closed.')
    
    
    def close_with_handle(self):
        """
        Tests if handle is None when system is closed properly.

        """
        self.lltf._open()
        self.lltf_close()
        self.assertFalse(self.lltf.handle)
    
    
    def wave_same_as_original(self):
        """
        https://pythonin1minute.com/how-to-test-logging-in-python/
        
        Check that getLogger returns appropriate message when someone tries to input the 
            wavelength that is already set.
        
        """
        status = self.lltf.status()
        wavelength = status['central_wavelength']
        message = 'Wavelength already set:', wavelength, 'nm'
        with self.assertLogs(level='DEBUG') as captured:
            self.lltf.set_wave(wavelength=wavelength)
        self.assertEqual(str(captured.records[0].getMessage()), str(message))


    def wave_out_of_range(self):
        """
        Check that proper ValueError is used when wavelength is out of range of the filter.

        """
        wavelength = 100
        with self.assertRaises(ValueError) as context:
            self.lltf.set_wave(wavelength=wavelength)
        self.assertEqual(str(context.exception), 'Invalid input wavelength:' + 'Requested wavelength is out of bounds.')
    
    
    def wave_correctly_set(self):
        """
        Check that wavelength gets properly set by asserting that status returns the set wavelength.
        
        """
        wavelength = 1000
        self.lltf.set_wave(wavelength=wavelength)
        status = self.lltf.status()
        self.assertEqual(status['central_wavelength'], wavelength)
    
    
    def grating_not_retrieved(self):
        """
        Tests that proper ValueError is raised if grating isn't retrieved.

        """
        self.lltf._open()
        gratingIndex = None
        with self.assertRaises(ValueError) as context:
            minimum, maximum, extended_min, extended_max = self.lltf._grating_wave(gratingIndex=gratingIndex)
        self.assertEqual(str(context.exception), 'Grating index not found.')
        
        
    def incorrect_key_value(self):
        """
        Tests that if an incorrect key is returned, an error statement is printed but no error is returned.

        """
        wavelength = self.lltf._get_wave()
        self.assertEqual(wavelength, 'Could not retrieve wavelength:' + 'Supplied handle is corrupted or has a NULL value.')
        
        
if __name__ == '__main__':
    unittest.main()