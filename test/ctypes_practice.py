from enum import IntEnum
import ctypes as ct
print(ct.cdll.msvcrt)
libc = ct.cdll.msvcrt

#Test printf and using c library
printf = libc.printf
printf(b"Hello, %s\n",  b"World!")
printf(b'Hello World!')

#Test argtypes - strlen
strlen = libc.strlen
strlen.argtypes = [ct.c_char_p]
string = b'Hello World!'
#s = string.encode('ASCII')
print(strlen(string))

#Test restypes - atol
atol = libc.atol
atol.argtypes = [ct.c_char_p]
atol.restype = ct.c_long
a_number = b'200000000.34'
num_res = atol(a_number)
#python_num = int(a_number)
print('Number (C): ', num_res)
print(type(num_res))

#Test restypes but with doubles - atof
atof = libc.atof
atof.argtypes = [ct.c_char_p]
atof.restype = ct.c_double
a_number = b'123.45'
num = atof(a_number)
python_res = float(a_number)
print('Number (c):', num, '\n',
      'Number (Python):', python_res)
print(type(num))
print(type(python_res))

#Test strchr - restypes with strings and bytes
strchr = libc.strchr
strchr.argtypes = [ct.c_char_p, ct.c_int]
strchr.restype = ct.c_char_p
string = b'Hello, World!'
ch = ord('o')
new_string = strchr(string, ch)
new_chr = ord('r')
newnew = strchr(new_string, new_chr)
print('First:', new_string, '\n',
      'Second:', newnew)
print('type of first:', type(new_string), '\n',
      'type of second:', type(newnew))

#Test out params - strcpy
strcpy = libc.strcpy
strcpy.argtypes = [ct.c_char_p, ct.c_char_p]
strcpy.restype = ct.c_char_p
string = b'Hello World!'
dest = ct.create_string_buffer(12)
print(strcpy(dest, string))

#Testing out params, but with POINTER instead of create_string_buffer - strcpy
strcpy = libc.strcpy
strcpy.argtypes = [ct.POINTER(ct.c_char_p), ct.c_char_p]
strcpy.restype = ct.c_char_p
string = b'Hello World!'
dest = ct.c_char_p()
strcpy(ct.byref(dest), string)
print(strcpy(ct.byref(dest), string))

#Testing out byref and .value
frexp = libc.frexp
frexp.argtypes = [ct.c_double, ct.POINTER(ct.c_int)]
frexp.restype = ct.c_double
num = 275
exp = ct.c_int()
res = frexp(num, ct.byref(exp))
#new = cast(exp, c_void_p).value
print(exp)
print('Fraction is:', res, 'Exponent is: ', exp.value)

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
    """
    Class using the custom class
    
    """
    def __init__(self):
        """
        Load c library
        
        """
        print(ct.cdll.msvcrt)
        self.libc = ct.cdll.msvcrt
    
    def Newfunc(self, string):
        """
        Use atoi to test how custom class works
        
        """
        print('In Newfunc!')
        libc = self.libc
        atoi = libc.atoi
        string = string.encode('ASCII')
        print(string)
        atoi.argtypes = [ct.c_char_p]
        atoi.restype = PE_STATUS
        num = atoi(string)
        # =============================================================================
        # if num == PE_STATUS.PE_MISSING_CONFIGFILE:
        #     print('True!')
        # =============================================================================
        return num

classs = NewClass()
print(classs.Newfunc('Hello world'))
# =============================================================================
# pointerthing = pointer(num)
# print(pointerthing.value)
# =============================================================================

