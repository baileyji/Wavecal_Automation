/*
 * Photon etc., Inc. Confidential. Do Not Distribute. 
 * This is proprietary work which is protected under copyright laws.
 * This code may only be used with a valid license from Photon etc.
 *
 */

#ifndef	_PE_FILTER_H_
#define	_PE_FILTER_H_

//! Export/Import macro for library symbol.
#ifdef PEFILTERSDK_EXPORTS
#	define PEFILTERSDK_API	__declspec(dllexport)
#else
#	define PEFILTERSDK_API	__declspec(dllimport)
#endif

//! Status code definitions.
typedef enum
{
	PE_SUCCESS = 0,				//!< Successful operation
	PE_INVALID_HANDLE,			//!< Handle is already deleted or null
	PE_FAILURE,					//!< Instrument communication failure
	PE_MISSING_CONFIGFILE,		//!< Configuration file is missing
	PE_INVALID_CONFIGURATION,	//!< Configuration file is corrupted
	PE_INVALID_WAVELENGTH,		//!< Wavelength is out of bound
	PE_MISSSING_HARMONIC_FILTER,//!< No harmonic present in the system
	PE_INVALID_FILTER,			//!< The requested filter doesn't exist
	PE_UNKNOWN,					//!< Unknown status
	PE_INVALID_GRATING,			//!< The requested grating doesn't exist
	PE_INVALID_BUFFER,			//!< The buffer is null
	PE_INVALID_BUFFER_SIZE,		//!< The buffer is to small
	PE_UNSUPPORTED_CONFIGURATION,//!< The filter configuration is unsupported
	PE_NO_FILTER_CONNECTED		//!< No filter is connected
} PE_STATUS;


typedef void* PE_HANDLE;
typedef const void* CPE_HANDLE;

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// MANAGEMENT FUNCTIONS
//=============================================================================

//! Creates filter resource with configuration file but do not connect to filter.
//! @param[in] conffile Full path to the XML configuration file
//! @param[out] peHandle Handle to the resource created
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_Create(const char* conffile, PE_HANDLE* peHandle);

//! Destroys filter resource previously created with PE_Create().
//! @param[in] peHandle Handle to the resource
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_Destroy(PE_HANDLE peHandle);

//! Gets the number of systems available in the configuration file.
//! @param[in] peHandle Handle to the resource
//! @return Number of configured systems
PEFILTERSDK_API int PE_GetSystemCount(CPE_HANDLE peHandle);

//! Gets the name of the system specified by index in the list of systems.
//! @param[in] peHandle Handle to the resource
//! @param[in] index Position of the system to get
//! @param[out] name String defining uniquely a system
//! @param[in] size Maximum length of the given string buffer
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetSystemName(CPE_HANDLE peHandle, int index, char* name, int size);

//! Gets the version number of this library.
//! @return Version number encoded as (major << 16) + (minor << 8) + bugfix
PEFILTERSDK_API int PE_GetLibraryVersion(void);

//! Gets the string explaining the given status code.
//! @param[in] code Status code to describe
//! @return String describing the status code, do not free memory
PEFILTERSDK_API const char* PE_GetStatusStr(PE_STATUS code);

//=============================================================================
// LLTF CONTRAST CONTROL FUNCTIONS
//=============================================================================

//! Opens a communication channel with the filter with the given name.
//! @param[in] peHandle Handle to the resource
//! @param[in] name String defining uniquely a system
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_Open(PE_HANDLE peHandle, const char* name);

//! Closes the communication and reset the filter.
//! @param[in] peHandle Handle to the resource
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_Close(PE_HANDLE peHandle);

//! Gets the current central wavelength filtered by the system.
//! @param[in] peHandle Handle to the resource
//! @param[out] wavelength Central wavelength in nanometers
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetWavelength(CPE_HANDLE peHandle, double* wavelength);

//! Sets the central wavelength of the system.
//! @param[in] peHandle Handle to the resource
//! @param[out] wavelength Central wavelength in nanometers
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_SetWavelength(PE_HANDLE peHandle, double wavelength);

//! Gets the wavelength range of the system.
//! @param[in] peHandle Handle to the resource
//! @param[out] minimum Minimum wavelength in nanometers
//! @param[out] maximum Maximum wavelength in nanometers
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetWavelengthRange(CPE_HANDLE peHandle, double* minimum, double* maximum);

//! Gets the availability of the harmonic filter accessory.
//! @param[in] peHandle Handle to the resource
//! @return A non-zero value is returned if available, otherwise zero is returned
PEFILTERSDK_API int PE_HasHarmonicFilter(CPE_HANDLE peHandle);

//! Gets the status of the harmonic filter accessory.
//! @param[in] peHandle Handle to the resource
//! @param[out] enable State of the harmonic filter
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetHarmonicFilterEnabled(CPE_HANDLE peHandle, int* enable);

//! Sets the status of the harmonic filter accessory.
//! @param[in] peHandle Handle to the resource
//! @param[in] enable State of the harmonic filter
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_SetHarmonicFilterEnabled(PE_HANDLE peHandle, int enable);

//=============================================================================
// LLTF CONTRAST CONTROL ADVANCED FUNCTIONS
//=============================================================================

//! Gets the number of gratings of the system.
//! @param[in] peHandle Handle to the resource
//! @param[out] count grating count
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetGratingCount(CPE_HANDLE peHandle, int* count);

//! Gets the name of the grating specified by index.
//! @param[in] peHandle Handle to the resource
//! @param[in] gratingIndex Position of the grating to get (zero-based)
//! @param[out] name String defining uniquely a grating
//! @param[in] size Maximum length of the given string buffer
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetGratingName(CPE_HANDLE peHandle, int gratingIndex, char* name, int size);

//! Gets the regular wavelength range of the grating specified by index.
//! @param[in] peHandle Handle to the resource
//! @param[in] gratingIndex Position of the grating (zero-based)
//! @param[out] minimum Minimum wavelength in nanometers
//! @param[out] maximum Maximum wavelength in nanometers
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetGratingWavelengthRange(CPE_HANDLE peHandle, int gratingIndex, double* minimum, double* maximum);

//! Gets the extended wavelength range of the grating specified by index.
//! @param[in] peHandle Handle to the resource
//! @param[in] gratingIndex Position of the grating (zero-based)
//! @param[out] minimum Minimum wavelength in nanometers
//! @param[out] maximum Maximum wavelength in nanometers
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetGratingWavelengthExtendedRange(CPE_HANDLE peHandle, int gratingIndex, double* extMinimum, double* extMaximum);

//! Sets the central wavelength of the system with the grating specified by index.
//! @param[in] peHandle Handle to the resource
//! @param[in] gratingIndex Position of the grating to use (zero-based)
//! @param[out] wavelength Central wavelength in nanometers
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_SetWavelengthOnGrating(PE_HANDLE peHandle, int gratingIndex, double wavelength);

//! Gets the current grating used by the system.
//! @param[in] peHandle Handle to the resource
//! @param[out] gratingIndex Position of the grating used by the system
//! @return Error code
PEFILTERSDK_API PE_STATUS PE_GetGrating(PE_HANDLE peHandle, int* gratingIndex);



#ifdef __cplusplus
}
#endif

#endif	// _PE_FILTER_H_
