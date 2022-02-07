"""
This is the hardware class for access to the high contrast LLTF filter.
"""

from .lltfdll import NKTContrast, PE_STATUS
from logging import getLogger


class LLTFError(Exception):
    pass


class LLTF:
    """

    Hardware class for connection to the LLTF High Contrast filter.

    """

    def __init__(self, conffile):
        self._conn = None

    def _open(self, index=0):
        """

        Creates and opens connection with the system. 
        Returns connection handle.

        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            index (Optional) - Position of the system. Default is zero.

        """
        NKT = NKTContrast()
        if self._conn is None:
            conffile = self.conffile
            peHandle, name, create_status, open_status = NKT.NKT_Open(conffile)
            if create_status or open_status != PE_STATUS.PE_SUCCESS:
                getLogger().debug('Could not connect to LLTF.')
                raise LLTFError('ConnectionError')
            self._conn = peHandle
            return self._conn, name

    def _close(self, peHandle):
        """

        Closes connection with system.

        Parameters
            peHandle (Required) - Handle to system

        """
        NKT = NKTContrast()
        if self._conn is not None:
            closestatus, destroystatus = NKT.NKT_Close(peHandle)
            if closestatus or destroystatus != PE_STATUS.PE_SUCCESS:
                getLogger().debug('Could not disconnect.')
                raise LLTFError('DisconnectionError')
            self._conn = None

    def status(self):
        """
        
        Returns status of filter as a dictionary.
        Status includes:
            Library version
            System name
            System handle
            Central wavelength
            and wavelength range

        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
        """
        close = False
        NKT = NKTContrast()
        try:
            peHandle, name = self._open()
            library_vers = self.library_version()
            wave, minimum, maximum = self.get_wave(peHandle)
            gindex, gname, gcount = self.grating(peHandle)
            count = self.system_count(peHandle)
            havail, henable = self.harmonic_filter(peHandle)
            status = {'library_version': library_vers,
                      'system_count': count,
                      'system_name': name,
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
                self._close(peHandle)
        return False
    
    def set_wave(self, wavelength):
        """

        Calibrates central wavelength of the filter. 
        Returns newly calibrated wavelength.

        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            wavelength (Required) - Desired central wavelength in nm

        """
        close = False
        NKT = NKTContrast()
        try:
            peHandle, name = self._open()
            prev_wave, prev_min, prev_max, wavestatus, rangestatus = NKT.NKT_GetWavelength(peHandle)
            if wavelength == prev_wave:
                getLogger().debug('Wavelength already set.')
                raise RuntimeError('Already calibrated.')
            setwavestatus = NKT.NKT_SetWavelength(peHandle, wavelength)
            new_wave, new_min, new_max, newwavestatus, newrangestatus = NKT.NKT_GetWavelength(peHandle)
            if wavestatus or rangestatus or setwavestatus or newwavestatus or newrangestatus != PE_STATUS.PE_SUCCESS:
                getLogger().debug('Could not set wavelength.')
                raise LLTFError('WavelengthSettingError')
            elif new_wave == prev_wave:
                getLogger().debug('Calibration could not occur.')
                raise RuntimeError('WavelengthSettingError')
            else:
                return True, new_wave
        except:
            close = True
        finally:
            if close:
                self._close(peHandle)
        return False
    
    def get_wave(self, peHandle):
        """
    
        Retrieves central wavelength and wavelength range filtered by system in nm.

        """
        NKT = NKTContrast()
        wave, minimum, maximum, wavestatus, rangestatus = NKT.NKT_GetWavelength(peHandle)
        if wavestatus or rangestatus != PE_STATUS.PE_SUCCESS:
                getLogger().debug('Could not retrieve wavelength.')
                raise LLTFError('StatusRetrievalError')
        return wave, minimum, maximum
    
    def library_version(self):
        """
        
        Return version number of library.
        
        """
        NKT = NKTContrast()
        library_vers = NKT.NKT_LibraryVersion()
        return library_vers
    
    def system_count(self, peHandle):
        """
        
        Retrieves the number of systems, connected or not.
        
        """
        NKT = NKTContrast()
        count = NKT.NKT_GetSystemCount(peHandle)
        return count
    
    def grating(self, peHandle):
        """

        Retrieves the LLTF grating index, name, and number.

        """
        NKT = NKTContrast()
        gindex, gname, gcount, gratingnamestatus, gratingcountstatus = NKT.NKT_GratingStatus(peHandle)
        if gratingnamestatus or gratingcountstatus != PE_STATUS.PE_SUCCESS:
            getLogger().debug('Could not retrieve grating.')
            raise LLTFError('GratingError')
        return gindex, gname, gcount

    def harmonic_filter(self, peHandle):
        """
        
        Checks availability and status of harmonic filter.

        """
        NKT = NKTContrast()
        avail, enable, harmon_status = NKT.NKT_HarmonicFilter(peHandle)
        if harmon_status != PE_STATUS.PE_SUCCESS:
            getLogger().debug('Could not find harmonic filter status.')
            raise LLTFError('HarmonicFilterError')
        return avail, enable