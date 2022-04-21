"""
This is the hardware class for access to the high contrast LLTF filter.

"""

from logging import getLogger
from ctypes import *
from sys import platform
from enum import IntEnum


ERROR_CODES = {0: 'Success',
               1: 'Supplied handle is corrupted or has a NULL value.',
               2: 'Communication with system failed.',
               3: 'Configuration file is missing.',
               4: 'Configuration file is corrupted.',
               5: 'Requested wavelength is out of bounds.',
               6: 'No harmonic filter present in the system configuration.',
               7: 'Requested filter does not match any available.',
               8: 'An unknown status code has been returned by the system.',
               9: 'Requested grating does not match any available.',
               10: 'Output buffer has a NULL value.',
               11: 'Output buffer size is too small to receive the value.',
               12: 'The system configuration is not supported by this SDK.',
               13: 'No filter connected.'}


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
        If handle is already available, it closes the system and reopens.

        Parameters
            index (integer) - Position of the system. Default is zero.

        """
        pe_Create = self._library.PE_Create
        pe_Create.argtypes = [c_char_p, c_void_p]#(PE_HANDLE)]
        pe_Create.restype = PE_STATUS

        pe_GetSystemName = self._library.PE_GetSystemName
        pe_GetSystemName.argtypes = [c_void_p, c_int, c_char_p, c_int]
        pe_GetSystemName.restype = PE_STATUS

        pe_Open = self._library.PE_Open
        pe_Open.argtypes = [c_void_p, c_char_p]
        pe_Open.restype = PE_STATUS

        if self._handle is not None:
            self._close()
        #Create system connection
        self._handle = c_void_p() #PE_HANDLE()
        create_status = pe_Create(self.conffile.encode('ASCII'), byref(self._handle))
        if create_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not create connection to LLTF: ' + ERROR_CODES.get(open_status.value, 'Unknown Error'))
        #Retrieve system name
        name_i = c_buffer(80)
        name_status = pe_GetSystemName(self._handle, index, name_i, sizeof(name_i))
        if name_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not retrieve LLTF name: ' + ERROR_CODES.get(open_status.value, 'Unknown Error'))
        self.name = str(name_i.value)
        #Open connection to system
        open_status = pe_Open(self._handle, name_i)
        # NB returns 2 if device is open by the software
        if open_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Opening LLTF failed: '+ ERROR_CODES.get(open_status.value, 'Unknown Error'))


    def _close(self):
        """
        Closes connection with system.
        If no handle avaliable, it notifies the user and passes.

        """
        pe_Close = self._library.PE_Close
        pe_Close.argtypes = [c_void_p]
        pe_Close.restype = PE_STATUS

        pe_Destroy = self._library.PE_Destroy
        pe_Destroy.argtypes = [c_void_p]
        pe_Destroy.restype = PE_STATUS

        if self._handle is not None:
            #Close connection
            closestatus = pe_Close(self._handle)
            if closestatus == PE_STATUS.PE_INVALID_HANDLE:
                self._handle = None
                raise LLTFError('Invalid handle:' + ERROR_CODES.get(open_status.value, 'Unknown Error'))
            elif closestatus != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not close system:' + ERROR_CODES.get(open_status.value, 'Unknown Error'))
            #Destroy connection
            destroystatus = pe_Destroy(self._handle)
            if destroystatus != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not destroy system:'+ ERROR_CODES.get(open_status.value, 'Unknown Error'))
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
            gmin, gmax, gextmin, gextmax = self._grating_wave(gindex)
            havail, henable = self._harmonic_filter()
            return {'library_version': library_vers,
                      'system_name': self.name,
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
        If desired wavelength is already set, it notifies the user and closes.

        Parameters
            conffile (string) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            wavelength (float) - Desired central wavelength in nm

        """
        pe_SetWavelength = self._library.PE_SetWavelength
        pe_SetWavelength.argtypes = [c_void_p, c_double]
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
                    raise ValueError('Invalid input wavelength:' + ERROR_CODES.get(open_status.value, 'Unknown Error'))
                elif status != PE_STATUS.PE_SUCCESS:
                    raise LLTFError('Could not set wavelength:' + ERROR_CODES.get(open_status.value, 'Unknown Error'))
                #Retrieve new wavelength
                new_wave = self._get_wave()
                if new_wave != wavelength:
                    raise LLTFError("Retrieved wavelength doesn't reflect set wavelength.")
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
        pe_GetSystemCount.argtypes = [c_void_p]
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
        pe_GetWavelength.argtypes = [c_void_p, POINTER(c_double)]
        pe_GetWavelength.restype = PE_STATUS

        wavelength_i = c_double()
        status = pe_GetWavelength(self._handle, byref(wavelength_i))
        if status != PE_STATUS.PE_SUCCESS:
            wavelength = 'Could not retrieve wavelength:' + ERROR_CODES.get(open_status.value, 'Unknown Error')
        else:
            wavelength = wavelength_i.value
        return wavelength


    def _get_range(self):
        """
        Retrieves wavelength range filtered by system in nm.

        Returns
            minimum (float) - Range minimum
            maximum (float) - Range maximum

        """
        pe_GetWavelengthRange = self._library.PE_GetWavelengthRange
        pe_GetWavelengthRange.argtypes = [c_void_p,
                                          POINTER(c_double), POINTER(c_double)]
        pe_GetWavelengthRange.restype = PE_STATUS

        minimum_i = c_double()
        maximum_i = c_double()
        status = pe_GetWavelengthRange(self._handle,
                                       byref(minimum_i), byref(maximum_i))
        if status != PE_STATUS.PE_SUCCESS:
                minimum = 'Could not retrieve wavelength range:' + ERROR_CODES.get(open_status.value, 'Unknown Error')
                maximum = minimum
        else:
            minimum = minimum_i.value
            maximum = maximum_i.value
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
        pe_GetGrating.argtypes = [c_void_p, POINTER(c_int)]
        pe_GetGrating.restype = PE_STATUS

        pe_GetGratingName = self._library.PE_GetGratingName
        pe_GetGratingName.argtypes = [c_void_p, c_int, c_char_p, c_int]
        pe_GetGratingName.restype = PE_STATUS

        pe_GetGratingCount = self._library.PE_getGratingCount
        pe_GetGratingCount.argtypes = [c_void_p, POINTER(c_int)]
        pe_GetGratingCount.restype = PE_STATUS

        #Retrieve grating
        gratingIndex = c_int()
        getgratingstatus = pe_GetGrating(self._handle, byref(gratingIndex))
        if getgratingstatus != PE_STATUS.PE_SUCCESS:
            gindex = 'Could not retrieve grating:' + ERROR_CODES.get(open_status.value, 'Unknown Error')
        else:
            gindex = gratingIndex.value
        #Retrieve grating name
        name = c_buffer(80)
        gratingnamestatus = pe_GetGratingName(self._handle, gindex,
                                              name, sizeof(name))
        if gratingnamestatus != PE_STATUS.PE_SUCCESS:
            gname = 'Could not retrieve grating name:' + ERROR_CODES.get(open_status.value, 'Unknown Error')
        else:
            gname = str(name.value)
        #Retrieve grating count
        count = c_int()
        gratingcountstatus = pe_GetGratingCount(self._handle, byref(count))
        if gratingcountstatus != PE_STATUS.PE_SUCCESS:
            gcount = 'Could not retrieve grating count:' + ERROR_CODES.get(open_status.value, 'Unknown Error')
        else:
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
        pe_GetGratingWavelengthRange.argtypes = [c_void_p, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthRange.restype = PE_STATUS

        pe_GetGratingWavelengthExtendedRange = self._library.PE_GetGratingWavelengthExtendedRange
        pe_GetGratingWavelengthExtendedRange.argtypes = [c_void_p, c_int, POINTER(c_double), POINTER(c_double)]
        pe_GetGratingWavelengthExtendedRange.restype = PE_STATUS

        if gratingIndex == None:
            raise ValueError('Grating index not found.')
        minimum_i = c_double()
        maximum_i = c_double()
        rangestatus = pe_GetGratingWavelengthRange(self._handle, gratingindex,
                                                   byref(minimum_i), byref(maximum_i))
        if rangestatus != PE_STATUS.PE_SUCCESS:
            minimum = 'Could not return grating wavelength range:' + ERROR_CODES.get(open_status.value, 'Unknown Error')
            maximum = minimum
        else:
            minimum = minimum_i.value
            maximum = maximum_i.value
        extended_min_i = c_double()
        extended_max_i = c_double()
        extendedstatus = pe_GetGratingWavelengthExtendedRange(self._handle, gratingindex,
                                                              byref(extended_min_i), byref(extended_max_i))
        if extendedstatus != PE_STATUS.PE_SUCCESS:
            extended_min = 'Could not return grating wavelength extended range:' + ERROR_CODES.get(open_status.value, 'Unknown Error')
            extended_max = extended_min
        else:
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
        pe_HasHarmonicFilter.argtypes = [c_void_p]
        pe_HasHarmonicFilter.restype = c_int

        pe_GetHarmonicFilterEnabled = self._library.pe_GetHarmonicFilterEnabled
        pe_GetHarmonicFilterEnabled.argtypes = [c_void_p, POINTER(c_int)]
        pe_HasHarmonicFilter.restype = PE_STATUS

        avail = pe_HasHarmonicFilter(self._handle)
        enable_i = c_int()
        status = pe_GetHarmonicFilterEnabled(self._handle, byref(enable_i))
        if status != PE_STATUS.PE_SUCCESS:
            enable = 'Could not find harmonic filter status:' + ERROR_CODES.get(open_status.value, 'Unknown Error')
        else:
            enable = enable_i.value
        return avail, enable
