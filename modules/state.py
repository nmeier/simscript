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

def touch(key, duration):
    """ touch a variable for given duration 
    
    key - key to use
    duration - duration of new value
    
    returns True if newly touched, False if duration==0 and expired, None if without change
    
    """ 
    
    if duration>0:
        was = key in __dict
        __dict[key] = time.clock()+duration
        if not was:
            return True
    else:
        try:
            expired = __dict[key] < time.clock()
            if expired: 
                del __dict[key]
                return False
        except KeyError:
            pass
    
    # no change
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


