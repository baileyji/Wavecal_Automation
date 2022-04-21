from enum import IntEnum
from ctypes import *
import unittest

    
class NewClass():
    def __init__(self):
        print(cdll.msvcrt)
        self.libc = cdll.msvcrt
    
    def Newfunc(self, string):
        """
        Changes a string to an integer

        """
        libc = self.libc
        atoi = libc.atoi
        string = string.encode('ASCII')
        atoi.argtypes = [c_char_p]
        atoi.restype = c_int
        num = atoi(string)
        return num

    
    def OtherFunc(self, string):
        """
        Uses strchr on a string of user's choice

        """
        libc = self.libc
        strchr = libc.strchr
        strchr.argtypes = [c_char_p, c_int]
        strchr.restype = c_char_p
        ch = ord('o')
        new_string = strchr(string, ch)
        new_chr = ord('r')
        newnew = strchr(new_string, new_chr)
        return new_string, newnew
    
    
    def Errors(self):
        raise ValueError('False!')

class Test(unittest.TestCase):
        
    def setUp(self):
        """
        Create class instance

        """
        print('Starting up!')
        self.someClass = NewClass()


    def tearDown(self):
        print('Closing!')
        
        
    def testNewFunc(self):
        """
        Tests that New func returns the correct integer
        
        """
        string='93563'
        num = self.someClass.Newfunc(string)
        self.assertEqual(num, 93563)
        
    
    def testOtherFunc(self):
        """
        Tests that strchr works correctly.

        """
        string = b'Duck Duck Goose'
        stringOne, stringTwo = self.someClass.OtherFunc(string)
        self.assertEqual(stringOne, b'oose')
        self.assertFalse(stringTwo)
        
    
    def testErrors(self):
        """
        Tests that errors are recorded correctly.
        
        """
        with self.assertRaises(ValueError) as context:
            self.someClass.Errors()
        self.assertEqual(str(context.exception), 'False!')
    
    
if __name__ == '__main__':
    unittest.main()        