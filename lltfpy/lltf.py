"""
This is the hardware class for access to the high contrast LLTF filter.

"""

from logging import getLogger
import ctypes as ct
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
        #Check platform. dll files will be added to repo in future.
        if platform.startswith('win64'):
            lib_path = './win64/PE_Filter_SDK.dll'
        elif platform.startswith('win32'):
            lib_path = './win32/PE_Filter_SDK.dll'
        else:
            raise IOError('Platform not supported.')

        self.conffile = conffile
        self._library = ct.CDLL(lib_path)
        self._handle = None
        self.name = ''


    def _open(self, index=0):
        """
        Creates and opens connection with the system.
        If handle is already available, it closes the system and reopens.

        Parameters
            index (integer) - Position of the system. Default is zero.

        """
        pe_create = self._library.PE_Create
        pe_create.argtypes = [ct.c_char_p, ct.c_void_p]#(PE_HANDLE)]
        pe_create.restype = PE_STATUS

        pe_get_system_name = self._library.PE_GetSystemName
        pe_get_system_name.argtypes = [ct.c_void_p, ct.c_int, ct.c_char_p, ct.c_int]
        pe_get_system_name.restype = PE_STATUS

        pe_open = self._library.PE_Open
        pe_open.argtypes = [ct.c_void_p, ct.c_char_p]
        pe_open.restype = PE_STATUS

        if self._handle is not None:
            self._close()
        #Create system connection
        self._handle = ct.c_void_p() #PE_HANDLE()
        create_status = pe_create(self.conffile.encode('ASCII'), ct.byref(self._handle))
        if create_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not create connection to LLTF: ' + ERROR_CODES.get(create_status.value, 'Unknown Error'))
        #Retrieve system name
        name_i = ct.c_buffer(80)
        name_status = pe_get_system_name(self._handle, index, name_i, ct.sizeof(name_i))
        if name_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Could not retrieve LLTF name: ' + ERROR_CODES.get(name_status.value, 'Unknown Error'))
        self.name = str(name_i.value)
        #Open connection to system
        open_status = pe_open(self._handle, name_i)
        # NB returns 2 if device is open by the software
        if open_status != PE_STATUS.PE_SUCCESS:
            raise LLTFError('Opening LLTF failed: '+ ERROR_CODES.get(open_status.value, 'Unknown Error'))
            
            
    def _close(self):
        """
        Closes connection with system.
        If no handle avaliable, it notifies the user and passes.

        """
        pe_close = self._library.PE_Close
        pe_close.argtypes = [ct.c_void_p]
        pe_close.restype = PE_STATUS

        pe_destroy = self._library.PE_Destroy
        pe_destroy.argtypes = [ct.c_void_p]
        pe_destroy.restype = PE_STATUS

        if self._handle is not None:
            #Close connection
            close_status = pe_close(self._handle)
            if close_status == PE_STATUS.PE_INVALID_HANDLE:
                self._handle = None
                raise LLTFError('Invalid handle destroyed:' + ERROR_CODES.get(close_status.value, 'Unknown Error'))
            elif close_status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not close system: ' + ERROR_CODES.get(close_status.value, 'Unknown Error'))
            #Destroy connection
            destroy_status = pe_destroy(self._handle)
            if destroy_status != PE_STATUS.PE_SUCCESS:
                raise LLTFError('Could not destroy system: ' + ERROR_CODES.get(destroy_status.value, 'Unknown Error'))
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
                      Grating info (dictionary) : {Grating index (integer), name (string),
                          range (float), extended range (float)}
            If any error occurs, the corresponding dictionary value will be replaced with an
                error code (string).

        """
        try:
            self._open()
            library_vers = self._library_version()
            count = self._system_count()
            wave = self._get_wave()
            minimum, maximum = self._get_range()
            gindex, gname, gcount = self._grating()
            gmin, gmax, gextmin, gextmax = self._grating_wave(gindex)
            return {'library_version': library_vers,
                      'system_name': self.name,
                      'system_count': count,
                      'central_wavelength': wave,
                      'range': (minimum, maximum),
                      'grating': {'index':gindex, 'name':gname,
                                  'range': (gmin, gmax), 'extended_range': (gextmin, gextmax)}}
        except Exception as e:
            raise e
        finally:
            self._close()


    def set_wave(self, wavelength):
        """
        Sets central wavelength of the filter.
        If desired wavelength is already set, it notifies the user and closes.
        Closes system if error incurred.

        Parameters
            conffile (string) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            wavelength (float) - Desired central wavelength in nm

        """
        pe_set_wavelength = self._library.PE_SetWavelength
        pe_set_wavelength.argtypes = [ct.c_void_p, ct.c_double]
        pe_set_wavelength.restype = PE_STATUS
        
        try:
            self._open()
            resolution = 5.0/8 #FWHM / Bandwidth is 5.0 nm
            check_wave = self._get_wave()
            if wavelength-resolution < check_wave < wavelength+resolution:
                getLogger(__name__).debug('Wavelength already set:', check_wave, 'nm')
            else:
                if 500 < wavelength < 1000: #Double wavelength if below range to use second harmonics
                    wavelength *= 2
                #Set wavelength
                set_wave_status = pe_set_wavelength(self._handle, ct.c_double(wavelength))  
                if set_wave_status == PE_STATUS.PE_INVALID_WAVELENGTH:
                    raise ValueError('Invalid input wavelength: ' + ERROR_CODES.get(set_wave_status.value, 'Unknown Error'))
                elif set_wave_status != PE_STATUS.PE_SUCCESS:
                    raise LLTFError('Could not set wavelength: ' + ERROR_CODES.get(set_wave_status.value, 'Unknown Error'))
                #Retrieve new wavelength
                new_wave = self._get_wave()
                if not wavelength-resolution < new_wave < wavelength+resolution:
                    raise LLTFError("Retrieved wavelength doesn't reflect set wavelength.")
        except Exception as e:
            raise e
        finally:
            self._close()


    def _library_version(self):
        """
        Returns version number of library.
        Returns
            library_vers (integer) - Library version number
        """
        pe_library_version = self._library.PE_GetLibraryVersion
        pe_library_version.restype = ct.c_int

        library_vers = pe_library_version()
        return library_vers


    def _system_count(self):
        """
        Retrieves the number of systems, connected or not.

        Returns
            count (integer) - Number of systems listed in config file

        """
        pe_get_system_count = self._library.PE_GetSystemCount
        pe_get_system_count.argtypes = [ct.c_void_p]
        pe_get_system_count.restype = ct.c_int

        count = pe_get_system_count(self._handle)
        return count


    def _get_wave(self):
        """
        Retrieves central wavelength filtered by system in nm.

        Returns
            wavelength (float) - Central wavelength filtered by system (nm)

        """
        pe_get_wavelength = self._library.PE_GetWavelength
        pe_get_wavelength.argtypes = [ct.c_void_p, ct.POINTER(ct.c_double)]
        pe_get_wavelength.restype = PE_STATUS

        wavelength_i = ct.c_double()
        get_wave_status = pe_get_wavelength(self._handle, ct.byref(wavelength_i))
        if get_wave_status != PE_STATUS.PE_SUCCESS:
            wavelength = 'Could not retrieve wavelength: ' + ERROR_CODES.get(get_wave_status.value, 'Unknown Error')
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
        pe_get_wavelength_range = self._library.PE_GetWavelengthRange
        pe_get_wavelength_range.argtypes = [ct.c_void_p,
                                          ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
        pe_get_wavelength_range.restype = PE_STATUS

        minimum_i = ct.c_double()
        maximum_i = ct.c_double()
        status = pe_get_wavelength_range(self._handle,
                                       ct.byref(minimum_i), ct.byref(maximum_i))
        if status != PE_STATUS.PE_SUCCESS:
                minimum = 'Could not retrieve wavelength range: ' + ERROR_CODES.get(status.value, 'Unknown Error')
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

        """
        pe_get_grating = self._library.PE_GetGrating
        pe_get_grating.argtypes = [ct.c_void_p, ct.POINTER(ct.c_int)]
        pe_get_grating.restype = PE_STATUS

        pe_get_grating_name = self._library.PE_GetGratingName
        pe_get_grating_name.argtypes = [ct.c_void_p, ct.c_int, ct.c_char_p, ct.c_int]
        pe_get_grating_name.restype = PE_STATUS

        #Retrieve grating
        gratingIndex = ct.c_int()
        get_grating_status = pe_get_grating(self._handle, ct.byref(gratingIndex))
        if get_grating_status != PE_STATUS.PE_SUCCESS:
            gindex = 'Could not retrieve grating: ' + ERROR_CODES.get(get_grating_status.value, 'Unknown Error')
        else:
            gindex = gratingIndex.value
        #Retrieve grating name
        name = ct.c_buffer(80)
        grating_name_status = pe_get_grating_name(self._handle, gindex,
                                              name, ct.sizeof(name))
        if grating_name_status != PE_STATUS.PE_SUCCESS:
            gname = 'Could not retrieve grating name: ' + ERROR_CODES.get(grating_name_status.value, 'Unknown Error')
        else:
            gname = str(name.value)
        return gindex, gname


    def _grating_wave(self, grating_index):
        """
        Returns wavelength range and extended wavelength range on the grating.

        Inputs:
            grating_index (integer) - Position of the grating. Retrieved from NKT_GratingStatus
        Returns:
            minimum (float) - Minimum available wavelength (in nm)
            maximum (float) - Maximum available wavelength
            extended_min (float) - Minimum extended wavelength (in nm)
            extended_max (float) - Maximum extended wavelength

        """
        pe_get_grating_wavelength_range = self._library.PE_GetGratingWavelengthRange
        pe_get_grating_wavelength_range.argtypes = [ct.c_void_p, ct.c_int, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
        pe_get_grating_wavelength_range.restype = PE_STATUS

        pe_get_grating_wavelength_extended_range = self._library.PE_GetGratingWavelengthExtendedRange
        pe_get_grating_wavelength_extended_range.argtypes = [ct.c_void_p, ct.c_int, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
        pe_get_grating_wavelength_extended_range.restype = PE_STATUS

        if grating_index == None:
            raise ValueError('Grating index not found.')
        minimum_i = ct.c_double()
        maximum_i = ct.c_double()
        grating_range_status = pe_get_grating_wavelength_range(self._handle, grating_index,
                                                   ct.byref(minimum_i), ct.byref(maximum_i))
        if grating_range_status != PE_STATUS.PE_SUCCESS:
            minimum = 'Could not return grating wavelength range: ' + ERROR_CODES.get(grating_range_status.value, 'Unknown Error')
            maximum = minimum
        else:
            minimum = minimum_i.value
            maximum = maximum_i.value
        extended_min_i = ct.c_double()
        extended_max_i = ct.c_double()
        extended_grating_range_status = pe_get_grating_wavelength_extended_range(self._handle, grating_index,
                                                              ct.byref(extended_min_i), ct.byref(extended_max_i))
        if extended_grating_range_status != PE_STATUS.PE_SUCCESS:
            extended_min = 'Could not return grating wavelength extended range: ' + ERROR_CODES.get(extended_grating_range_status.value, 'Unknown Error')
            extended_max = extended_min
        else:
            extended_min = extended_min_i.value
            extended_max = extended_max_i.value
        return minimum, maximum, extended_min, extended_max

