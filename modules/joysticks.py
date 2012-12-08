import logging,traceback,os,platform,ctypes

''' Joystick abstraction layer '''

HAT_N = 1
HAT_E = 2
HAT_S = 4
HAT_W = 8
HAT_NE = HAT_N | HAT_E
HAT_SE = HAT_S | HAT_E
HAT_SW = HAT_S | HAT_W
HAT_NW = HAT_N | HAT_W

class Joystick:
    
    MAX_AXIS = 16
    
    def __init__(self, nameOrIndex):
        
        self._axishistory = []
        for i in range(Joystick.MAX_AXIS):
            self._axishistory.append([]) 
       
        if isinstance(nameOrIndex, int):
            if nameOrIndex < numJoysticks():
                index = nameOrIndex
        else: 
            for j in range(0, numJoysticks()) :
                if nameOrIndex == _joysticks[j].name:
                    index = j

        try:    
            self.index = index;
        except:
            raise EnvironmentError("joysticks.get('%s') is not available" % nameOrIndex)

        self._handle = ctypes.c_void_p()
        # see http://nedbatchelder.com/text/unipain.html on Python 2/3 differences on unicode handling re decode()
        self.name = _sdl.SDL_JoystickName(self.index).decode().strip()
        
    def _acquire(self):
        if self._handle:
            return
        self._handle = _sdl.SDL_JoystickOpen(self.index)
        if not self._handle:
            raise EnvironmentError("joysticks.get('%s') can't be acquired" % self.index)
            
        
    def numAxis(self):
        return _sdl.SDL_JoystickNumAxes(self._handle)

    def getHat(self, i):
        return _sdl.SDL_JoystickGetHat(self._handle, 0)

    def getAxis(self, i, deadzone=0.01, smoothing=1):
        
        assert i<Joystick.MAX_AXIS
        
        val = _sdl.SDL_JoystickGetAxis(self._handle, i) / float(32767)
        
        deadzone = abs(deadzone)
        if val < -1+deadzone:
            val = -1
        if val > 1-deadzone:
            val =  1
            
        assert not smoothing<1
        
        history = self._axishistory[i]             
        if len(history)>=smoothing:
            del history[0:len(history)-smoothing]

        if smoothing==1:
            return val;

        history.append(val)
        
        return sum(history)/len(history)
    
    def setAxis(self, a, value):
        raise EnvironmentError("%s is not a virtual voystick" % self.name)
    
    def numButtons(self):
        return _sdl.SDL_JoystickNumButtons(self._handle)  
    
    def getButton(self, i):
        # no idea why but if I don't touch the logging subsystem here then Python 2.7 simply bails without exit hooks
        _log.isEnabledFor(_log.debug)
        return _sdl.SDL_JoystickGetButton(self._handle, i)
    
    def setButton(self, b, value):
        raise EnvironmentError("%s is not a virtual voystick" % self.name)
    
    def _sync(self):
        pass
    
    def __str__(self):
        # button/axis information isn't available before acquired
        return "joysticks.get('%s') # index %d" % (self.name, self.index)
    

