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
    
    """
    def status():
        """
        Returns
        -------
        Status of the instrument (PE_STATUS)
        """
        
    def wavecal(wave1, wave2):
        """
        

        Parameters
        ----------
        Param 1:
            
        Param 2:

        Returns
        -------
        Calibrates the 

        """
        
if __name__ == '__main__':
    #from flask import Flask
    #Argparse here. Takes some arguments.
    #PE_CREATE. Creates a new environment
    #Open file
    #...Do stuff here
    #Close file
    #PE_DESTROY. Destroys the environment