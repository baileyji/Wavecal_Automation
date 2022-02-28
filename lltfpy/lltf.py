"""
This is the hardware class for access to the high contrast LLTF filter.
"""

from logging import getLogger
from ctypes import *
from sys import platform
from enum import IntEnum

class LLTFError(IOError):
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
        if not isinstance(obj, PE_STATUS):
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
            raise IOError('Platform not supported.')
            
        self.conffile = conffile
        self._library = CDLL(lib_path)
        self._handle = None
        self.name = ''
        

    def _open(self, index=0):
        """
        Creates and opens connection with the system.
        If handle is already available, it tests the handle before use.

        Parameters
            index (integer) - Position of the system. Default is zero.
        Returns
            self._handle (PE_HANDLE)- Connection handle
            name (bytes) - System name
            
        """
        pe_Create = self._library.PE_Create
        pe_Create.argtypes = [c_char_p, POINTER(PE_HANDLE)]
        pe_Create.restype = PE_STATUS

        pe_GetSystemName = self._library.PE_GetSystemName
        pe_GetSystemName.argtypes = [CPE_HANDLE, c_int, POINTER(c_char), c_int]
        pe_GetSystemName.restype = PE_STATUS
        
        pe_Open = self._library.PE_Open
        pe_Open.argtypes = [PE_HANDLE, c_char_p]
        pe_Open.restype = PE_STATUS
        
        if self._handle is not None:
            self._close()
        #Create system connection
        conffile = self.conffile.encode('ASCII')
        peHandle_i = PE_HANDLE()
        create_status = pe_Create(conffile, byref(peHandle_i))
        if create_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not create connection to LLTF:', str(create_status))
        self._handle = peHandle_i.value
        #Retrieve system name
        name_i = c_char()
        name_status = pe_GetSystemName(self._handle, index, 
                                       byref(name_i), sizeof(name_i))
        if name_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not retrieve LLTF name:', str(name_status))
        self.name = str(name_i.value)
        #Open connection to system
        open_status = pe_Open(self._handle, self.name)
        if open_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not open connection to LLTF:', str(open_status))
            
    def _close(self):
        """
        Closes connection with system.

        Parameters
            peHandle (PE_HANDLE) - Handle to system. 

        """
        pe_Close = self._library.PE_Close
        pe_Close.argtypes = [PE_HANDLE]
        pe_Close.restype = PE_STATUS

        pe_Destroy = self._library.PE_Destroy
        pe_Destroy.argtypes = [PE_HANDLE]
        pe_Destroy.restype = PE_STATUS

        if self._handle is not None:
            #Close connection
            closestatus = pe_Close(self._handle)
            if closestatus == PE_STATUS.PE_INVALID_HANDLE:
                self._handle = None
                raise ValueError('Invalid handle:', str(closestatus))
            elif closestatus != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not close system:', str(closestatus))
            #Destroy connection
            destroystatus = pe_Destroy(self._handle)
            if destroystatus != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not destroy system:', str(destroystatus))
            self._handle = None
        else:
            getLogger(__name__).debug('Already closed.')
        
        
    def status(self):
        """
        Returns status of filter as a dictionary. 
        
        Parameters
            conffile (string) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
                
        Returns
            status - Dictionary containing status of the filter.
                Includes:
                      Library version (integer)
                      System name (string)
                      Number of possible systems (integer)
                      Central wavelength (float)
                      Wavelength range (float)
                      Grating index (integer), name (string), 
                          count (integer), range (float), extended range (float)
                      Availability and status of harmonic filter (string)
                      
        """
        try:
            self._open()
            library_vers = self._library_version()
            count = self._system_count()
            wave = self._get_wave()
            minimum, maximum = self._get_range()
            gindex, gname, gcount = self._grating()
            gmin, gmax, gextmin, gestmax = self._grating_wave(gindex)
            havail, henable = self._harmonic_filter()
            return {'system_name': self.name,
                      'library_version': library_vers,
                      'system_count': count,
                      'central_wavelength': wave, 
                      'range': (minimum, maximum),
                      'grating': {'index':gindex, 'name':gname, 'count':gcount, 
                                  'range': (gmin, gmax), 'extended_range': (gextmin, gextmax)},
                      'harmonic_filter': 'Unavailable' if havail==0 else 
                      ('Available', 'Disabled' if henable==0 else 'Enabled')}
        except Exception as e:
            raise e
        finally:
            self._close()
       
        
    def set_wave(self, wavelength):
        """

        Sets central wavelength of the filter. 

        Parameters
            conffile (string) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            wavelength (float) - Desired central wavelength in nm
            
        """
        pe_SetWavelength = self._library.PE_SetWavelength
        pe_SetWavelength.argtypes = [PE_HANDLE, c_double]
        pe_SetWavelength.restype = PE_STATUS

        try:
            self._open()
            check_wave = self._get_wave()
            if check_wave == wavelength:
                getLogger(__name__).debug('Wavelength already set:', check_wave, 'nm')
            else:
                #Set wavelength
                status = pe_SetWavelength(self._handle, wavelength)
                if status == PE_STATUS.PE_INVALID_WAVELENGTH:
                    raise ValueError('Invalid input wavelength:', str(status))
                elif status != PE_STATUS.PE_SUCCESS:
                    raise LLTFError('Could not set wavelength:', str(status))
                #Retrieve new wavelength
                new_wave = self._get_wave()
                if new_wave != wavelength:
                    raise ValueError("Retrieved wavelength doesn't reflect set wavelength.")
        except Exception as e:
            raise e
        finally:
            self._close()
    
    
    def _library_version(self):
        """
        Return version number of library. 
        
        Returns
            library_vers (integer) - Library version number
            
        """
        pe_LibraryVersion = self._library.PE_GetLibraryVersion
        pe_LibraryVersion.restype = c_int
    
        library_vers = pe_LibraryVersion()
        return library_vers


    def _system_count(self):
        """
        Retrieves the number of systems, connected or not. 
        
        Returns
            count (integer) - Number of systems listed in config file
            
        """
        pe_GetSystemCount = self._library.PE_GetSystemCount
        pe_GetSystemCount.argtypes = [CPE_HANDLE]
        pe_GetSystemCount.restype = c_int
        
        count = pe_GetSystemCount(self._handle)
        return count
    
    
    def _get_wave(self):
        """
        Retrieves central wavelength filtered by system in nm. 

        Returns
            wavelength (float) - Central wavelength filtered by system (nm)
            
        """
        pe_GetWavelength = self._library.PE_GetWavelength
        pe_GetWavelength.argtypes = [CPE_HANDLE, POINTER(c_double)]
        pe_GetWavelength.restype = PE_STATUS
        
        wavelength_i = c_double()
        status = pe_GetWavelength(self._handle, byref(wavelength_i))
        wavelength = wavelength_i.value
        if status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not retrieve wavelength:', str(status))
        return wavelength
    
    
    def _get_range(self):
        """
        Retrieves wavelength range filtered by system in nm. 
        
        Returns
            minimum (float) - Range minimum
            maximum (float) - Range maximum
            
        """
        pe_GetWavelengthRange = self._library.PE_GetWavelengthRange
        pe_GetWavelengthRange.argtypes = [CPE_HANDLE, 
                                          POINTER(c_double), POINTER(c_double)]
        pe_GetWavelengthRange.restype = PE_STATUS
        
        minimum_i = c_double()
        maximum_i = c_double()
        status = pe_GetWavelengthRange(self._handle, 
                                       byref(minimum_i), byref(maximum_i))
        minimum = minimum_i.value
        maximum = maximum_i.value
        if status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not retrieve wavelength range:', str(status))
        return minimum, maximum
    
    
    def _grating(self):
        """
        Retrieves LLTF grating info. 
        
        Returns
            gindex (integer)- Grating index
            gname (string) - Grating name
            gcount (integer) - Grating number

        """
        pe_GetGrating = self._library.PE_GetGrating
        pe_GetGrating.argtypes = [PE_HANDLE, POINTER(c_int)]
        pe_GetGrating.restype = PE_STATUS

        pe_GetGratingName = self._library.PE_GetGratingName
        pe_GetGratingName.argtypes = [CPE_HANDLE, c_int, POINTER(c_char), c_int]
        pe_GetGratingName.restype = PE_STATUS

        pe_GetGratingCount = self._library.PE_getGratingCount
        pe_GetGratingCount.argtypes = [CPE_HANDLE, POINTER(c_int)]
        pe_GetGratingCount.restype = PE_STATUS
        
        #Retrieve grating
        gratingIndex = c_int()
        getgratingstatus = pe_GetGrating(self._handle, byref(gratingIndex))
        if getgratingstatus != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not retrieve grating:', str(getgratingstatus))
        gindex = gratingIndex.value
        #Retrieve grating name
        name = c_char()
        gratingnamestatus = pe_GetGratingName(self._handle, gindex, 
                                              byref(name), sizeof(name))
        if gratingnamestatus != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not retrieve grating name:', str(gratingnamestatus))
        gname = str(name.value)
        #Retrieve grating count
        count = c_int()
        gratingcountstatus = pe_GetGratingCount(self._handle, byref(count))
        if gratingcountstatus != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not retrieve grating count:', str(gratingcountstatus))
        gcount = count.value    
        return gindex, gname, gcount

         
    def _grating_wave(self, gratingIndex):
        """
        Returns wavelength range and extended wavelength range on the grating.
        
        Inputs:
            gratingIndex (integer) - Position of the grating. Retrieved from NKT_GratingStatus
        Returns:
            minimum (float) - Minimum available wavelength (in nm)
            maximum (float) - Maximum available wavelength
            extended_min (float) - Minimum extended wavelength (in nm)
            extended_max (float) - Maximum extended wavelength
     
        """
        pe_GetGratingWavelengthRange = self._library.PE_GetGratingWavelengthRange
        pe_GetGratingWavelengthRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthRange.restype = PE_STATUS

        pe_GetGratingWavelengthExtendedRange = self._library.PE_GetGratingWavelengthExtendedRange
        pe_GetGratingWavelengthExtendedRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthExtendedRange.restype = PE_STATUS
        
        if gratingIndex == None:
            raise ValueError('Grating index not found.')
        minimum_i = c_double()
        maximum_i = c_double()
        rangestatus = pe_GetGratingWavelengthRange(self._handle, gratingindex, 
                                                   byref(minimum_i), byref(maximum_i))
        if rangestatus != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not return grating wavelength range:', str(rangestatus))
        extended_min_i = c_double()
        extended_max_i = c_double()
        extendedstatus = pe_GetGratingWavelengthExtendedRange(self._handle, gratingindex, 
                                                              byref(extended_min_i), byref(extended_max_i))
        if extendedstatus != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not return grating wavelength extended range:', str(extendedstatus))
        minimum = minimum_i.value
        maximum = maximum_i.value
        extended_min = extended_min_i.value
        extended_max = extended_max_i.value
        return minimum, maximum, extended_min, extended_max
    
    
    def _harmonic_filter(self):
        """
        Checks availability and status of harmonic filter. 

        Returns
            avail (integer) - Availability of harmonic filter. 0 if unavailable.
            enable (integer) - Status of harmonic filter. 0 if disabled.
            
        """
        pe_HasHarmonicFilter = self._library.PE_HasHarmonicFilter
        pe_HasHarmonicFilter.argtypes = [CPE_HANDLE]
        pe_HasHarmonicFilter.restype = c_int
        
        pe_GetHarmonicFilterEnabled = self._library.pe_GetHarmonicFilterEnabled
        pe_GetHarmonicFilterEnabled.argtypes = [CPE_HANDLE, POINTER(c_int)]
        pe_HasHarmonicFilter.restype = PE_STATUS
        
        avail = pe_HasHarmonicFilter(self._handle)
        enable_i = c_int()
        status = pe_GetHarmonicFilterEnabled(self._handle, byref(enable_i))
        enable = enable_i.value
        if status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not find harmonic filter status:', str(status))
        return avail, enable
    