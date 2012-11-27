import win32gui, win32con, win32gui_struct, os.path, win32api, win32event, winerror, logging

try:
    import _winreg as winreg #@UnusedImport
except:
    import winreg #@Reimport

class TrayIcon:
  
    def _commandCallback(self, hwnd, msg, wparam, lparam):
        try:
            callback = self._callbacks[win32gui.LOWORD(wparam)]
        except:
            return
        callback()
    
    def _notifyCallback(self, hwnd, msg, wparam, lparam):
        if not lparam in [win32con.WM_LBUTTONDBLCLK, win32con.WM_RBUTTONUP, win32con.WM_LBUTTONUP]:
            return
        hMenu = win32gui.CreatePopupMenu()
        
        self._callbacks.clear()
        
        items = self._items() if callable(self._items) else self._items
        
        wId = 1023
        for txt, bmp, checked, callback in items:
            if checked is None:
                item, _ = win32gui_struct.PackMENUITEMINFO(text=str(txt),hbmpItem=bmp, wID=wId)
            else:
                item, _ = win32gui_struct.PackMENUITEMINFO(text=str(txt),hbmpItem=bmp, wID=wId, fState = win32con.MFS_CHECKED if checked else win32con.MFS_UNCHECKED) 
            win32gui.InsertMenuItem(hMenu, 0, 1, item)
            self._callbacks[wId] = callback
            wId += 1
    
        pos = win32gui.GetCursorPos()
        try:
            win32gui.SetForegroundWindow(hwnd)
            win32gui.TrackPopupMenu(hMenu,win32con.TPM_LEFTALIGN,pos[0],pos[1],0,hwnd,None)
            win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)
        except:
            pass
        

        win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    def __init__(self, tip, ico, items):
        
        if not ico: raise
        
        self._callbacks = dict()
        self._keys = []
        self._tip = tip
        self._ico = ico
        self._items = items
        
        windowClass = win32gui.WNDCLASS()
        windowClass.hInstance = win32gui.GetModuleHandle(None)
        windowClass.lpszClassName = "5ea86490-d4ec-11e1-9b23-0800200c9a66"
        windowClass.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        windowClass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        windowClass.hbrBackground = win32con.COLOR_WINDOW
        windowClass.lpfnWndProc = {win32con.WM_COMMAND: self._commandCallback, win32con.WM_USER+20 : self._notifyCallback} 
        
        self._hwnd = win32gui.CreateWindow(win32gui.RegisterClass(windowClass),windowClass.lpszClassName,win32con.WS_OVERLAPPED | win32con.WS_SYSMENU,0,0,win32con.CW_USEDEFAULT,win32con.CW_USEDEFAULT,0,0,windowClass.hInstance,None)
        
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, (self._hwnd,0,win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,win32con.WM_USER+20,win32gui.LoadImage(win32gui.GetModuleHandle(None), os.path.abspath(self._ico), win32con.IMAGE_ICON,0,0,win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE), self._tip))
        
    def close(self):
        if not self._hwnd:
            return
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self._hwnd, 0))
        win32gui.DestroyWindow(self._hwnd)
        win32gui.PostQuitMessage(0) 
        self._hwnd = None
       
def pumpEvents(self, block=True):
    if block:
        win32gui.PumpMessages()
    else:
        win32gui.PumpWaitingMessages()    
        
def singleton():
    win32event.CreateMutex(None, False, "5ea86490-d4ec-11e1-9b23-0800200c9a66")
    return win32api.GetLastError() != winerror.ERROR_ALREADY_EXISTS

def recall(key):
    try:
        reg = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "SOFTWARE\\simscript", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(reg, key)
        return value
    except:
        logging.getLogger(__name__).warn("can't read %s from windows registry" % key)
        return None

def remember(key, value):
    reg = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "SOFTWARE\\simscript", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(reg, key, 0, winreg.REG_SZ, str(value))
    winreg.CloseKey(reg)
    
    #QueryValue(reg, installkey) == installpath and
    #CloseKey(reg)
    
if __name__ == "__main__":    
    
    option = set([True])
    
    def action():
        print("action!")
    
    def items():
        return [ 
            ("Quit", None, None, lambda: tray.close()),  
            ("Option 1", None, option, lambda: option.add(True)),
            ("Option 2", None, not option, lambda: option.discard(True))
            ("Action", None, None, lambda: action),
            ]
        
    tray = TrayIcon("Test", os.path.join(os.path.dirname(__file__), 'simscript.ico'), items)
    tray.pump()
    
        

