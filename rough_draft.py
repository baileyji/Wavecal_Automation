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
    Before performing any functions, please start connection with NKT_Open.
    ------
    After you're done, please close communications using NKT_Close.
    
    """
    def __init__(self):
        self.conffile = conffile
        
    def NKT_Open(self, conffile):
        """
        Opens communication channel with system
        
        Inputs:
            index - Position of the system
        """
        #Acquire handle on LLTF Contrast
        pe_Create = library.PE_Create
        pe_Create.argtypes = [c_char_p, POINTER(PESTATUS)]
        pe_Create.restypes = PE_STATUS
        
        #Retrieves system name
        pe_GetSystemName = library.PE_GetSystemName
        pe_GetSystemName.argtypes = [CPE_HANDLE, c_int, c_char_p]
        
        #Retrieves version number of library
        pe_LibraryVersion = library.PE_GetLibraryVersion
        pe_LibraryVersion.restypes = c_int
                
        #Open communication channel
        pe_Open = library.PE_Open
        pe_Open.argtypes = [PE_HANDLE, c_char_p]
        pe_Open.restypes = PE_STATUS
        
        try:
            peHandle = PE_HANDLE
            name = c_char_p
            index = 
            size = 
            pe_Create(conffile, byref(peHandle))
            pe_GetSystemName(peHandle, index, byref(name), size)
        except:
            pass
    
    def NKT_Status(self, code):
        """
        Gets status of the current process.
        
        """
        pe_GetStatusStr = library.PE_GetStatusStr
        pe_GetStatusStr.argtypes = [PE_STATUS]
        pe_GetStatusStr.restypes = c_char_p
        
        
    def NKT_Wavelength(self):
        """
        Returns the central wavelength and the wavelength range.
        
        """
        #Returns the central wavelength filtered by the system in nanometers
        pe_GetWavelength = library.PE_GetWavelength
        pe_GetWavelength.argtypes = [CPE_HANDLE, c_double_p]
        pe_GetWavelength.restypes = PE_STATUS
        
        #Retrieves wavelength range of system in nanometers
        pe_GetWavelengthRange = library.pe_GetWavelengthRange
        pe_GetWavelengthRange.argtypes = [CPE_HANDLE, c_double_p]
        pe_GetWavelengthRange.restypes = PE_STATUS
        
    def NKT_Calibrate(self):
        """
        Calibrates the instrument.
        
        """
        #Sets central wavelength filtered by system in nanometers
        pe_SetWavelength = library.PE_SetWavelength
        pe_SetWavelength.argtypes = [PE_HANDLE, c_double]
        pe_SetWavelength.restypes = PE_STATUS
        
    def NKT_GratingStatus(self):
        """
        Retrieves information about the grating specified by the index, 
        including the wavelength range.
        
        """
        
        #Retrieves grating name
        pe_GetGratingName = library.PE_GetGratingName
        pe_GetGratingName.argtypes = [c_int, CPE_HANDLE, c_char_p]
        pe_GetGratingName.restypes = PE_STATUS
        
        #Retrieves system's grating count number
        pe_GetGratingCount = library.PE_getGratingCount
        pe_GetGratingCount.argtypes = [CPE_HANDLE, POINTER(c_int)]
        pe_GetGratingCount.restypes = PE_STATUS
        
        #Retrieve wavelength range of grating in nanometers
        pe_GetGratingWavelengthRange = library.PE_GetGratingWavelengthRange
        pe_GetGratingWavelengthRange.argtypes = [CPE_HANDLE, c_int, c_double_p]
        pe_GetGratingWavelengthRange.restypes = PE_STATUS
        
        #Retrieve extended wavelength range of grating in nanometers
        pe_GetGratingWavelengthExtendedRange = library.PE_GetGratingWavelengthExtendedRange
        pe_GetGratingWavelengthExtendedRange.argtypes = [CPE_HANDLE, c_int, c_double_p]
        pe_GetGratingWavelengthExtendedRange.restypes = PE_STATUS
        
    def NKT_CalibrateGrating(self):
        """
        Calibrates the central wavelength of the grating.

        """
        #Retrieves grating
        pe_GetGrating = library.PE_GetGrating
        pe_GetGrating.argtypes = [PE_HANDLE, POINTER(c_int)]
        pe_GetGrating.restypes = PE_STATUS
        
        #Sets central wavelength filtered by system in nanometers
        pe_SetWavelengthOnGrating = library.PE_SetWavelengthOnGrating 
        pe_SetWavelengthOnGrating.argtypes = [PE_HANDLE, c_int, c_double]
        pe_SetWavelengthOnGrating.restypes = PE_STATUS
        
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