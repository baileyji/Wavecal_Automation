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
        
    def NKT.Open(self, peHandle, conffile, name):
        """
        Opens communication channel with system
        
        """
        #Acquire handle on LLTF Contrast
        peCreate = library.PE_Create
        peCreate.argtypes = [c_char_p, ctypes.POINTER(PESTATUS)]
        peCreate.restypes = [PE_STATUS]
        peCreate(conffile, peHandle)
        
        #Open communication channel
        peOpen = library.PE_Open
        peOpen.argtypes[PE_HANDLE, c_char_p]
        peOpen.restypes[PE_STATUS]
        return peOpen(peHandle, name)
    
    def NKT.Status(self, code):
        """
        Gets status of the instrument (PE_STATUS)
        
        """
        peGetStatusStr = library.PEGetStatusStr
        peGetStatusStr.argtypes = [PE_STATUS]
        peGetStatusStr.restypes = c_char_p
        return pegetstatusstr(code)
        
    def NKT.Wavelength(self, peHandle, wavelength):
        """
        Returns the central wavelength filtered by the system in nanometers.

        """
        peGetWavelength = library.PE_GetWavelength
        peGetWavelength.argtypes = [CPE_HANDLE, c_double_p]
        peGetWavelength.restypes = PE_STATUS
        peGetWavelength(peHandle, wavelength)
        
    def NKT.Calibrate(self):
        """
        Calibrates the instrument (Not sure which pe function i use here)
        
        """
        
    def NKT.Close(self, peHandle):
        """
        Closes communication channel with system

        """
        #Close communication channel
        peClose = library.PE_Close
        peClose.argtypes = PE_HANDLE
        peClose.restypes = PE_STATUS
        peClose(peHandle)
        
        #Destroys filter resource created with PE_Create
        peDestroy = library.PE_Destroy
        peDestroy.argtypes = PE_HANDLE
        peDestroy.restypes = PE_STATUS
        return peDestroy(peHandle)
        
if __name__ == '__main__':
    #from flask import Flask
    #Argparse here. Takes some arguments.
    pe_open
    #...
    #Close file
    #PE_DESTROY. Destroys the environment
