import unittest
from ..lltfpy.lltf import LLTF, PE_STATUS


class Test(unittest.TestCase):
    
    def __init__(self):
        pass

    def setUp(self):
        """
        Create class instance of LLTF.

        """
        self.conffile = 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
        self.lltf = LLTF(conffile=self.conffile)


    def tearDown(self):
        """
        Close and destroy system at end.
        
        """
        self.lltf._close()
        
        
    def handle_is_open(self):
        """
        Tests that system is closed if left open without closing.
        
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
       
        """
        #Make an invalid handle
        self.lltf.handle = 0
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
        
        Check that getLogger prints appropriate message when someone tries to input the 
            wavelength that is already set.
        
        """
        status = self.lltf.status()
        wavelength = status['central_wavelength']
        message = 'Wavelength already set:', wavelength, 'nm'
        with self.assertLogs(level='DEBUG') as captured:
            self.lltf.set_wave(wavelength=wavelength)
        self.assertEqual(captured.records[0].getMessage(), message)


    def wave_out_of_range(self):
        """
        Check that proper IOError is used when wavelength is out of range of the filter.

        """
        wavelength = 100
        with self.assertRaises(ValueError) as context:
            self.lltf.set_wave(wavelength=wavelength)
        self.assertEqual(str(context.exception), 'Invalid input wavelength: PE_STATUS.PE_INVALID_WAVELENGTH')
    
    
    def wave_correctly_set(self):
        """
        Check that wavelength gets properly set.
        
        """
        wavelength = 600
        self.lltf.set_wave(wavelength=wavelength)
        status = self.lltf.status()
        self.assertEqual(status['central_wavelength'], wavelength)
    
    
    def grating_not_retrieved(self):
        """
        Tests that proper error is raised if grating isn't retrieved.

        """
        self.lltf._open()
        gratingIndex = None
        with self.assertRaises(ValueError) as context:
            self.lltf._grating_wave(gratingIndex=gratingIndex)
        self.assertEqual(str(context.exception), 'Grating index not found.')
        
if __name__ == '__main__':
    unittest.main()