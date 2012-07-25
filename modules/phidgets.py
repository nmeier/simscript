''' Phidget abstraction layer '''
import logging, traceback, simscript

from Phidgets.Manager import Manager
from Phidgets import Devices
from Phidgets.PhidgetException import PhidgetException

class __PhidgetWrapper:
    def __init__(self, phidget):
        self._phidget = phidget
    def __getattribute__(self, attr):
        phidget = super().__getattribute__("_phidget")
        method = phidget.__getattribute__(attr)
        def safe(*args):
            try:
                return method(*args)
            except PhidgetException as pex:
                _log.debug("PhidgetException in %s%s: %s" % (attr,args,pex.details) )
                return None
        return safe

def _init():

    global _log, _serial2phidgets, _manager, _encoderAxisLower
        
    _log = logging.getLogger("phidgets")
    _serial2phidgets = dict()
    _encoderAxisLower = dict()

    PhidgetException.__str__ = lambda self: self.details
    
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
                phidget = simscript.classbyname(ptype)()
            except:
                _log.debug(traceback.format_exc())
                raise EnvironmentError("No specific wrapper for wrapper %s can be found" % phidget.getDeviceType)
            
            _log.info("phidgets.get(%s) # returns %s" % (device.getSerialNum(), ptype) )

            phidget = __PhidgetWrapper(phidget)
            phidget.openPhidget(serial)
            _serial2phidgets[serial] = phidget
            return phidget
        
    raise EnvironmentError("phidgets.get(%s) is not connected" % serial)

def all():
            
    if not _manager:   
        return []
   
    return [ _phidget(p.getSerialNum()) for p in _manager.getAttachedDevices()]


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

def encoder2axis(encoder, revolutions=1):
    pos = encoder.getPosition(0)
    lower = _encoderAxisLower.get(encoder, pos)
    upper = lower + int(revolutions*80)

    lower, pos, upper = _rerange(lower, pos, upper)
    
    _encoderAxisLower[encoder] = lower
    
    return (pos-lower) / (upper-lower) * 2 - 1


_init()
    
