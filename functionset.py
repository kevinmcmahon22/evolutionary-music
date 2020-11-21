
# imported as func in gp.py
import_shortcut = 'func'



def getTerminalSet():
    return [1, 2]


# Functions all have arity of 2, can be either list or int

def getFunctionSet():
    return [(add_on, 2)]



def add_on(x, y):
    return x*y