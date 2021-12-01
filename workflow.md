NKT_Open

  -Creates handle
  -Tells user what new handle is
  -Retrieves number of systems
  -Gets name of system by retrieving first system number possible
  -Check state of name retrieval
  -If status is not PE_SUCCESS, fail state. Let user know.
  -Retrieves library version
  -Connects to system
  -Check status of system connection
  -If status is not PE_SUCCESS, fail state. Let user know.
  -Tells user the library version, number of systems, handle to system, system name

NKT_StatusStr

  -Retrieves definition of status string (only there if needed by the user)

NKT_Wavelength

  -Retrieves current wavelength of system
  -Checks status of retrieval
  -If PE_STATUS is PE_SUCCESS, retrieves the wavelength
  -Otherwise, lets user know
  -Gets wavelength range too
  -Checks status of retrieval
  -If PE_STATUS is PE_SUCCESS, tells user the wavelength range
  -If not success, lets user know
  
NKT_Calibrate

  -Sets wavelength
  -If state = PE_SUCCESS, sets wavelength, retrieves status to let user know the new wavelength is set

NKT_GratingStatus

  -Retrieves grating index
  -Checks status of grating index retrieval
  -if state doesn’t = PE_SUCCESS, fail state.
  -Retrieve grating name
  -Checks status of grating name retrieval
  -If state not equal PE_SUCCESS. fail state.
  -Retrieves grating count.
  -Checks status of grating count retrieval.
  -If state not equal PE_SUCCESS, fail state.
  -Retrieves grating range
  -Checks status of grating wavelength range retrieval
  -If state not equal PE_SUCCESS, fail state.
  -Retrieves extended grating range
  -Checks status of extended grating range retrieval
  -If state not equal PE_SUCCESS, fail state.
  -Prints out grating name, grating count number, grating wavelength range, and grating extended wavelength range

NKT_CalibrateGrating

  -Calibrates grating
  -Checks status of grating calibration
  -If PE_SUCCESS, lets user know and retrieves grating wavelength range

NKT_Close

  -Closes system. 
  -Lets user know the status of system closing.
  -If state not equal PE_SUCCESS, fail state.
  -Destroys system
  -Checks status of system destruction.
  -If state not equal PE_SUCCESS, fail state.
  -If both are success, lets user know.
