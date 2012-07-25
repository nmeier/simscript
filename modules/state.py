''' script state  '''
def get(key,default=None):
    try:
        return __dict[key]
    except KeyError:
        return default

def set(key,val):
    try:
        old =  __dict[key]
    except KeyError:
        old = val
    __dict[key] = val
    return old

def inc(key):
    val = get(key, 0)
    val += 1
    set(key,val)
    return val

def _init():
    global __dict
    __dict = dict()

def sync():
    pass

_init()


