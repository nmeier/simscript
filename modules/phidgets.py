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

    global _log, _serial2phidgets, _manager, _encoderHistory, _lastPollDevices

        
    _log = logging.getLogger("phidgets")
    _serial2phidgets = dict()
    _encoderHistory = dict()
    _lastPollDevices = 0

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
    pass

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

''' translates a boundless encoder position to an axis for given number of revolutions '''
def encoder2axis(encoder, revolutions=1):
    pos = encoder.getPosition(0)
    lower = _encoderHistory.get( (encoder,"axis_start") , pos)
    upper = lower + int(revolutions*_ENCODER_TICKS_PER_REVOLUTION)

    lower, pos, upper = _rerange(lower, pos, upper)
    
    _encoderHistory[ (encoder,"axis_start") ] = lower
    
    return (pos-lower) / float(upper-lower) * 2 - 1

''' translates a boundless encoder positions to increments per revolution '''
def encoder2delta(encoder, ticks=8):
    
    key = (encoder,"current_tick")
    
    # pos has to move to one of the 'click' areas
    pos = int(encoder.getPosition(0) / (_ENCODER_TICKS_PER_REVOLUTION/ticks/2) )
    
    if pos&1:
        return 0
    pos >>= 1
    # calculate delta to current position
    delta = _encoderHistory.get(key, pos) - pos
    _encoderHistory[key] = pos
    return delta

_init()
    
