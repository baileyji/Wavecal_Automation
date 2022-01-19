# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 12:06:19 2022

@author: autum
"""
from Wavecal_Automation.rough_draft_noprintst import NKTContrast
from Wavecal_Automation.rough_draft_noprintst import PE_STATUS

class LLFT():
    """
    
    Hardware class for connection to the LLTF High Contrast filter.
    
    """
    
    def __init__(self, conffile):
        self._conn = None 
        
    def _open(self, index=0):
        """
        
        Creates and opens connection with the system.
        
        Parameters
            conffile (Required) - Path to configuration file. 
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            index (Optional) - Position of the system. Default is zero.
       
        """
        if self._conn is None:           
            try:
                conffile = self.conffile
                library_vers, num_sys, peHandle, name, create_status, open_status = NKTContrast.NKT_Open(conffile, index)
                if not create_status == PE_STATUS.PE_SUCCESS:
                    raise RuntimeError('Unable to create handle.')   
                if not open_status == PE_STATUS.PE_SUCCESS:
                    raise RuntimeError('Unable to open system.')            
                print('Communication channel opened.', '\n', 
                     'Library Version:', library_vers, '\n', 
                     'Number of systems:', num_sys, '\n',
                     'Handle to the system:', peHandle, '\n', 
                     'System name:', name)
                self._conn = peHandle
                return self._conn
            except:
                print('Could not connect to system.')
        else:
            print('System already open.')
            
    def _close(self):
        """
        
        Closes connection with system.

        """
        if self._conn is not None:
            try:
                closestatus, destroystatus = NKTContrast.NKT_Close()  
                if not closestatus == PE_STATUS.PE_SUCCESS:
                    raise RuntimeError('Unable to close system. \n, Error:', closestatus)
                if not destroystatus == PE_STATUS.PE_SUCCESS:
                    raise RuntimeError('Unable to destroy system. \n, Error:', destroystatus)
                self._conn = None  
                print('System successfully closed and destroyed!')
            except:
                print('Could not close system.')
        
    def set_wave(self, wavelength):
        """
        
        Calibrates central wavelength of the filter.
        
        Parameters
            conffile (Required) - Path to configuration file. 
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            wavelength (Required) - Desired central wavelength in nm

        """
        close = False
        try:
            peHandle = self._open()
            prev_wave, prev_min, prev_max, wavestatus, rangestatus = NKTContrast.NKT_Wavelength(peHandle)
            print('Current central wavelength:', prev_wave, '/n',
                  'Current wavelength range:', prev_min, 'to', prev_max)
            new_wave, new_wavestatus, new_rangestatus = NKTContrast.NKT_Calibrate(peHandle, wavelength)
            print('New central wavelength:', new_wave)
            return True
        except wavestatus or rangestatus or new_wavestatus or new_rangestatus != PE_STATUS.PE_SUCCESS:
            close = True
            print('Calibration could not occur.')
        except wavelength == prev_wave:
            close = True
            print('Already calibrated to', wavelength)
        except new_wave == prev_wave:
            close = True
            print("Calibration didn't occur. Still at", new_wave)
        finally:
            if close:
                self._close()
        return False
    
    def get_wave(self):
        """
        Returns current central wavelength and wavelength range of filter.
        
        Parameters
            conffile (Required) - Path to configuration file. 
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'

        """
        close=False
        try:
            peHandle = self._open()
            wave, minimum, maximum, wavestatus, rangestatus = NKTContrast.NKT_Wavelength(peHandle)
            print('Central wavelength:', wave, '/n',
                  'Wavelength range:', minimum, 'to', maximum)
            return True
        except wavestatus or rangestatus != PE_STATUS.PE_SUCCESS:
            close = True
            print('Calibration could not occur.')
        finally:
            if close:
                self._close()
        return False
    
    def grating_wave(self, wavelength):
        pass