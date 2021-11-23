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
    
    @classmethod
    def from_param(cls, obj):
        if not is_instance(obj, PE_STATUS):
            raise TypeError('Not a PE_STATUS instance.')
        return int(obj)

class PE_HANDLE:
    """
    A c void pointer. PE_HANDLE structure where handle is stored
    
    """
    def __init__(self, c_void_p):
        self._as_parameter_ = c_void_p
        
class CPE_HANDLE:
    """
    A c void constant pointer. Constant handle to system.
    
    """
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
        pass
        
    def NKT_Open(self, conffile, index=0):
        """
        Creates and opens communication channel with system
        
        Inputs:
            conffile (Required) - Path to configuration file. 
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            index (Optional) - Position of the system. Default is zero.
            
        """
        #Acquire handle on LLTF Contrast
        pe_Create = library.PE_Create
        pe_Create.argtypes = [c_char_p, POINTER(PE_HANDLE)]
        pe_Create.restype = PE_STATUS
        
        #Retrieves number of systems available in config file
        pe_GetSystemCount = library.PE_GetSystemCount
        pe_GetSystemCount.argtypes = [CPE_HANDLE]
        pe_GetSystemCount.restype = c_int
        
        #Retrieves system name
        pe_GetSystemName = library.PE_GetSystemName
        pe_GetSystemName.argtypes = [CPE_HANDLE, c_int, POINTER(c_char), c_int]
        pe_GetSystemName.restype = PE_STATUS
        
        #Retrieves version number of library
        pe_LibraryVersion = library.PE_GetLibraryVersion
        pe_LibraryVersion.restype = c_int
                
        #Open communication channel
        pe_Open = library.PE_Open
        pe_Open.argtypes = [PE_HANDLE, c_char_p]
        pe_Open.restype = PE_STATUS
        
        try:
            conffile = conffile.encode('ASCII')
            peHandle = PE_HANDLE()
            create_status = pe_Create(conffile, byref(peHandle))
            print('Status of handle creation:', create_status)
            peHandle = peHandle.value
            num_sys = pe_GetSystemCount(peHandle)
            name = c_char()
            #How to get system size??? Need to look into
            name_status = pe_GetSystemName(peHandle, index, byref(name), sizeof(name))
            print('Status of system name retrieval:', name_status)
            library_vers = pe_LibraryVersion()
            open_status = pe_Open(peHandle, name.value)
            print('Status of system opening:', open_status, '\n')
            print('Communcation channel opened.', '\n', 
                  'Library Version:', library_vers, '\n', 
                  'Number of systems:', num_sys, '\n',
                  'Handle to the system:', peHandle, '\n', 
                  'System name:', name.value)
        except:
            print('Could not connect to system.')
    
    def NKT_StatusStr(self, pestatuscode):
        """
        Retrieves explanation for a given status code. 
        
        Inputs:
            pestatuscode (Required) - A status code like PE_SUCCESS or PE_INVALID_HANDLE
            Should be in form PE_STATUS.PE_ERRORCODE
            
        """
        pe_GetStatusStr = library.PE_GetStatusStr
        pe_GetStatusStr.argtypes = [PE_STATUS]
        pe_GetStatusStr.restype = c_char_p
        
        try:
            statusstring = pe_GetStatusStr(pestatuscode)
            print(pestatuscode, ':', statusstring)
        except:
            print('Not able to retrieve status code string.')
        
    def NKT_Wavelength(self, peHandle):
        """
        Returns the central wavelength and the wavelength range.
        
        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
            
        """
        #Returns the central wavelength filtered by the system in nanometers
        pe_GetWavelength = library.PE_GetWavelength
        pe_GetWavelength.argtypes = [CPE_HANDLE, POINTER(c_double)]
        pe_GetWavelength.restype = PE_STATUS
        
        #Retrieves wavelength range of system in nanometers
        pe_GetWavelengthRange = library.pe_GetWavelengthRange
        pe_GetWavelengthRange.argtypes = [CPE_HANDLE, POINTER(c_double), POINTER(c_double)]
        pe_GetWavelengthRange.restype = PE_STATUS
        
        try:
            wavelength = c_double()
            getwavestatus = pe_GetWavelength(peHandle, byref(wavelength))
            print('Status of wavelength retrieval:', getwavestatus)
            if getwavestatus == PE_STATUS.PE_SUCCESS:
                print('Wavelength:', wavelength.value, 'nm')
            else:
                print('Unable to retrieve wavelength.')
            minimum = c_double()
            maximum = c_double()
            getrangestatus = pe_GetWavelengthRange(peHandle, byref(minimum), byref(maximum))
            print('Status of wavelength range retrieval:', getrangestatus)
            if getrangestatus == PE_STATUS.PE_SUCCESS:
                print('Wavelength range:', minimum.value, 'to', maximum.value, 'nm')
            else:
                print('Unable to retrieve wavelength range.')
        except:
            print('Could not retrieve wavelength.')
            
    def NKT_Calibrate(self, peHandle, wavelength):
        """
        Calibrates the instrument.
        
        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
            wavelength (required) - Desired central wavelength to be filtered by system (nm)
        
        """
        #Sets central wavelength filtered by system in nanometers
        pe_SetWavelength = library.PE_SetWavelength
        pe_SetWavelength.argtypes = [PE_HANDLE, c_double]
        pe_SetWavelength.restype = PE_STATUS
        
        pe_GetWavelength = library.PE_GetWavelength
        pe_GetWavelength.argtypes = [CPE_HANDLE, POINTER(c_double)]
        pe_GetWavelength.restype = PE_STATUS
        
        try:
            setwavestatus = pe_SetWavelength(peHandle, wavelength)
            print('Status of calibration:', setwavestatus)
            if setwavestatus == PE_STATUS.PE_SUCCESS:
                print('Central wavelength set.')
                newwavelength = c_double()
                pe_GetWavelength(peHandle, byref(newwavelength))
                print('New central wavelength:', newwavelength.value)
            else:
                print('Unable to calibrate.')
        except:
            print('Could not calibrate wavelength.')
            
    def NKT_GratingStatus(self, peHandle):
        """
        Retrieves information about the grating specified by the index, 
        including the wavelength range.
        
        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
            
        """
        #Retrieves grating
        pe_GetGrating = library.PE_GetGrating
        pe_GetGrating.argtypes = [PE_HANDLE, POINTER(c_int)]
        pe_GetGrating.restype = PE_STATUS
        
        #Retrieves grating name
        pe_GetGratingName = library.PE_GetGratingName
        pe_GetGratingName.argtypes = [CPE_HANDLE, c_int, POINTER(c_char), c_int]
        pe_GetGratingName.restype = PE_STATUS
        
        #Retrieves system's grating count number
        pe_GetGratingCount = library.PE_getGratingCount
        pe_GetGratingCount.argtypes = [CPE_HANDLE, POINTER(c_int)]
        pe_GetGratingCount.restype = PE_STATUS
        
        #Retrieve wavelength range of grating in nanometers
        pe_GetGratingWavelengthRange = library.PE_GetGratingWavelengthRange
        pe_GetGratingWavelengthRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthRange.restype = PE_STATUS
        
        #Retrieve extended wavelength range of grating in nanometers
        pe_GetGratingWavelengthExtendedRange = library.PE_GetGratingWavelengthExtendedRange
        pe_GetGratingWavelengthExtendedRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthExtendedRange.restype = PE_STATUS
        
        try:
            gratingIndex = c_int()
            getgratingstatus = pe_GetGrating(peHandle, byref(gratingIndex))
            gindex = gratingIndex.value
            print('Status of grating retrieval:', getgratingstatus, '\n', 
                  'Grating index:', gindex)
            name = c_char()
            #size = ??
            gratingnamestatus = pe_GetGratingName(peHandle, gindex, byref(name), size)
            print('Status of grating name retrieval:', gratingnamestatus)
            count = c_int()
            gratingcountstatus = pe_GetGratingCount(peHandle, byref(count))
            print('Status of grating count retrieval:', gratingcountstatus)
            minimum = c_double()
            maximum = c_double()
            gratingrangestatus = pe_GetGratingWavelengthRange(peHandle, gindex, byref(minimum), byref(maximum))
            print('Status of grating wavelength range retrieval:', gratingrangestatus)
            extended_min = c_double()
            extended_max = c_double()
            extendedstatus = pe_GetGratingWavelengthExtendedRange(peHandle, gindex, byref(extended_min), byref(extended_max))
            print('Status of grating extended wavelength range retrieval:', extendedstatus)
            print('Grating name:', name.value, '\n', 
                  'Grating count number:', count.value, '\n', 
                  'Grating wavelength range:', minimum, 'nm to', maximum, 'nm', '\n',
                  'Grating extended wavelength range:', extended_min, 'nm to', extended_max, 'nm')
        except:
            print('Could not retrieve grating status.')
            
    def NKT_CalibrateGrating(self, peHandle, gratingIndex, wavelength):
        """
        Calibrates the central wavelength of the grating.

        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
            gratingIndex (required) - Position of the grating. Retrieved from NKT_GratingStatus
            wavelength (required) - Desired central wavelength in nm
       
        """
        #Sets central wavelength filtered by system in nanometers
        pe_SetWavelengthOnGrating = library.PE_SetWavelengthOnGrating 
        pe_SetWavelengthOnGrating.argtypes = [PE_HANDLE, c_int, c_double]
        pe_SetWavelengthOnGrating.restype = PE_STATUS
        
        pe_GetGratingWavelengthRange = library.PE_GetGratingWavelengthRange
        pe_GetGratingWavelengthRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthRange.restype = PE_STATUS
        
        try:
            gratingcalibstatus = pe_SetWavelengthOnGrating(peHandle, gratingIndex, wavelength)
            print('Status of grating calibration:', gratingcalibstatus)
            if gratingcalibstatus == PE_STATUS.PE_SUCCESS:
                print('Grating calibration set.')
                minimum = c_double()
                maximum = c_double()
                pe_GetGratingWavelengthRange(peHandle, gindex, byref(minimum), byref(maximum))
                print('New grating wavelength range:', minimum, 'nm to', maximum, 'nm')
            else:
                print('Unable to calibrate grating.')
        except:
            print('Could not calibrate grating.')
            
    def NKT_Close(self):
        """
        Closes communication channel with system
        
        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
            
        """
        #Close communication channel
        pe_Close = library.PE_Close
        pe_Close.argtypes = [PE_HANDLE]
        pe_Close.restype = PE_STATUS
        
        #Destroys filter resource created with PE_Create
        pe_Destroy = library.PE_Destroy
        pe_Destroy.argtypes = [PE_HANDLE]
        pe_Destroy.restype = PE_STATUS
        
        try:
            closestatus = pe_Close(peHandle)
            print('Status of closing system:', closestatus)
            destroystatus = pe_Destroy(peHandle)
            print('Status of destroying system:', destroystatus)
            if closestatus == PE_STATUS.PE_SUCCESS and destroystatus == PE_STATUS.PE_SUCCESS:
                print('System successfully closed and destroyed!')
                
if __name__ == '__main__':
    #from flask import Flask
    #Argparse here. Takes some arguments.
    
    #...
    #Close file
    #PE_DESTROY. Destroys the environment
