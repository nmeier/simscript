''' Joystick abstraction layer '''

from ctypes import CDLL, Structure, byref, c_void_p, c_char_p, c_long, c_byte
import logging,traceback,os.path

class Joystick:
    
    def __init__(self, joysticks, nameOrIndex):
        
        if isinstance(nameOrIndex, int):
            if nameOrIndex < joysticks.numJoysticks():
                index = nameOrIndex
        else: 
            for j in range(0, joysticks.numJoysticks()) :
                if nameOrIndex == str(Joysticks._sdl.SDL_JoystickName(j), "utf-8"):
                    index = j

        try:    
            self.index = index;
        except:
            raise EnvironmentError("joysticks.get('%s') is not available" % nameOrIndex)

        self._handle = c_void_p()
        self.name = str(Joysticks._sdl.SDL_JoystickName(self.index), "utf-8")
        
    def _acquire(self):
        if self._handle:
            return
        self._handle = Joysticks._sdl.SDL_JoystickOpen(self.index)
        if not self._handle:
            raise EnvironmentError("joysticks.get('%s') can't be acquired" % self.index)
            
        
    def numAxis(self):
        return Joysticks._sdl.SDL_JoystickNumAxes(self._handle) if self._handle else 0

    def getAxis(self, i):
        return Joysticks._sdl.SDL_JoystickGetAxis(self._handle, i) / 32767  if self._handle else 0
    
    def numButtons(self):
        return Joysticks._sdl.SDL_JoystickNumButtons(self._handle)  if self._handle else 0
    
    def getButton(self, i):
        return Joysticks._sdl.SDL_JoystickGetButton(self._handle, i)  if self._handle else False
    
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

    class Position(Structure):
        _fields_ = [
          ("index", c_byte),
          ("wThrottle", c_long),
          ("wRudder", c_long),
          ("wAileron", c_long),
          ("wAxisX", c_long),
          ("wAxisY", c_long),
          ("wAxisZ", c_long),
          ("wAxisXRot", c_long), 
          ("wAxisYRot", c_long),
          ("wAxisZRot", c_long),
          ("wSlider", c_long),
          ("wDial", c_long),
          ("wWheel", c_long),
          ("wAxisVX", c_long),
          ("wAxisVY", c_long),
          ("wAxisVZ", c_long),
          ("wAxisVBRX", c_long), 
          ("wAxisVBRY", c_long),
          ("wAxisVBRZ", c_long),
          ("lButtons", c_long),  # 32 buttons: 0x00000001 to 0x80000000 
          ("bHats", c_long),     # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ("bHatsEx1", c_long),  # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ("bHatsEx2", c_long),  # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ("bHatsEx3", c_long)   # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ]
    

    def __init__(self, joysticks, joystick, virtualIndex):
        self.index = joystick.index
        self.name = joystick.name
        
        self._position = VirtualJoystick.Position()
        self._position.index = virtualIndex+1
        
        self._acquired = False

        self._buttons = Joysticks._vjoy.GetVJDButtonNumber(self._position.index)
        
        self._axis = []
        for akey, pkey in VirtualJoystick._AXIS_KEYS:
            if Joysticks._vjoy.GetVJDAxisExist(self._position.index, akey):
                amax = c_long()
                amin = c_long()
                Joysticks._vjoy.GetVJDAxisMin(self._position.index, akey, byref(amin))
                Joysticks._vjoy.GetVJDAxisMax(self._position.index, akey, byref(amax))
                self._axis.append((pkey, amin.value,amax.value))
                self._position.__setattr__(pkey, int(amin.value + (amax.value-amin.value)/2)) 
                
    def _acquire(self):
        if self._acquired:
            return
        if not Joysticks._vjoy.AcquireVJD(self._position.index):
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
            raise EnvironmentError("joysticks.get('%s') doesn't have axis %d" % a)
        if value < -1 or value > 1:
            raise EnvironmentError("joysticks.get('%s') value for axis %d not -1.0 < %d < 1.0" % (self.index, a, value))
        pkey, amin, amax = self._axis[a]
        self._position.__setattr__(pkey, int( (value+1)/2 * (amax-amin) + amin))
    
    def numButtons(self):
        return self._buttons
    
    def getButton(self, i):
        if i<0 or i>=self._buttons:
            raise EnvironmentError("joysticks.get('%s') doesn't have button  %d" % i)
        return self._position.lButtons & (1<<i)
    
    def setButton(self, i, value):
        if i<0 or i>=self._buttons:
            raise EnvironmentError("joysticks.get('%s') doesn't have button  %d" % i)
        if value:
            self._position.lButtons |= 1<<i
        else:
            self._position.lButtons &= ~(1<<i)
        
    def _sync(self):
        if not Joysticks._vjoy.UpdateVJD(self._position.index, byref(self._position)):
            Joysticks._log.warning("joysticks.get('%s') couldn't be set" % self.name)
    
    def __str__(self):
        return "joysticks.get('%s') # VirtualJoystick index %d" % (self.name, self.index)
    
    
class Joysticks: 

    _log = logging.getLogger(__name__)
    _sdl = None
    _vjoy = None
            
    def __init__(self):
        
        self._joysticks = []
        
        # preload all available joysticks for reporting
        if not Joysticks._sdl: 
            try:
                Joysticks._sdl = CDLL(os.path.join("contrib","sdl","SDL.dll"))
                Joysticks._sdl.SDL_Init(0x200)
                Joysticks._sdl.SDL_JoystickName.restype = c_char_p
                for index in range(0, Joysticks._sdl.SDL_NumJoysticks()) :
                    joy = Joystick(self, index)
                    self._joysticks.append(joy)
            except Exception:
                Joysticks._log.warning("Cannot initialize support for physical Joysticks")
                Joysticks._log.warning(traceback.format_exc())

        # wrap virtual joysticks where applicable                
        if not Joysticks._vjoy: 
            try:
                Joysticks._vjoy = CDLL(os.path.join("contrib", "vjoy", "vJoyInterface.dll"))
                
                if not Joysticks._vjoy.vJoyEnabled():
                    Joysticks._log.info("No Virtual Joystick Driver active")
                    return

                numVirtuals = 0
                                
                for i,joy in enumerate(self._joysticks):
                    if joy.name == VirtualJoystick._DEVICE_NAME:
                        try:
                            virtual = VirtualJoystick(self, joy, numVirtuals)
                            self._joysticks[i] = virtual
                        except:
                            Joysticks._log.warning("Cannot initialize support for virtual Joystick %s" % joy.name)
                            Joysticks._log.warning(traceback.format_exc())
                        numVirtuals += 1
                    
            except Exception:
                Joysticks._log.warning("Cannot initialize support for virtual Joysticks")
                Joysticks._log.warning(traceback.format_exc())

        # build dictionary
        self._dict = dict()
        for joy in self._joysticks:
            self._dict[joy.name] = joy 
            self._dict[joy.index] = joy 
            Joysticks._log.info(joy)

                
    def numJoysticks(self):
        return max(Joysticks._sdl.SDL_NumJoysticks(), len(self._joysticks))
    
    def get(self,nameOrIndex):
        try:
            joy = self._dict[nameOrIndex]
        except:
            joy = Joystick(self, nameOrIndex)
            self._joysticks.append(joy)
            self._dict[joy.index] = joy
            self._dict[joy.name] = joy 
        joy._acquire()
        return joy
    
    
    def button(self, nameOrIndexAndButton):
        """ test button eg button 1 of Saitek Pro Flight Quadrant via button('Saitek Pro Flight Quadrant.1') """
        nameOrIndex, button = nameOrIndexAndButton.split(".")
        return self.get(nameOrIndex).button(int(button))
        
    def poll(self):
        if Joysticks._sdl:
            Joysticks._sdl.SDL_JoystickUpdate()
        for joy in self._joysticks:
            joy._sync()
    
def init():
    return Joysticks()