class VirtualJoystick:
    
    _DEVICE_NAME = 'vJoy Device'

    _AXIS_KEYS = [
        (0x30, "wAxisX"), 
        (0x31, "wAxisY"), 
        (0x32, "wAxisZ"),
        (0x33, "wAxisXRot"),
        (0x34, "wAxisYRot"),
        (0x35, "wAxisZRot"),
        (0x36, "wSlider"),
        (0x37, "wDial"),
        (0x38, "wWheel")
        ]

    class Position(ctypes.Structure):
        _fields_ = [
          ("index", ctypes.c_byte),
          ("wThrottle", ctypes.c_long),
          ("wRudder", ctypes.c_long),
          ("wAileron", ctypes.c_long),
          ("wAxisX", ctypes.c_long),
          ("wAxisY", ctypes.c_long),
          ("wAxisZ", ctypes.c_long),
          ("wAxisXRot", ctypes.c_long), 
          ("wAxisYRot", ctypes.c_long),
          ("wAxisZRot", ctypes.c_long),
          ("wSlider", ctypes.c_long),
          ("wDial", ctypes.c_long),
          ("wWheel", ctypes.c_long),
          ("wAxisVX", ctypes.c_long),
          ("wAxisVY", ctypes.c_long),
          ("wAxisVZ", ctypes.c_long),
          ("wAxisVBRX", ctypes.c_long), 
          ("wAxisVBRY", ctypes.c_long),
          ("wAxisVBRZ", ctypes.c_long),
          ("lButtons", ctypes.c_long),  # 32 buttons: 0x00000001 to 0x80000000 
          ("bHats", ctypes.c_long),     # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ("bHatsEx1", ctypes.c_long),  # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ("bHatsEx2", ctypes.c_long),  # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ("bHatsEx3", ctypes.c_long)   # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ]
    

    def __init__(self, joystick, virtualIndex):
        self.index = joystick.index
        self.name = joystick.name
        
        self._position = VirtualJoystick.Position()
        self._position.index = virtualIndex+1
        
        self._acquired = False
        self._dirty = False

        self._buttons = _vjoy.GetVJDButtonNumber(self._position.index)
        
        self._axis = []
        for akey, pkey in VirtualJoystick._AXIS_KEYS:
            if _vjoy.GetVJDAxisExist(self._position.index, akey):
                amax = ctypes.c_long()
                amin = ctypes.c_long()
                _vjoy.GetVJDAxisMin(self._position.index, akey, ctypes.byref(amin))
                _vjoy.GetVJDAxisMax(self._position.index, akey, ctypes.byref(amax))
                self._axis.append((pkey, amin.value,amax.value))
                self._position.__setattr__(pkey, int(amin.value + (amax.value-amin.value)/2)) 
                
    def _acquire(self):
        if self._acquired:
            return
        if not _vjoy.AcquireVJD(self._position.index):
            raise EnvironmentError("joysticks.get('%s') is not a free Virtual Joystick" % self.index)
        self._acquired = True
                
    def numAxis(self):
        return len(self._axis)

    def getAxis(self, i):
        if i<0 or i>=len(self._axis):
            raise EnvironmentError("joysticks.get('%s') doesn't have axis %d" % i)
        pkey, amin, amax = self._axis[i] 
        return (self._position.__getattribute__(pkey) - amin) / (amax-amin) * 2 - 1
    
    def setAxis(self, a, value):
        if a<0 or a>=len(self._axis):
            raise EnvironmentError("joysticks.get('%s') doesn't have axis %d" % (self.index, a))
        if value < -1 or value > 1:
            raise EnvironmentError("joysticks.get('%s') value for axis %d not -1.0 < %d < 1.0" % (self.index, a, value))
        pkey, amin, amax = self._axis[a]
        self._position.__setattr__(pkey, int( (value+1)/2 * (amax-amin) + amin))
        self._dirty = True
    
    def numButtons(self):
        return self._buttons
    
    def getButton(self, i):
        if i<0 or i>=self._buttons:
            raise EnvironmentError("joysticks.get('%s') doesn't have button  %d" % (self.name, i))
        return self._position.lButtons & (1<<i)
    
    def setButton(self, i, value):
        if i<0 or i>=self._buttons:
            raise EnvironmentError("joysticks.get('%s') doesn't have button  %d" % (self.name, i))
        if value:
            self._position.lButtons |= 1<<i
        else:
            self._position.lButtons &= ~(1<<i)
        self._dirty = True
        
    def _sync(self):
        if not self._dirty:
            return
        if not self._acquired:
            return
        if not _vjoy.UpdateVJD(self._position.index, ctypes.byref(self._position)):
            _log.warning("joysticks.get('%s') couldn't be set" % self.name)
            self._acquired = False
        self._dirty = False
        
    def __str__(self):
        return "joysticks.get('%s') # VirtualJoystick index %d" % (self.name, self.index)
     
def numJoysticks():
    if not _sdl:
        return 0
    return max(_sdl.SDL_NumJoysticks(), len(_joysticks))

def get(nameOrIndex):
    try:
        joy = _name2joystick[nameOrIndex if isinstance(nameOrIndex,int) else nameOrIndex.lower()]
    except:
        raise EnvironmentError("No joystick %s" % nameOrIndex)
    joy._acquire()
    return joy


def button(nameOrIndexAndButton):
    """ test button eg button 1 of Saitek Pro Flight Quadrant via button('Saitek Pro Flight Quadrant.1') """
    nameOrIndex, button = nameOrIndexAndButton.split(".")
    return get(nameOrIndex).button(int(button))
    
def sync():
    if _sdl:
        _sdl.SDL_JoystickUpdate()
    for joy in _joysticks:
        joy._sync()
    
def _init():    
    global _sdl, _vjoy, _log, _joysticks, _name2joystick
    
    _sdl = None
    _vjoy = None
    _log = logging.getLogger(__name__)
    _joysticks = []
    _name2joystick = dict()
   
    # preload all available joysticks for reporting
    if not _sdl: 
        try:
            _sdl = ctypes.CDLL(os.path.join("contrib","sdl",platform.architecture()[0],"SDL.dll"))
            _sdl.SDL_Init(0x200)
            _sdl.SDL_JoystickName.restype = ctypes.c_char_p
            _sdl.SDL_JoystickGetAxis.restype = ctypes.c_int16
            for index in range(0, _sdl.SDL_NumJoysticks()) :
                joy = Joystick(index)
                _joysticks.append(joy)
        except Exception as e:
            _log.warning("Cannot initialize support for physical Joysticks (%s)" % e)
            _log.debug(traceback.format_exc())
    
    # wrap virtual joysticks where applicable                
    if not _vjoy: 
        try:
            _vjoy = ctypes.CDLL(os.path.join("contrib", "vjoy", platform.architecture()[0], "vJoyInterface.dll"))
            if not _vjoy.vJoyEnabled():
                _log.info("No Virtual Joystick Driver active")
            else:
                numVirtuals = 0
                for i,joy in enumerate(_joysticks):
                    if joy.name == VirtualJoystick._DEVICE_NAME:
                        try:
                            virtual = VirtualJoystick(joy, numVirtuals)
                            _joysticks[i] = virtual
                        except Exception as e:
                            _log.warning("Cannot initialize support for virtual Joystick %s (%s)" % (joy.name, e))
                            _log.debug(traceback.format_exc())
                        numVirtuals += 1
                
        except Exception as e:
            _log.warning("Cannot initialize support for virtual Joysticks (%s)" % e)
            _log.debug(traceback.format_exc())
    
    # build dictionary
    for joy in _joysticks:
        _name2joystick[joy.name.lower()] = joy 
        _name2joystick[joy.index] = joy 
        _log.info(joy)
    

_init()