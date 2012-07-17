'''
Created on 2011-03-13

@author: netbook
'''
def classbyname(name):
    parts = name.split('.')
    m = __import__(".".join(parts[:-1]))
    for p in parts[1:]:
        m = getattr(m, p)            
    return m

def identity(x):
    return x

def modulo(value,range):
    if value!=value: #NaN check
        return value
    start,end = range
    value = (value - start) % (end-start)
    value = start+value if value>=0 else end+value
    return value