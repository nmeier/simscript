import logging, ctypes, threading, windows, win32gui

from ctypes import c_int, c_short, c_long, WINFUNCTYPE, Structure
from threading import Lock, Thread

WH_MOUSE_LL = 14
WM_MOUSEHWHEEL = 0x020e

class POINT(Structure):
    _fields_ = [ ("x", ctypes.wintypes.LONG), ("y", ctypes.wintypes.LONG)] 

class MSLLHOOKSTRUCT(Structure):
    _fields_ = [ 
        ("pt", POINT),
        ("mouseData", ctypes.wintypes.DWORD),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.wintypes.ULONG)
        ] 
PMSLLHOOKSTRUCT = ctypes.POINTER(MSLLHOOKSTRUCT)

LOWLEVELMOUSEPROC = WINFUNCTYPE(c_int, c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)
 
class _Hook(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
        
    def run(self):
        self.callback = LOWLEVELMOUSEPROC(self.lowLevelMouseProc)
        self.handle = ctypes.windll.user32.SetWindowsHookExA(WH_MOUSE_LL, self.callback, 0, 0)
        if self.handle:
            windows.pumpMessages()
        else:
            _log.warn("Can't hook into mouse events")
 
    def lowLevelMouseProc(self, nCode, wParam, lParam):
        global _horizontalWheel
        if wParam==WM_MOUSEHWHEEL:
            with _lock:
                _horizontalWheel += ctypes.c_long( ctypes.cast(lParam, PMSLLHOOKSTRUCT)[0].mouseData).value>>16
        return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lParam)


_log = logging.getLogger("mouse")
_lock = threading.Lock()
_horizontalWheel = 0
_hook = _Hook()

    
def getMouseHWheel():
    global _horizontalWheel
    with _lock:
        result = _horizontalWheel
        _horizontalWheel = 0
    return result

def sync():
    pass
