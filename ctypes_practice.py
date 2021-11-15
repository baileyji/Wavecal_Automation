# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 15:00:24 2021

@author: autum
"""

from ctypes import *
print(cdll.msvcrt)
libc = cdll.msvcrt

# =============================================================================
# printf = libc.printf
# printf(b"Hello, %s\n",  b"World!")
# printf(b'Hello World!')
# #Test argtypes
# strlen = libc.strlen
# strlen.argtypes = [c_char_p]
# string = b'Hello World!'
# #s = string.encode('ASCII')
# print(strlen(string))
# =============================================================================

#Test restypes
# =============================================================================
# atol = libc.atol
# atol.argtypes = [c_char_p]
# atol.restype = c_long
# a_number = b'20000000000000000000'
# num_res = atol(a_number)
# python_num = int(a_number)
# print('Number (C): ', num_res, '\n',
#       'Number (Python):', python_num)
# =============================================================================
# =============================================================================
# atof = libc.atof
# atof.argtypes = [c_char_p]
# #atof.restype = c_double
# a_number = b'123.45'
# num = atof(a_number)
# python_res = float(a_number)
# print('Number (c):', num, '\n',
#       'Number (Python):', python_res)
# =============================================================================
# =============================================================================
# strchr = libc.strchr
# strchr.argtypes = [c_char_p, c_int]
# strchr.restype = c_char_p
# string = b'Hello, World!'
# ch = ord('o')
# print(strchr(string, ch))
# =============================================================================


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
# print(strcpy(byref(dest), string))
# =============================================================================
frexp = libc.frexp
frexp.argtypes = [c_double, POINTER(c_int)]
frexp.restype = c_double
num = 275
exp = c_int()
res = frexp(num, byref(exp))
#new = cast(exp, c_void_p).value
print('Fraction is:', res, 'Exponent is: ', exp.value)
