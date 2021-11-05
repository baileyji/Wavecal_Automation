# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 22:18:35 2021
@author: Maile Sasaki
This code is for the ease of communication with the LLTF Contrast at the Subaru Observatory.
"""

from ctypes import *
from sys import platform
import os
from enum import IntEnum

#Checking which dll file to use.
if platform.startswith('win64'):
    lib_path = './win64/PE_Filter_SDK.dll'
elif platform.startswith('win32'):
    lib_path = './win32/PE_Filter_SDK.dll'
else:
    raise Exception('Not running on a Windows platform. Please retry.')
    
#Loading dll file with ctypes
try:
    library = CDLL(lib_path)
    print('Successfully loaded', library)
except Exception as excep:
    print(excep, 'Could not load .dll file.')

#Look for config file. user_conffile is put in by user, maybe as argument.
try:
    conffile = user_conffile
    
except Exception as excep:
    print(excep, 'Configuration file not found.')
    
class PE_STATUS(IntEnum):
    """
    Passes enums in c into Python
    
    """
    PE_SUCCESS = 0
    PE_INVALID_HANDLE = 1
    PE_FAILURE = 2
    PE_MISSING_CONFIGFILE = 3
    PE_INVALID_CONFIGURATION = 4
    PE_INVALID_WAVELENGTH = 5
    PE_MISSING_HARMONIC_FILTER = 6
    PE_INVALID_FILTER = 7
    PE_UNKNOWN = 8
    PE_INVALID_GRATING = 9
    PE_INVALID_BUFFER = 10
    PE_INVALID_BUFFER_SIZE = 11
    PE_UNSUPPORTED_CONFIGURATION = 12
    PE_NO_FILTER_CONNECTED = 13
    
    def __init__(self, value):
        self._as_parameter_ = int(value)

class PE_HANDLE:
    def __init__(self, c_void_p):
        self._as_parameter_ = c_void_p
        
class CPE_HANDLE:
    def __init__(self, c_void_p):
        self._as_parameter_ = c_void_p
        
class NKTContrast():
    """
    This class performs various functions in the NKT Photon instrument.
    ------
    Before performing any functions, please start connection with pe_open.
    ------
    After you're done, please close communications using pe_close.
    
    """
    def __init__(self):
        pass
        
    def NKT_Open(self):
        """
        Opens communication channel with system
        
        """
        #Acquire handle on LLTF Contrast
        pe_Create = library.PE_Create
        pe_Create.argtypes = [c_char_p, ctypes.POINTER(PESTATUS)]
        pe_Create.restypes = [PE_STATUS]
        
        #Open communication channel
        pe_Open = library.PE_Open
        pe_Open.argtypes[PE_HANDLE, c_char_p]
        pe_Open.restypes[PE_STATUS]
    
    def NKT_Status(self, code):
        """
        Gets status of the instrument.
        
        """
        
        pe_GetStatusStr = library.PE_GetStatusStr
        pe_GetStatusStr.argtypes = [PE_STATUS]
        pe_GetStatusStr.restypes = c_char_p
        
        pe_GetSystemName = library.PE_GetSystemName
        pe_GetSystemName.argtypes[CPE_HANDLE, c_int, c_char_p]
        
    def NKT_Wavelength(self):
        """
        Returns the central wavelength filtered by the system in nanometers.
        """
        pe_GetWavelength = library.PE_GetWavelength
        pe_GetWavelength.argtypes = [CPE_HANDLE, c_double_p]
        pe_GetWavelength.restypes = PE_STATUS
        
        pe_GetWavelengthRange = library.pe_GetWavelengthRange
        pe_GetWavelengthRange.argtypes = [CPE_HANDLE, c_double_p]
        pe_GetWavelengthRange.restypes = PE_STATUS
        
    def NKT_Calibrate(self):
        """
        Calibrates the instrument
        
        """
        
    def NKT_GratingWavelength(self):
        """
        Retrieves the wavelength range of the grating specified by index.
        
        """
    def NKT_CalibrateGrating(self):
        """
        Calibrates the central wavelength of the grating.

        """
    def NKT_Close(self):
        """
        Closes communication channel with system
        """
        #Close communication channel
        pe_Close = library.PE_Close
        pe_Close.argtypes = PE_HANDLE
        pe_Close.restypes = PE_STATUS
        
        #Destroys filter resource created with PE_Create
        pe_Destroy = library.PE_Destroy
        pe_Destroy.argtypes = PE_HANDLE
        pe_Destroy.restypes = PE_STATUS
        
        
if __name__ == '__main__':
    #from flask import Flask
    #Argparse here. Takes some arguments.
    
    #...
    #Close file
    #PE_DESTROY. Destroys the environment