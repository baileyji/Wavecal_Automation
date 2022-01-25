from ctypes_practice import NewClass
from ctypes_practice import PE_STATUS

def troubleshoot(string):
    print('Starting!')
    thing = NewClass()
    num = thing.Newfunc(string)
    print(num)
    
troubleshoot(b'3')
