''' Phidget abstraction layer '''
import logging, traceback, time

from Phidgets.Manager import Manager
from Phidgets import Devices
from Phidgets.PhidgetException import PhidgetException

_ENCODER_TICKS_PER_REVOLUTION = 80

class __PhidgetWrapper:
    def __init__(self, phidget):
        self._phidget = phidget
    def __getattr__(self, attr):
        phidget = getattr(self, "_phidget")
        method = getattr(phidget, attr)
        def safe(*args):
            try:
                return method(*args)
            except PhidgetException as pex:
                _log.debug("PhidgetException in %s%s: %s" % (attr,args,pex.details) )
                return None
        return safe

def _init():

    global _log, _serial2phidgets, _manager, _encoderHistory, _encoderAsAxis, _lastPollDevices, _sync

    _log = logging.getLogger("phidgets")
    _serial2phidgets = dict()
    _encoderHistory = dict()
    _encoderAsAxis = dict()
    _lastPollDevices = 0
    _sync = 0

    try:
        _manager = Manager()
        _manager.openManager()
    except Exception as e:
        _manager = None
        _log.warning("Cannot initialize support for Phidgets (%s)", e)
        _log.debug(traceback.format_exc())
        
    all()

def num():
    return len(_manager.getAttachedDevices()) if _manager else 0

def _phidget(serial):

    try:
        return _serial2phidgets[serial]
    except KeyError:
        pass

    if not _manager:   
        raise EnvironmentError("phidgets not initialized")
    
    for device in _manager.getAttachedDevices():
        if device.getSerialNum() == serial:
            try:
                ptype = "Phidgets.Devices."+Devices.__all__[device.getDeviceClass()]+"."+Devices.__all__[device.getDeviceClass()]
                _log.debug("Trying class %s for #%s" % (ptype, device.getSerialNum()))
                phidget = _classbyname(ptype)()
            except:
                _log.debug(traceback.format_exc())
                raise EnvironmentError("No specific wrapper for wrapper %s can be found" % phidget.getDeviceType)
            
            _log.info("phidgets.get(%s) # returns %s" % (device.getSerialNum(), ptype) )

            phidget = __PhidgetWrapper(phidget)
            phidget.openPhidget(serial)
            _serial2phidgets[serial] = phidget
            return phidget
        
    raise EnvironmentError("phidgets.get(%s) is not connected" % serial)

def _classbyname(name):
    parts = name.split('.')
    m = __import__(".".join(parts[:-1]))
    for p in parts[1:]:
        m = getattr(m, p)            
    return m

def all(): #@ReservedAssignment
    
    global _lastPollDevices
    if time.clock() - _lastPollDevices > 3:
        if _manager:   
            for p in _manager.getAttachedDevices():
                _phidget(p.getSerialNum()) 
            
        _lastPollDevices = time.clock()

    return _serial2phidgets.values()
            

def get(serial):

    phidget = _phidget(serial)

    if not phidget.isAttached():        
        phidget.waitForAttach(1000)
        if not phidget.isAttached():        
            raise EnvironmentError("phidgets.get(%s) is not ready for use" % serial)
            
    return phidget

def flatten(phidget):
    return "%s #%s" % (phidget.getDeviceName(), phidget.getSerialNum())

def sync():

    global _sync
    
    # look for unwatched encoder axis that need to be re-aligned b/o rotated encoder
    for ((encoder,key), (sync, datum, old)) in _encoderAsAxis.items():
        if sync == _sync:
            continue
        new = encoder.getPosition(0)
        if new == old:
            continue
        _encoderAsAxis[(encoder,key)] = (_sync+1, datum+new-old, new)

    # next sync    
    _sync += 1
    

'''
   returns an axis value -1<=v<=1 for a given encoder
'''
def getAxis(encoder, key=None, revolutions=1, default=0):
    
    pos = encoder.getPosition(0)
    
    key = (encoder, key)
    
    range = revolutions*_ENCODER_TICKS_PER_REVOLUTION
    
    if not key in _encoderAsAxis:
        value = default
        datum = pos + int( float(range)/2 * default)
    else:
        _,datum,_ = _encoderAsAxis.get(key)
        datum, pos, _ = _rerange(datum, pos, datum + int(range))
        value = (pos-datum) / float(range) * 2 - 1

    _encoderAsAxis[key] = (_sync, datum, pos)
    
    return value

''' 
    l<v<u returns l<v<u
    l<u<v returns l<v=u
    v<l<u returns l=v<u
'''
def _rerange(lower, value, upper):
    if value>upper:
        return value-(upper-lower), value, value
    elif value<lower:
        return value, value, value+(upper-lower)
    return lower, value, upper

''' translates a boundless encoder positions to increments per revolution '''
def getDelta(encoder, ticks=8):
    # pos has to move to one of the 'click' areas
    pos = int(encoder.getPosition(0) / (_ENCODER_TICKS_PER_REVOLUTION/ticks/2) )
    if pos&1:
        return 0
    pos >>= 1
    # calculate delta to current position
    delta = _encoderHistory.get(encoder, pos) - pos
    _encoderHistory[encoder] = pos
    return delta

_init()
    
