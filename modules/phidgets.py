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
                __log.debug("PhidgetException in %s%s: %s" % (attr,args,pex.details) )
                return None
        return safe

def init():

    global __log, __serial2phidgets, __manager
        
    __log = logging.getLogger("phidgets")
    __serial2phidgets = dict()
    
    PhidgetException.__str__ = lambda self: self.details
    
    try:
        __manager = Manager()
        __manager.openManager()
    except Exception as e:
        __manager = None
        __log.warning("Cannot initialize support for Phidgets (%s)", e)
        __log.debug(traceback.format_exc())
        
    all()

def num():
    return len(__manager.getAttachedDevices()) if __manager else 0

def _phidget(serial):

    try:
        return __serial2phidgets[serial]
    except KeyError:
        pass

    if not __manager:   
        raise EnvironmentError("phidgets not initialized")
    
    for device in __manager.getAttachedDevices():
        if device.getSerialNum() == serial:
            try:
                ptype = "Phidgets.Devices."+Devices.__all__[device.getDeviceClass()]+"."+Devices.__all__[device.getDeviceClass()]
                __log.debug("Trying class %s for #%s" % (ptype, device.getSerialNum()))
                phidget = simscript.classbyname(ptype)()
            except:
                __log.debug(traceback.format_exc())
                raise EnvironmentError("No specific wrapper for wrapper %s can be found" % phidget.getDeviceType)
            
            __log.info("phidgets.get(%s) # returns %s" % (device.getSerialNum(), ptype) )

            phidget = __PhidgetWrapper(phidget)
            phidget.openPhidget(serial)
            __serial2phidgets[serial] = phidget
            return phidget
        
    raise EnvironmentError("phidgets.get(%s) is not connected" % serial)

def all():
            
    if not __manager:   
        return []
   
    return [ _phidget(p.getSerialNum()) for p in __manager.getAttachedDevices()]


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

init()
    
