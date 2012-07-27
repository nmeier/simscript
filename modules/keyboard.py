import ctypes

VK_LBUTTON      = 0x1
VK_RBUTTON      = 0x2
VK_CANCEL      = 0x3
VK_MBUTTON      = 0x4
VK_BACK      = 0x8
VK_TAB      = 0x9
VK_CLEAR      = 0x0C 
VK_RETURN      = 0x0D 
VK_SHIFT      = 0x10
VK_CONTROL      = 0x11
VK_MENU      = 0x12
VK_PAUSE      = 0x13
VK_CAPITAL      = 0x14
VK_ESCAPE      = 0x1B 
VK_SPACE      = 0x20
VK_PRIOR      = 0x21
VK_NEXT      = 0x22
VK_END      = 0x23
VK_HOME      = 0x24
VK_LEFT      = 0x25
VK_UP      = 0x26
VK_RIGHT      = 0x27
VK_DOWN      = 0x28
VK_SELECT      = 0x29
VK_PRINT      = 0x2A 
VK_EXECUTE      = 0x2B 
VK_SNAPSHOT      = 0x2C 
VK_INSERT      = 0x2D 
VK_DELETE      = 0x2E 
VK_HELP      = 0x2F 
VK_0     = 0x30
VK_1     = 0x31
VK_2     = 0x32
VK_3     = 0x33
VK_4     = 0x34
VK_5     = 0x35
VK_6     = 0x36
VK_7     = 0x37
VK_8     = 0x38
VK_9     = 0x39
VK_A     = 0x41
VK_B     = 0x42
VK_C     = 0x43
VK_D     = 0x44
VK_E     = 0x45
VK_F     = 0x46
VK_G     = 0x47
VK_H     = 0x48
VK_I     = 0x49
VK_J     = 0x4A 
VK_K     = 0x4B 
VK_L     = 0x4C 
VK_M     = 0x4D 
VK_N     = 0x4E 
VK_O     = 0x4F 
VK_P     = 0x50
VK_Q     = 0x51
VK_R     = 0x52
VK_S     = 0x53
VK_T     = 0x54
VK_U     = 0x55
VK_V     = 0x56
VK_W     = 0x57
VK_X     = 0x58
VK_Y     = 0x59
VK_Z     = 0x5A 
VK_NUMPAD0      = 0x60
VK_NUMPAD1      = 0x61
VK_NUMPAD2      = 0x62
VK_NUMPAD3      = 0x63
VK_NUMPAD4      = 0x64
VK_NUMPAD5      = 0x65
VK_NUMPAD6      = 0x66
VK_NUMPAD7      = 0x67
VK_NUMPAD8      = 0x68
VK_NUMPAD9      = 0x69
VK_SEPARATOR      = 0x6C 
VK_SUBTRACT      = 0x6D 
VK_DECIMAL      = 0x6E 
VK_DIVIDE      = 0x6F 
VK_F1      = 0x70
VK_F2      = 0x71
VK_F3      = 0x72
VK_F4      = 0x73
VK_F5      = 0x74
VK_F6      = 0x75
VK_F7      = 0x76
VK_F8      = 0x77
VK_F9      = 0x78
VK_F10      = 0x79
VK_F11      = 0x7A 
VK_F12      = 0x7B 
VK_F13      = 0x7C 
VK_F14      = 0x7D 
VK_F15      = 0x7E 
VK_F16      = 0x7F 
VK_F17      = 0x80
VK_F18      = 0x81
VK_F19      = 0x82
VK_F20      = 0x83
VK_F21      = 0x84
VK_F22      = 0x85
VK_F23      = 0x86
VK_F24      = 0x87
VK_NUMLOCK      = 0x90
VK_SCROLL      = 0x91
VK_LSHIFT      = 0xA0 
VK_RSHIFT      = 0xA1 
VK_LCONTROL      = 0xA2 
VK_RCONTROL      = 0xA3 
VK_LMENU      = 0xA4 
VK_RMENU      = 0xA5 
VK_PLAY      = 0xFA 
VK_ZOOM      = 0xFB 

class KeyInput(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
    def __init__(self):
        self.type = 1
        self.time = 0
        self.extra = ctypes.c_ulong(0)
        self.dwExtraInfo = ctypes.pointer(self.extra)
        
    def setVK(self, vk):
        self.wVk = vk
        self.wScan = 0
        self.dwFlags = 0
        
    def setKeyDown(self):
        self.dwFlags = 0
    
    def setKeyUp(self):
        self.dwFlags = 2

_keyInput = KeyInput()


def _sendModifiers(mods, press):
    if mods & 0x01:
        _sendVirtual(0x10, press)
    if mods & 0x02:
        _sendVirtual(0x11, press)
    if mods & 0x04:
        _sendVirtual(0x12, press)

def _sendVirtual(vk, press=True):
    
    _keyInput.setVK(vk)
    
    if press:
        _keyInput.setKeyDown()
    else:
        _keyInput.setKeyUp()

    ctypes.windll.user32.SendInput(1, ctypes.byref(_keyInput), 28)

def _sendScanCode(scanCode, press=True):
    scanned = ctypes.windll.user32.VkKeyScanA(ord(scanCode))
    vk = scanned & 0xff
    modifiers = scanned >> 8
    if press and modifiers: _sendModifiers(modifiers, True)
    _sendVirtual(vk, press)
    if not press and modifiers: _sendModifiers(modifiers, False)

def _sendTokens(tokens, press=True):
    vks = []
    for token in tokens.upper().split():
        try:
            vk = globals()['VK_'+token] 
        except:
            raise Exception("no virtual key [VK_]%s" % token)
        vks.append(vk)
    if not press: vks.reverse()
    for vk in vks:
        _sendVirtual(vk, press)

def _send(key, press=True):

    if isinstance(key, int):
        return _sendVirtual(key, press)
    
    if isinstance(key, str):
        n = len(key)
        if n==1:
            return _sendScanCode(key, press)
        if n>1:
            return _sendTokens(key, press)
        
    raise Exception("unsupported key %s" % key)

def click(c):
    _send(c, True)
    _send(c, False)

def press(c):
    _send(c, True)

def release(c):
    _send(c, False)

def sync():
    pass