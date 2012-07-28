''' script state  '''
def get(key,default=None):
    try:
        return __dict[key]
    except KeyError:
        return default

def set(key,val): #@ReservedAssignment
    try:
        old =  __dict[key]
    except KeyError:
        old = val
    __dict[key] = val
    return old

'''
        N T F
      N N T N
      F N T N
      T N N F
'''
def toggle(key, change):
    old = set(key, change)
    if not old and change: return True
    if old and not change: return False
    return None

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


