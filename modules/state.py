import time

''' script state  '''
def get(key,default=None):
    try:
        return __dict[key]
    except KeyError:
        return default

def set(key,val): #@ReservedAssignment
    """ store value for given key and return last known value (None, if not known, False, if not known and val is True or False) """
    try:
        old =  __dict[key]
    except KeyError:
        old = False if val==True or val==False else None
    __dict[key] = val
    return old

def lock(key, refresh, ttl):
    
    if refresh:
        was = key in __dict
        __dict[key] = time.clock()+ttl
        return True if not was else None

    try:
        expired = __dict[key] < time.clock()
        
        if not expired: return None
        
        del __dict[key]
        
        return False
    
    except KeyError:
        return None


'''
        N T F
      N N T N
      F N T N
      T N N F
'''
def toggle(key, now, hold=None):
    was = get(key) 
    if not was and now: 
        if hold: 
            if not __holds.get(key, None):
                __holds[key] = time.clock()
            if time.clock() - __holds[key] < hold:
                return False
        set(key, True)
        return True
    
    if hold and key in __holds:
        del __holds[key]
    
    if was and not now:
        set(key, False) 
        return False
    
    return None

def remove(key):
    del __dict[key]

def inc(key, increment=1):
    val = get(key, 0)
    val += increment
    set(key,val)
    return val

def _init():
    global __dict, __holds
    __dict = dict()
    __holds = dict()

def sync():
    pass

_init()


