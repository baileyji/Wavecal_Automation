# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 22:18:35 2021

@author: Maile Sasaki

This code is for the ease of communication with the LLTF Contrast at the Subaru Observatory.
"""

from ctypes import *
from sys import platform
import os

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

#Look for config file. Maybe make this an argument so user can plug in their own config file?
try:
    os.path.isfile('C:\Program Files (x86)\Photon etc\PHySpecV2/system.xml')
except Exception as excep:
    print(excep, 'Configuration file not found.')
    
class NKTContrast():
    """
    This class performs various functions in the NKT Photon instrument.
    ------
    Before performing any functions, please start connection with pe_open.
    ------
    After you're done, please close communications using pe_close.
    
    """
    def __init__(self):
        s
        
    def pe_open(self):
        """
        Opens communication channel with system
        
        """
        #Acquire handle on LLTF Contrast
        peCreate = library.PE_Create
        peCreate.argtypes = [c_char_p, c_PE_HANDLE_p]
        
        #Open communication channel
        peOpen = library.PE_Open
    
    def status(self):
        """
        Gets status of the instrument (PE_STATUS)
        
        """
        pegetstatusstr = library.PEGetStatusStr
        pegetstatusstr.argtypes = []
        pegetstatusstr.restype = c_char_p
        
    def get_wavelength(self):
        """
        Returns the central wavelength filtered by the system in nanometers.

        """
        pegetwavelength = library.PE_GetWavelength
        pegetwavelength.restype = c_double_p
    
    def wavecal(self, wave1, wave2):
        """
        Calibrates the instrument (Not sure which pe function i use here)
        
        """
        
    def pe_close(self):
        """
        Closes communication channel with system

        """
        #Close communication channel
        peClose = library.PE_Close
        
        #Destroys filter resource created with PE_Create
        peDestroy = library.PE_Destroy
        
if __name__ == '__main__':
    #from flask import Flask
    #Argparse here. Takes some arguments.
    #PE_CREATE. Creates a new environment
    #Open file
    #...
    #Close file
    #PE_DESTROY. Destroys the environment