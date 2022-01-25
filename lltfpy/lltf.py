from .lltfdll import NKTContrast, PE_STATUS


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

        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            index (Optional) - Position of the system. Default is zero.

        """
        NKT = NKTContrast()
        if self._conn is None:
            conffile = self.conffile
            library_vers, num_sys, peHandle, name, create_status, open_status = NKT.NKT_Open(conffile)
            if create_status or open_status != PE_STATUS.PE_SUCCESS:
                raise RuntimeError
            self._conn = peHandle
            return self._conn

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
                raise RuntimeError
            self._conn = None

    def set_wave(self, wavelength):
        """

        Calibrates central wavelength of the filter.

        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'
            wavelength (Required) - Desired central wavelength in nm

        """
        close = False
        NKT = NKTContrast()
        try:
            peHandle = self._open()
            prev_wave, prev_min, prev_max, wavestatus, rangestatus = NKT.NKT_Wavelength(peHandle)
            new_wave, calibstatus, new_wavestatus = NKT.NKT_Calibrate(peHandle, wavelength)
            return True
        except wavelength == prev_wave:
            close = True
        except wavestatus or rangestatus or new_wavestatus or calibstatus != PE_STATUS.PE_SUCCESS:
            close = True
        except new_wave == prev_wave:
            close = True
        finally:
            if close:
                self._close(peHandle)
        return False

    def get_wave(self):
        """
        Returns current central wavelength and wavelength range of filter.

        Parameters
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'

        """
        close = False
        NKT = NKTContrast()
        try:
            peHandle = self._open()
            wave, minimum, maximum, wavestatus, rangestatus = NKT.NKT_Wavelength(peHandle)
            return True
        except wavestatus or rangestatus != PE_STATUS.PE_SUCCESS:
            close = True
        finally:
            if close:
                self._close(peHandle)
        return False

    def grating_wave(self, wavelength):
        """

        Calibrates the LLTF grating.

        Parameters
            wavelength (Required) - Central wavelength to calibrate the grating to.
            conffile (Required) - Path to configuration file.
                Usually in 'C:\Program Files (x86)\Photon etc\PHySpecV2\system.xml'

        """
        close = False
        NKT = NKTContrast()
        try:
            peHandle = self._open()
            gindex, minimum, maximum, ext_min, ext_max, namestat, countstat, rangestat, extstat = NKT.NKT_GratingStatus(peHandle)
            central_wave = (maximum - minimum)/2 + minimum
            min_n, max_n, calibstat, rangestat_n = NKT.NKT_CalibrateGrating(peHandle, gindex, wavelength)
            new_wave = (max_n - min_n)/2 + min_n
            return True
        except namestat or countstat or rangestat or extstat or calibstat or rangestat_n != PE_STATUS.PE_SUCCESS:
            close = True
        except wavelength == central_wave:
            close = True
        except new_wave == central_wave:
            close = True
        finally:
            if close:
                self._close(peHandle)
        return False
