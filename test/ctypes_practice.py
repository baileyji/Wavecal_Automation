from enum import IntEnum
from ctypes import *
print(cdll.msvcrt)
libc = cdll.msvcrt

# =============================================================================
# printf = libc.printf
# printf(b"Hello, %s\n",  b"World!")
# printf(b'Hello World!')
# =============================================================================

# =============================================================================
# #Test argtypes
# strlen = libc.strlen
# strlen.argtypes = [c_char_p]
# string = b'Hello World!'
# #s = string.encode('ASCII')
# print(strlen(string))
# =============================================================================
# =============================================================================
# #Test restypes
# atol = libc.atol
# atol.argtypes = [c_char_p]
# atol.restype = c_long
# a_number = b'200000000.34'
# num_res = atol(a_number)
# #python_num = int(a_number)
# print('Number (C): ', num_res)
# print(type(num_res))
# =============================================================================
# =============================================================================
# atof = libc.atof
# atof.argtypes = [c_char_p]
# atof.restype = c_double
# a_number = b'123.45'
# num = atof(a_number)
# python_res = float(a_number)
# print('Number (c):', num, '\n',
#       'Number (Python):', python_res)
# print(type(num))
# print(type(python_res))
# =============================================================================
strchr = libc.strchr
strchr.argtypes = [c_char_p, c_int]
strchr.restype = c_char_p
string = b'Hello, World!'
ch = ord('o')
new_string = strchr(string, ch)
new_chr = ord('r')
newnew = strchr(new_string, new_chr)
print('First:', new_string, '\n',
      'Second:', newnew)
print('type of first:', type(new_string), '\n',
      'type of second:', type(newnew))
#Test out params
# =============================================================================
# strcpy = libc.strcpy
# strcpy.argtypes = [c_char_p, c_char_p]
# strcpy.restype = c_char_p
# string = b'Hello World!'
# dest = create_string_buffer(12)
# print(strcpy(dest, string))
# =============================================================================
# =============================================================================
# strcpy = libc.strcpy
# strcpy.argtypes = [POINTER(c_char_p), c_char_p]
# strcpy.restype = c_char_p
# string = b'Hello World!'
# dest = c_char_p()
# strcpy(byref(dest), string)
# print(strcpy(byref(dest), string))
# =============================================================================
# =============================================================================
# frexp = libc.frexp
# frexp.argtypes = [c_double, POINTER(c_int)]
# frexp.restype = c_double
# num = 275
# exp = c_int()
# res = frexp(num, byref(exp))
# #new = cast(exp, c_void_p).value
# print(exp)
# print('Fraction is:', res, 'Exponent is: ', exp.value)
# =============================================================================

#Testing custom classes

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
        
# =============================================================================
# if PE_STATUS.PE_INVALID_HANDLE == 1:
#     print('Success!')
# else:
#     print('Failure!')
# =============================================================================
class NewClass():
    def __init__(self):
        print(cdll.msvcrt)
        self.libc = cdll.msvcrt
    
    def Newfunc(self, string):
        print('In Newfunc!')
        libc = self.libc
        atoi = libc.atoi
        atoi.argtypes = [c_char_p]
        atoi.restype = PE_STATUS
        num = atoi(string)
        # =============================================================================
        # if num == PE_STATUS.PE_MISSING_CONFIGFILE:
        #     print('True!')
        # =============================================================================
        return num

# =============================================================================
# pointerthing = pointer(num)
# print(pointerthing.value)
# =============================================================================
