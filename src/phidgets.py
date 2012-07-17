''' Phidget abstraction layer '''
import logging, traceback, util

from Phidgets.Manager import Manager
from Phidgets import Devices
from Phidgets.PhidgetException import PhidgetException

class Phidgets():
    
    _log = logging.getLogger("phidgets")
    
    class Wrapper:
        def __init__(self, phidget):
            self._phidget = phidget
        def __getattribute__(self, attr):
            phidget = super().__getattribute__("_phidget")
            method = phidget.__getattribute__(attr)
            def safe(*args):
                try:
                    return method(*args)
                except PhidgetException as pex:
                    Phidgets._log.debug("PhidgetException in %s%s: %s" % (attr,args,pex.details) )
                    return None
            return safe

    def __init__(self):
        
        self._serial2phidgets = dict()
        
        try:
            self._manager = Manager()
            self._manager.openManager()
        except:
            self._manager = None
            Phidgets._log.warning("No type integration available")
            Phidgets._log.debug(traceback.format_exc())
            
        self.all()
    
    def num(self):
        return len(self._manager.getAttachedDevices()) if self._manager else 0
    
    def _phidget(self, serial):

        try:
            return self._serial2phidgets[serial]
        except KeyError:
            pass

        if not self._manager:   
            raise EnvironmentError("phidgets not initialized")
        
        for device in self._manager.getAttachedDevices():
            if device.getSerialNum() == serial:
                try:
                    ptype = "Phidgets.Devices."+Devices.__all__[device.getDeviceClass()]+"."+Devices.__all__[device.getDeviceClass()]
                    Phidgets._log.debug("Trying class %s for #%s" % (ptype, device.getSerialNum()))
                    phidget = util.classbyname(ptype)()
                except:
                    Phidgets._log.debug(traceback.format_exc())
                    raise EnvironmentError("No specific wrapper for wrapper %s can be found" % phidget.getDeviceType)
                
                Phidgets._log.info("phidgets.get(%s) # returns %s" % (device.getSerialNum(), ptype) )

                phidget = Phidgets.Wrapper(phidget)
                phidget.openPhidget(serial)
                self._serial2phidgets[serial] = phidget
                return phidget
            
        raise EnvironmentError("phidgets.get(%s) is not connected" % serial)
    
    def all(self):
                
        if not self._manager:   
            raise EnvironmentError("phidgets not initialized")
        
        return [ self._phidget(p.getSerialNum()) for p in self._manager.getAttachedDevices()]
    
    
    def get(self, serial):

        phidget = self._phidget(serial)

        if not phidget.isAttached():        
            phidget.waitForAttach(1000)
            if not phidget.isAttached():        
                raise EnvironmentError("phidgets.get(%s) is not ready for use" % serial)
                
        return phidget
    
    def str(self, phidget):
        return "%s #%s" % (phidget.getDeviceName(), phidget.getSerialNum())
    