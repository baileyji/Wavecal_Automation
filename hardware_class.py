# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 12:06:19 2022

@author: autum
"""
from Wavecal_Automation.rough_draft_noprintst import NKTContrast
from Wavecal_Automation.rough_draft_noprintst import PE_STATUS

class LLFT():
    """
    """
    
    def __init__(self, conffile):
        self._conn = None 
        
    def _open(self, index=0):
        """
        

        Parameters
        ----------
        index : TYPE, optional
            DESCRIPTION. The default is 0.

        Raises
        ------
        Exception
            DESCRIPTION.
        RuntimeError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if self._conn is None:           
            try:
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
                return peHandle
            except:
                print('Could not connect to system.')
        else:
            print('System already open.')
            
    def _close(self):
        """
        

        Raises
        ------
        RuntimeError
            DESCRIPTION.

        Returns
        -------
        None.

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
        close = False
        try:
            peHandle = self._open()
            prev_wave, prev_min, prev_max, wavestatus, rangestatus = NKTContrast.NKT_Wavelength(peHandle)
            print('Current central wavelength:', prev_wave, '/n',
                  'Current wavelength range:', prev_min, 'to', prev_max)
            newwave, newwavestatus, newrangestatus = NKTContrast.NKT_Calibrate(peHandle, wavelength)
        except wavestatus or rangestatus or newwavestatus or newrangestatus != PESTATUS.PE_SUCCESS:
            close = True
            print('Calibration could not occur.')
        #Continue writing more excepts...
            
    def get_wave(self):
        close=False
        try:
            peHandle = self._open()
        
    def grating_wave(self, wavelength):