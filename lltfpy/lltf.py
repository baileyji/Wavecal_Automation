"""
This is the hardware class for access to the high contrast LLTF filter.
"""

from .lltfdll import LLTFContrast, PE_STATUS
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

        Creates and opens connection with the system. Called by status and get_wave.

        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            index (Optional) - Position of the system. Default is zero.
        Returns
            self._conn - Connection handle
            name - System name
            
        """
        LLTFdll = LLTFContrast()
        if self._conn is None:
            conffile = self.conffile
            peHandle, name, create_status, name_status, open_status = LLTFdll.LLTF_Open(conffile)
            if create_status or name_status or open_status != PE_STATUS.PE_SUCCESS:
                getLogger().debug('Could not connect to LLTF.')
                raise LLTFError('ConnectionError')
            self._conn = peHandle
            return self._conn, name

    def _close(self, peHandle):
        """

        Closes connection with system. Called by status and get_wave.

        Parameters
            peHandle (Required) - Handle to system

        """
        LLTFdll = LLTFContrast()
        if self._conn is not None:
            closestatus, destroystatus = LLTFdll.LLTF_Close(peHandle)
            if closestatus or destroystatus != PE_STATUS.PE_SUCCESS:
                getLogger().debug('Could not disconnect.')
                raise LLTFError('DisconnectionError')
            self._conn = None

    def status(self):
        """
        
        Returns status of filter as a dictionary. Called directly by client.
        
        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
                
        Returns
            status - Dictionary containing status of the filter.
                Includes:
                      Library version (int)
                      System name (string)
                      Number of possible systems (int)
                      Central wavelength (int)
                      Wavelength range (int)
                      Grating index (int)
                      Grating name (string)
                      Grating count (int)
                      Availability of harmonic filter (int) - 0 if unavailable
                      Status of harmonic filter (int) - 0 if unavailable
                      
        """
        close = False
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

        Calibrates central wavelength of the filter. Called directly by client.
        Returns newly calibrated wavelength.

        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            wavelength (Required, int) - Desired central wavelength in nm
        Returns
            new_wave (int) - Newly set wavelength, retrieved from the filter.
            
        """
        close = False
        LLTFdll = LLTFContrast()
        try:
            peHandle, name = self._open()
            prev_wave, prev_min, prev_max, wavestatus, rangestatus = LLTFdll.LLTF_GetWavelength(peHandle)
            if wavelength == prev_wave:
                getLogger().debug('Wavelength already set.')
                raise RuntimeError('Already calibrated.')
            setwavestatus = LLTFdll.LLTF_SetWavelength(peHandle, wavelength)
            new_wave, new_min, new_max, newwavestatus, newrangestatus = LLTFdll.LLTF_GetWavelength(peHandle)
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
    
        Retrieves central wavelength and wavelength range filtered by system in nm. Called by _status.

        Parameters
            peHandle - Handle to system 
        Returns
            wave (int) - Central wavelength filtered by system (nm)
            minimum (int) - Minimum wavelength filtered (nm)
            maximum (int) - Maximum wavleneght filtered (nm)
            
        """
        LLTFdll = LLTFContrast()
        wave, minimum, maximum, wavestatus, rangestatus = LLTFdll.LLTF_GetWavelength(peHandle)
        if wavestatus or rangestatus != PE_STATUS.PE_SUCCESS:
                getLogger().debug('Could not retrieve wavelength.')
                raise LLTFError('StatusRetrievalError')
        return wave, minimum, maximum
    
    def library_version(self):
        """
        
        Return version number of library. Called by status.
        
        Returns
            library_vers (int) - Library version number
        
        """
        LLTFdll = LLTFContrast()
        library_vers = LLTFdll.LLTF_LibraryVersion()
        return library_vers
    
    def system_count(self, peHandle):
        """
        
        Retrieves the number of systems, connected or not. Called by status.
        
        Parameters
            peHandle - Connection handle
        Returns
            count (int) - Number of systems listed in config file
            
        """
        LLTFdll = LLTFContrast()
        count = LLTFdll.LLTF_GetSystemCount(peHandle)
        return count
    
    def grating(self, peHandle):
        """

        Retrieves LLTF grating info. Called by status.
        
        Parameters
            peHandle - Connection handle
        Returns
            gindex (int)- Grating index
            gname (string) - Grating name
            gcount (int) - Grating number

        """
        LLTFdll = LLTFContrast()
        gindex, gname, gcount, getgratingstatus, gratingnamestatus, gratingcountstatus = LLTFdll.LLTF_GratingStatus(peHandle)
        if getgratingstatus or gratingnamestatus or gratingcountstatus != PE_STATUS.PE_SUCCESS:
            getLogger().debug('Could not retrieve grating.')
            raise LLTFError('GratingError')
        return gindex, gname, gcount

    def harmonic_filter(self, peHandle):
        """
        
        Checks availability and status of harmonic filter. Called by status.

        Parameters
            peHandle - Connection handle
        Returns
            avail (int) - Availability of harmonic filter. 0 if unavailable.
            enable (int) - Status of harmonic filter. 0 if disabled.
            
        """
        LLTFdll = LLTFContrast()
        avail, enable, harmon_status = LLTFdll.LLTF_HarmonicFilter(peHandle)
        if harmon_status != PE_STATUS.PE_SUCCESS:
            getLogger().debug('Could not find harmonic filter status.')
            raise LLTFError('HarmonicFilterError')
        return avail, enable