''' Joystick abstraction layer '''

from ctypes import CDLL, Structure, c_byte, c_void_p, c_char_p, c_long
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
            raise EnvironmentError("joysticks.get('%s') is n/a" % nameOrIndex)

        self._handle = c_void_p()
        self.name = "Disconnected"

        if Joysticks._sdl and index>=0 and index<Joysticks._sdl.SDL_NumJoysticks():
            self._handle = Joysticks._sdl.SDL_JoystickOpen(self.index)
            self.name = str(Joysticks._sdl.SDL_JoystickName(self.index), "utf-8")
        
    def numAxis(self):
        return Joysticks._sdl.SDL_JoystickNumAxes(self._handle) if self._handle else 0

    def getAxis(self, i):
        return Joysticks._sdl.SDL_JoystickGetAxis(self._handle, i) / 32767  if self._handle else 0
    
    def numButtons(self):
        return Joysticks._sdl.SDL_JoystickNumButtons(self._handle)  if self._handle else 0
    
    def getButton(self, i):
        return Joysticks._sdl.SDL_JoystickGetButton(self._handle, i)  if self._handle else False
    
    def __str__(self):
        return "joysticks.get('%s') # index %d (%d axis, %d buttons)" % (self.name, self.index, self.numAxis(), self.numButtons())
    

class VirtualJoystick:

    _VJD_STAT_OWN  = 0 # Device is owned by this application.
    _VJD_STAT_FREE = 1 # Device is NOT owned by any application (including this one).
    _VJD_STAT_BUSY = 2 # Device is owned by another application. It cannot be acquired by this application.
    _VJD_STAT_MISS = 3 # Device is missing. It either does not exist or the driver is down.
    _VJD_STAT_UNKN = 4 # Unknown

    _HID_USAGE_X  = 0x30
    _HID_USAGE_Y  = 0x31
    _HID_USAGE_Z  = 0x32
    _HID_USAGE_RX  = 0x33
    _HID_USAGE_RY  = 0x34
    _HID_USAGE_RZ  = 0x35
    _HID_USAGE_SL0 = 0x36
    _HID_USAGE_SL1 = 0x37
    _HID_USAGE_WHL = 0x38
    _HID_USAGE_POV = 0x39
    
    _usableAxis = [_HID_USAGE_X, _HID_USAGE_Y, _HID_USAGE_Z, _HID_USAGE_RX, _HID_USAGE_RY, _HID_USAGE_RZ, _HID_USAGE_SL0, _HID_USAGE_SL1, _HID_USAGE_WHL]
    
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
          ("bHats", c_long)     # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
          ]

    def __init__(self, joysticks, index):
        self._index = index
        self._buttons = 0
        self._axis = []

        if Joysticks._vjoy.GetVJDStatus(index+1) != VirtualJoystick._VJD_STAT_FREE:
            raise EnvironmentError("joysticks.virtual('%s') is not free" % index)
        
        self._buttons = Joysticks._vjoy.GetVJDButtonNumber(index+1)
        self._axis = []
        
        for a in VirtualJoystick._usableAxis:
            if Joysticks._vjoy.GetVJDAxisExist(index+1, a):
                self._axis.append(a) 
                
    def __str__(self):
        return "joysticks.virtual(%d) # VirtualJoystick (%d buttons, %d axis)" % (self._index, self._buttons, len(self._axis))
    
    
class Joysticks: 

    _log = logging.getLogger(__name__)
    _sdl = None
    _vjoy = None
            
    def __init__(self):
        
        self._sticks = dict()
        self._virtuals = dict()
        
        if not Joysticks._sdl: 
            try:
                Joysticks._sdl = CDLL(os.path.join("contrib","sdl","SDL.dll"))
                Joysticks._sdl.SDL_Init(0x200)
                Joysticks._sdl.SDL_JoystickName.restype = c_char_p
                for j in range(0, Joysticks._sdl.SDL_NumJoysticks()) :
                    Joysticks._log.info(self.get(j))
            except Exception:
                Joysticks._log.warning("Cannot initialize support for physical Joysticks")
                Joysticks._log.debug(traceback.format_exc())
                
        if not Joysticks._vjoy: 
            try:
                Joysticks._vjoy = CDLL(os.path.join("contrib", "vjoy", "vJoyInterface.dll"))
                
                if not Joysticks._vjoy.vJoyEnabled():
                    Joysticks._log.info("No Virtual Joystick Driver active")
                    return
                for i in range(0,16):
                    try:
                        Joysticks._log.info(self.virtual(i))
                    except:
                        pass
                    
            except Exception:
                Joysticks._log.warning("Cannot initialize support for virtual Joysticks")
                Joysticks._log.warning(traceback.format_exc())
                
    def numJoysticks(self):
        return Joysticks._sdl.SDL_NumJoysticks() if Joysticks._sdl else 0
    
    def get(self,nameOrIndex):
        try:
            joy = self._sticks[nameOrIndex]
        except:
            joy = self._sticks[nameOrIndex] = Joystick(self, nameOrIndex)
        return joy
    
    def virtual(self,index):
        
        try:
            joy = self._virtuals[index]
        except:
            joy = self._virtuals[index] = VirtualJoystick(self, index)
        return joy
    
    def button(self, nameOrIndexAndButton):
        """ test button eg button 1 of Saitek Pro Flight Quadrant via button('Saitek Pro Flight Quadrant.1') """
        nameOrIndex, button = nameOrIndexAndButton.split(".")
        return self.get(nameOrIndex).button(int(button))
        
    def poll(self):
        if not Joysticks._sdl:
            return
        # poll
        Joysticks._sdl.SDL_JoystickUpdate()
    
def init():
    return Joysticks()
