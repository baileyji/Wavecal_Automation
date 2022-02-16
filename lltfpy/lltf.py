"""
This is the hardware class for access to the high contrast LLTF filter.
"""

from logging import getLogger
from ctypes import *
from sys import platform
from enum import IntEnum

class LLTFError(Exception):
    pass

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

class LLTF:
    """

    Hardware class for connection to the LLTF High Contrast filter.

    """

    def __init__(self, conffile):
        #Check platform
        if platform.startswith('win64'):
            lib_path = './win64/PE_Filter_SDK.dll'
        elif platform.startswith('win32'):
            lib_path = './win32/PE_Filter_SDK.dll'
        else:
            raise LLTFError('Could not find library.')
            
        self._conffile = conffile
        self._library = CDLL(lib_path)
        self._handle = None

    def _open(self, index=0):
        """

        Creates and opens connection with the system. 
        Called by status and get_wave.

        Parameters
            index (integer) - Position of the system. Default is zero.
        Returns
            self._handle (PE_HANDLE)- Connection handle
            name (bytes) - System name
            
        """
        library = self._library

        #Acquire handle on LLTF Contrast
        pe_Create = library.PE_Create
        pe_Create.argtypes = [c_char_p, POINTER(PE_HANDLE)]
        pe_Create.restype = PE_STATUS

        #Retrieves system name
        pe_GetSystemName = library.PE_GetSystemName
        pe_GetSystemName.argtypes = [CPE_HANDLE, c_int, POINTER(c_char), c_int]
        pe_GetSystemName.restype = PE_STATUS
        
        #Open communication channel
        pe_Open = library.PE_Open
        pe_Open.argtypes = [PE_HANDLE, c_char_p]
        pe_Open.restype = PE_STATUS
        
        if self._handle is None:
            #Create system connection
            conffile = self._conffile
            conffile = conffile.encode('ASCII')
            peHandle_i = PE_HANDLE()
            create_status = pe_Create(conffile, byref(peHandle_i))
            if create_status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not create connection to LLTF.')
            peHandle = peHandle_i.value
            #Retrieve system name
            name_i = c_char()
            name_status = pe_GetSystemName(peHandle, index, 
                                           byref(name_i), sizeof(name_i))
            if name_status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not retrieve LLTF name.')
            name = name_i.value
            #Open connection to system
            open_status = pe_Open(peHandle, name)
            if open_status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not open connection to LLTF.')
            self._handle = peHandle
            return self._handle, name
        else:
            getLogger().debug('Already open.')
            pass
        
    def _close(self):
        """

        Closes connection with system. '
        Called by status and get_wave.

        Parameters
            peHandle (PE_HANDLE) - Handle to system. 

        """
        library = self._library

        #Close communication channel
        pe_Close = library.PE_Close
        pe_Close.argtypes = [PE_HANDLE]
        pe_Close.restype = PE_STATUS

        #Destroys filter resource created with PE_Create
        pe_Destroy = library.PE_Destroy
        pe_Destroy.argtypes = [PE_HANDLE]
        pe_Destroy.restype = PE_STATUS

        if self._handle is not None:
            peHandle = self._handle
            #Close connection
            closestatus = pe_Close(peHandle)
            if closestatus != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not close system.')
            #Destroy connection
            destroystatus = pe_Destroy(peHandle)
            if destroystatus != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not destroy system.')
            self._handle = None
        else:
            getLogger().debug('Already closed.')
            pass
        
    def status(self):
        """
        
        Returns status of filter as a dictionary. 
        Called directly by client.
        
        Parameters
            conffile (string) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
                
        Returns
            status - Dictionary containing status of the filter.
                Includes:
                      Library version (integer)
                      System name (bytes)
                      Number of possible systems (integer)
                      Central wavelength (float)
                      Wavelength range (float)
                      Grating index (integer)
                      Grating name (bytes)
                      Grating count (integer)
                      Availability of harmonic filter (integer) - 0 if unavailable
                      Status of harmonic filter (integer) - 0 if unavailable
                      
        """
        close = False
        try:
            self._handle, name = self._open()
            library_vers = self.library_version()
            count = self.system_count()
            wave = self.get_wave()
            minimum, maximum = self.get_range()
            gindex, gname, gcount = self.grating()
            havail, henable = self.harmonic_filter()
            status = {'system_name': name,
                      'library_version': library_vers,
                      'system_count': count,
                      'central_wavelength': wave, 
                      'range_minimum': minimum,
                      'range_maximum': maximum,
                      'grating_index': gindex,
                      'grating_name': gname,
                      'grating_count': gcount,
                      'harmonic_filter_availability': havail,
                      'harmonic_filter_status': henable
                      }
            return True, status
        except:
            close = True
        finally:
            if close:
                self._close()
        return False
    
    def set_wave(self, wavelength):
        """

        Sets central wavelength of the filter. 
        Called directly by client.
        Returns newly calibrated wavelength.

        Parameters
            conffile (string) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            wavelength (float) - Desired central wavelength in nm
            
        """
        library = self._library

        #Sets central wavelength filtered by system in nanometers
        pe_SetWavelength = library.PE_SetWavelength
        pe_SetWavelength.argtypes = [PE_HANDLE, c_double]
        pe_SetWavelength.restype = PE_STATUS

        close = False
        try:
            self._handle, name = self._open()
            peHandle = self._handle
            #Set wavelength
            status = pe_SetWavelength(peHandle, wavelength)
            if status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not set wavelength.')
            #Retrieve new wavelength
            new_wave = self.get_wave()
            if new_wave != wavelength:
                raise LLTFError('Calibration could not occur.')
            else:
                return True
        except:
            close = True
        finally:
            if close:
                self._close()
        return False
    
    def library_version(self):
        """
    
        Return version number of library. 
        Called by status.
        
        Returns
            library_vers (integer) - Library version number
            
        """
        library = self._library
            
        #Retrieves version number of library
        pe_LibraryVersion = library.PE_GetLibraryVersion
        pe_LibraryVersion.restype = c_int
    
        library_vers = pe_LibraryVersion()
        return library_vers

    def system_count(self):
        """
        
        Retrieves the number of systems, connected or not. 
        Called by status.
        
        Parameters
            peHandle - Handle to system
        Returns
            count (integer) - Number of systems listed in config file
            
        """
        library = self._library
        peHandle = self._handle
        
        #Retrieves number of systems available in config file
        pe_GetSystemCount = library.PE_GetSystemCount
        pe_GetSystemCount.argtypes = [CPE_HANDLE]
        pe_GetSystemCount.restype = c_int
        
        count = pe_GetSystemCount(peHandle)
        return count
    
    def get_wave(self):
        """
    
        Retrieves central wavelength filtered by system in nm. 
        Called by _status and set_wave.

        Parameters
            peHandle - Handle to system 
        Returns
            wavelength (float) - Central wavelength filtered by system (nm)
            
        """
        library = self._library
        peHandle = self._handle

        #Returns the central wavelength filtered by the system in nanometers
        pe_GetWavelength = library.PE_GetWavelength
        pe_GetWavelength.argtypes = [CPE_HANDLE, POINTER(c_double)]
        pe_GetWavelength.restype = PE_STATUS
        
        wavelength_i = c_double()
        status = pe_GetWavelength(peHandle, byref(wavelength_i))
        wavelength = wavelength_i.value
        if status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not retrieve wavelength.')
        return wavelength
    
    def get_range(self):
        """
        
        Retrieves wavelength range filtered by system in nm. 
        Called by _status and set_wave.
        
        Parameters
            peHandle - Handle to system
        Returns
            minimum (float) - Range minimum
            maximum (float) - Range maximum
            
        """
        library = self._library
        peHandle = self._handle
        
        #Retrieves wavelength range of system in nanometers
        pe_GetWavelengthRange = library.PE_GetWavelengthRange
        pe_GetWavelengthRange.argtypes = [CPE_HANDLE, 
                                          POINTER(c_double), POINTER(c_double)]
        pe_GetWavelengthRange.restype = PE_STATUS
        
        minimum_i = c_double()
        maximum_i = c_double()
        status = pe_GetWavelengthRange(peHandle, 
                                       byref(minimum_i), byref(maximum_i))
        minimum = minimum_i.value
        maximum = maximum_i.value
        if status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not retrieve wavelength range.')
        return minimum, maximum
    
    def grating(self):
        """

        Retrieves LLTF grating info. 
        Called by status.
        
        Parameters
            peHandle - Connection handle
        Returns
            gindex (integer)- Grating index
            gname (bytes) - Grating name
            gcount (integer) - Grating number

        """
        library = self._library
        peHandle = self._handle

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
        
        #Retrieve grating
        gratingIndex = c_int()
        getgratingstatus = pe_GetGrating(peHandle, byref(gratingIndex))
        gindex = gratingIndex.value
        #Retrieve grating name
        name = c_char()
        gratingnamestatus = pe_GetGratingName(peHandle, gindex, 
                                              byref(name), sizeof(name))
        gname = name.value
        #Retrieve grating count
        count = c_int()
        gratingcountstatus = pe_GetGratingCount(peHandle, byref(count))
        gcount = count.value
        #Check for errors
        if getgratingstatus or gratingnamestatus or gratingcountstatus != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not retrieve grating.')
        return gindex, gname, gcount

        
    def harmonic_filter(self):
        """
        
        Checks availability and status of harmonic filter. 
        Called by status.

        Parameters
            peHandle - Connection handle
        Returns
            avail (integer) - Availability of harmonic filter. 0 if unavailable.
            enable (integer) - Status of harmonic filter. 0 if disabled.
            
        """
        library = self._library
        peHandle = self._handle
        
        #Retrieves availability of harmonic filter accessory.
        pe_HasHarmonicFilter = library.PE_HasHarmonicFilter
        pe_HasHarmonicFilter.argtypes = [CPE_HANDLE]
        pe_HasHarmonicFilter.restype = c_int
        
        #Retrieves status of harmonic filter accessory.
        pe_GetHarmonicFilterEnabled = library.pe_GetHarmonicFilterEnabled
        pe_GetHarmonicFilterEnabled.argtypes = [CPE_HANDLE, POINTER(c_int)]
        pe_HasHarmonicFilter.restype = PE_STATUS
        
        avail = pe_HasHarmonicFilter(peHandle)
        enable_i = c_int()
        status = pe_GetHarmonicFilterEnabled(peHandle, byref(enable_i))
        enable = enable_i.value
        if status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not find harmonic filter status.')
        return avail, enable
    
