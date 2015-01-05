import inspect
import pdb

def triggerable(func):
    pdb.set_trace()
    print('hi')
    return func



@triggerable
def test():
    print("test called")
