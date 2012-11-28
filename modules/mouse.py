import logging, ctypes, threading, windows, win32api

from ctypes import c_int, c_short, c_long, WINFUNCTYPE, Structure, cdll
from threading import Lock, Thread

WH_MOUSE_LL = 14
WM_MOUSEWHEEL = 0x020A
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

class _Atomic:
    def __init__(self, value=None):
        self._lock = threading.Lock()
        self._value = value
    def add(self, value):
        with self._lock:
            self._value += value
    def set(self, value):
        with self._lock:
            result = self._value
            self._value = value
        return result
    
class _Hook(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
        
    def run(self):
        self._callback = LOWLEVELMOUSEPROC(self.lowLevelMouseProc) # protect against garbage collection
        self._handle = ctypes.windll.user32.SetWindowsHookExA(WH_MOUSE_LL, self._callback, windows.loadLibrary("user32.dll"), 0)
        if self._handle:
            windows.pumpMessages()
        else:
            _log.warn("Can't hook into mouse events - %s" % ctypes.WinError())
 
    def lowLevelMouseProc(self, nCode, wParam, lParam):
        if wParam==WM_MOUSEHWHEEL:
            _hWheel.add( ctypes.c_long( ctypes.cast(lParam, PMSLLHOOKSTRUCT)[0].mouseData).value>>16 )
        if wParam==WM_MOUSEWHEEL:
            _wheel.add( ctypes.c_long( ctypes.cast(lParam, PMSLLHOOKSTRUCT)[0].mouseData).value>>16 )
        return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lParam)


_log = logging.getLogger("mouse")
_hWheel = _Atomic(0)
_wheel = _Atomic(0)
_hook = _Hook()

def getWheel():
    return _wheel.set(0)
    
def getHWheel():
    return _hWheel.set(0)

def sync():
    pass