# =============================================================================
#     def grating_wave(self, gratingIndex):
#         """
#        
#         Returns wavelength range and extended wavelength range on the grating.
#         Currently not called by any functions.
#         
#         Inputs:
#             peHandle - Handle retrieved from NKT_Open
#             gratingIndex (integer) - Position of the grating. Retrieved from NKT_GratingStatus
#         Returns:
#             minimum (float) - Minimum available wavelength (in nm)
#             maximum (float) - Maximum available wavelength
#             extended_min (float) - Minimum extended wavelength (in nm)
#             extended_max (float) - Maximum extended wavelength
#      
#         """
#         library = self._library
#         peHandle = self._handle
#         
#         #Retrieve wavelength range of grating in nanometers
#         pe_GetGratingWavelengthRange = library.PE_GetGratingWavelengthRange
#         pe_GetGratingWavelengthRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
#         pe_GetGratingWavelengthRange.restype = PE_STATUS
# 
#         #Retrieve extended wavelength range of grating in nanometers
#         pe_GetGratingWavelengthExtendedRange = library.PE_GetGratingWavelengthExtendedRange
#         pe_GetGratingWavelengthExtendedRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
#         pe_GetGratingWavelengthExtendedRange.restype = PE_STATUS
#         
#         minimum = c_double()
#         maximum = c_double()
#         rangestatus = pe_GetGratingWavelengthRange(peHandle, gratingindex, 
#                                                    byref(minimum), byref(maximum))
#         if rangestatus != PE_STATUS.PE_SUCCESS:
#             raise LLTFError('Could not return grating wavelength range.')
#         extended_min = c_double()
#         extended_max = c_double()
#         extendedstatus = pe_GetGratingWavelengthExtendedRange(peHandle, gratingindex, 
#                                                               byref(extended_min), byref(extended_max))
#         if extendedstatus != PE_STATUS.PE_SUCCESS:
#             raise LLTFError('Could not return grating wavelength extended range.')
#         minimum_n = minimum.value
#         maximum_n = maximum.value
#         extended_min_n = extended_min.value
#         extended_max_n = extended_max.value
#         return minimum_n, maximum_n, extended_min_n, extended_max_n
# =============================================================================
