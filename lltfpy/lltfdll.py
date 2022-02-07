"""
The classes PE_STATUS, PE_HANDLE, and CPE_HANDLE are for converting c objects into
    in the LLTF .dll file.
NKTContrast converts c functions into python.

"""
from ctypes import *
from sys import platform
from enum import IntEnum

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

    """
    def __init__(self):
        if platform.startswith('win64'):
            lib_path = './win64/PE_Filter_SDK.dll'
        elif platform.startswith('win32'):
            lib_path = './win32/PE_Filter_SDK.dll'
        else:
            raise Exception
        self.library = CDLL(lib_path)

    def NKT_Open(self, conffile, index=0):
        """
        Creates and opens communication channel with system.
        Returns:
            peHandle - 

        """
        library = self.library

        #Acquire handle on LLTF Contrast
        pe_Create = library.PE_Create
        pe_Create.argtypes = [c_char_p, POINTER(PE_HANDLE)]
        pe_Create.restype = PE_STATUS

        #Retrieves system name
        pe_GetSystemName = library.PE_GetSystemName
        pe_GetSystemName.argtypes = [CPE_HANDLE, c_int, POINTER(c_char), c_int]
        pe_GetSystemName.restype = PE_STATUS(x, base)
        
        #Open communication channel
        pe_Open = library.PE_Open
        pe_Open.argtypes = [PE_HANDLE, c_char_p]
        pe_Open.restype = PE_STATUS
        
        conffile = conffile.encode('ASCII')
        peHandle = PE_HANDLE()
        create_status = pe_Create(conffile, byref(peHandle))
        peHandle = peHandle.value
        name = c_char()
        #How to get system size??? Need to look into
        name_status = pe_GetSystemName(peHandle, index, byref(name), sizeof(name))
        name = name.value
        open_status = pe_Open(peHandle, name.value)
        return peHandle, name, create_status, open_status

    def NKT_Close(self, peHandle):
        """
        Closes communication channel with system.
        Returns status of system closing and destruction.

        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open

        """
        library = self.library

        #Close communication channel
        pe_Close = library.PE_Close
        pe_Close.argtypes = [PE_HANDLE]
        pe_Close.restype = PE_STATUS

        #Destroys filter resource created with PE_Create
        pe_Destroy = library.PE_Destroy
        pe_Destroy.argtypes = [PE_HANDLE]
        pe_Destroy.restype = PE_STATUS

        closestatus = pe_Close(peHandle)
        destroystatus = pe_Destroy(peHandle)
        return closestatus, destroystatus
    
    def NKT_StatusStr(self, pestatuscode):
        """
        Retrieves explanation for a given status code.
        Returns a string explaining the given status code.

        Inputs:
            pestatuscode (Required) - A status code like PE_SUCCESS or PE_INVALID_HANDLE
            Should be in form PE_STATUS.PE_ERRORCODE

        """
        library = self.library

        pe_GetStatusStr = library.PE_GetStatusStr
        pe_GetStatusStr.argtypes = [PE_STATUS]
        pe_GetStatusStr.restype = c_char_p

        statusstring = pe_GetStatusStr(pestatuscode)
        return statusstring
    
    def NKT_LibraryVersion(self):
        """
        Retrieves library version number.

        """
        library = self.library
        
        #Retrieves version number of library
        pe_LibraryVersion = library.PE_GetLibraryVersion
        pe_LibraryVersion.restype = c_int
        
        library_vers = pe_LibraryVersion()
        return library_vers
    
    def NKT_GetSystemCount(self, peHandle):
        """
        Retrieves number of systems, connected or not.

        """
        library = self.library
        
        #Retrieves number of systems available in config file
        pe_GetSystemCount = library.PE_GetSystemCount
        pe_GetSystemCount.argtypes = [CPE_HANDLE]
        pe_GetSystemCount.restype = c_int
        
        count = pe_GetSystemCount(peHandle)
        return count
        
    def NKT_GetWavelength(self, peHandle):
        """
        Returns the central wavelength, wavelength range,
            and status of retrieval of both.

        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open

        """
        library = self.library

        #Returns the central wavelength filtered by the system in nanometers
        pe_GetWavelength = library.PE_GetWavelength
        pe_GetWavelength.argtypes = [CPE_HANDLE, POINTER(c_double)]
        pe_GetWavelength.restype = PE_STATUS

        #Retrieves wavelength range of system in nanometers
        pe_GetWavelengthRange = library.PE_GetWavelengthRange
        pe_GetWavelengthRange.argtypes = [CPE_HANDLE, POINTER(c_double), POINTER(c_double)]
        pe_GetWavelengthRange.restype = PE_STATUS

        wavelength = c_double()
        getwavestatus = pe_GetWavelength(peHandle, byref(wavelength))
        minimum = c_double()
        maximum = c_double()
        getrangestatus = pe_GetWavelengthRange(peHandle, byref(minimum), byref(maximum))
        wavelength_n = wavelength.value
        minimum_n = minimum.value
        maximum_n = maximum.value
        return wavelength_n, minimum_n, maximum_n, getwavestatus, getrangestatus

    def NKT_SetWavelength(self, peHandle, wavelength):
        """
        Calibrates the instrument.
        Returns the newly calibrated central wavelength and the status of 
            calibration and wavelength retrieval.

        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
            wavelength (required) - Desired central wavelength to be filtered by system (nm)

        """
        library = self.library

        #Sets central wavelength filtered by system in nanometers
        pe_SetWavelength = library.PE_SetWavelength
        pe_SetWavelength.argtypes = [PE_HANDLE, c_double]
        pe_SetWavelength.restype = PE_STATUS

        #Retrieves central wavelength
        pe_GetWavelength = library.PE_GetWavelength
        pe_GetWavelength.argtypes = [CPE_HANDLE, POINTER(c_double)]
        pe_GetWavelength.restype = PE_STATUS

        setwavestatus = pe_SetWavelength(peHandle, wavelength)
        return setwavestatus

    def NKT_GratingStatus(self, peHandle):
        """
        Retrieves information about the grating specified by the index.
        
        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open

        """
        library = self.library

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

        gratingIndex = c_int()
        getgratingstatus = pe_GetGrating(peHandle, byref(gratingIndex))
        gindex = gratingIndex.value
        name = c_char()
        #size = ??
        gratingnamestatus = pe_GetGratingName(peHandle, gindex, byref(name), size)
        gname = name.value
        count = c_int()
        gratingcountstatus = pe_GetGratingCount(peHandle, byref(count))
        gcount = count.value
        return gindex, gname, gcount, gratingnamestatus, gratingcountstatus
    
    def NKT_GetGratingWave(self, peHandle, gratingIndex):
        """
        Returns wavelength range and extended wavelength range on the grating.

        """
        #Retrieve wavelength range of grating in nanometers
        pe_GetGratingWavelengthRange = library.PE_GetGratingWavelengthRange
        pe_GetGratingWavelengthRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthRange.restype = PE_STATUS

        #Retrieve extended wavelength range of grating in nanometers
        pe_GetGratingWavelengthExtendedRange = library.PE_GetGratingWavelengthExtendedRange
        pe_GetGratingWavelengthExtendedRange.argtypes = [CPE_HANDLE, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthExtendedRange.restype = PE_STATUS
        
        minimum = c_double()
        maximum = c_double()
        gratingrangestatus = pe_GetGratingWavelengthRange(peHandle, gratingindex, byref(minimum), byref(maximum))
        extended_min = c_double()
        extended_max = c_double()
        extendedstatus = pe_GetGratingWavelengthExtendedRange(peHandle, gratingindex, byref(extended_min), byref(extended_max))
        minimum = minimum.value
        maximum = maximum.value
        extended_min = extended_min.value
        extended_max = extended_max.value
        return minimum, maximum, extended_min, extended_max, gratingrangestatus, extendedstatus
    
    def NKT_SetGratingWave(self, peHandle, gratingIndex, wavelength):
        """
        Calibrates the central wavelength of the grating.

        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
            gratingIndex (required) - Position of the grating. Retrieved from NKT_GratingStatus
            wavelength (required) - Desired central wavelength in nm

        """
        library = self.library

        #Sets central wavelength filtered by system in nanometers
        pe_SetWavelengthOnGrating = library.PE_SetWavelengthOnGrating
        pe_SetWavelengthOnGrating.argtypes = [PE_HANDLE, c_int, c_double]
        pe_SetWavelengthOnGrating.restype = PE_STATUS

        gratingcalibstatus = pe_SetWavelengthOnGrating(peHandle, gratingIndex, wavelength)
        return gratingcalibstatus

    def NKT_HarmonicFilter(self, peHandle):
        """
        Retrieves availability of harmonic filter accessory and its status.
        
        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
       
        """
        library = self.library
        
        #Retrieves availability of harmonic filter accessory.
        pe_HasHarmonicFilter = library.PE_HasHarmonicFilter
        pe_HasHarmonicFilter.argtypes = [CPE_HANDLE]
        pe_HasHarmonicFilter.restype = c_int
        
        #Retrieves status of harmonic filter accessory.
        pe_GetHarmonicFilterEnabled = library.pe_GetHarmonicFilterEnabled
        pe_GetHarmonicFilterEnabled.argtypes = [CPE_HANDLE, POINTER(c_int)]
        pe_HasHarmonicFilter.restype = PE_STATUS
        
        harmon_avail = pe_HasHarmonicFilter(peHandle)
        enable = c_int()
        harmon_status = pe_GetHarmonicFilterEnabled(peHandle, byref(enable))
        enable = enable.value
        return harmon_avail, enable, harmon_status
    
    def NKT_EnableHarmonicFilter(self, peHandle, enable):
        """
        Sets status of harmonic filter accessory.

        Inputs:
            peHandle (required) - Handle retrieved from NKT_Open
            enable - State of harmonic filter. 0 is disabled.
        """
        library = self.library
        
        pe_SetHarmonicFilterEnabled = library.PE_SetHarmonicFilterEnabled
        pe_SetHarmonicFilterEnabled.argtypes = [PE_HANDLE, c_int]
        pe_SetHarmonicFilterEnabled.restype = PE_STATUS
        
        status = pe_SetHarmonicFilterEnabled(peHandle, enable)
        return status