import win32gui, win32con, win32gui_struct, os.path, win32api, win32event, winerror
 
class TrayIcon:
  
    def _commandCallback(self, hwnd, msg, wparam, lparam):
        try:
            key = win32gui.LOWORD(wparam)
            _,_,_,callback = self._key2callback[key]
            callback(key)
        except:            pass
    
    def _notifyCallback(self, hwnd, msg, wparam, lparam):
        if not lparam in [win32con.WM_LBUTTONDBLCLK, win32con.WM_RBUTTONUP, win32con.WM_LBUTTONUP]:
            return
        hMenu = win32gui.CreatePopupMenu()
        
        for key in self._keys:
            txt, bmp, checked, _ = self._key2callback[key]
            if checked is None:
                item, _ = win32gui_struct.PackMENUITEMINFO(text=txt,hbmpItem=bmp, wID=key)
            else:
                item, _ = win32gui_struct.PackMENUITEMINFO(text=txt,hbmpItem=bmp, wID=key, fState = win32con.MFS_CHECKED if checked else win32con.MFS_UNCHECKED) 
            win32gui.InsertMenuItem(hMenu, 0, 1, item)
    
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(hwnd)
        win32gui.TrackPopupMenu(hMenu,win32con.TPM_LEFTALIGN,pos[0],pos[1],0,hwnd,None)
        win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)
    
    
    def __init__(self, tip, ico):
        
        if not ico: raise
        
        self._key2callback = dict()
        self._keys = []
        self._tip = tip
        self._ico = ico
        
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
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self._hwnd, 0))
        win32gui.DestroyWindow(self._hwnd)
        win32gui.PostQuitMessage(0) 
        self._hwnd = None
       
    def add(self, txt, bmp, checked, callback):
        key = 1023 if not self._keys else self._keys[-1] + 1
        self._keys.append(key)
        self._key2callback[key] = (txt, bmp, checked, callback)
        return key
        
    def remove(self, key):
        del(self._key2callback[key])
        del(self._keys[key])
        
    def check(self, key, checked=True):
        try:
            for k in key: self.check(k, checked)
        except:
            txt, bmp, _, callback = self._key2callback[key]
            self._key2callback[key] = (txt, bmp, checked, callback) 
                
    def pump(self, block=True):
        if not self._hwnd: raise
        if block:
            win32gui.PumpMessages()
        else:
            win32gui.PumpWaitingMessages()    
            
def singleton():
    win32event.CreateMutex(None, False, "5ea86490-d4ec-11e1-9b23-0800200c9a66")
    return win32api.GetLastError() != winerror.ERROR_ALREADY_EXISTS

if __name__ == "__main__":    
    icon = TrayIcon("Test", os.path.join(os.path.dirname(__file__), 'simscript.ico'))
    icon.add("Quit", None, None, lambda _: icon.close() )
    icon.add("Action 1", None, None, lambda _: print("1") )

    options = []
    options.append(icon.add("Option 1", None, True, lambda key: icon.check(options, False) & icon.check(key)  ))
    options.append(icon.add("Option 2", None, False, lambda key: icon.check(options, False) & icon.check(key)  ))
    
    icon.pump()
    
        

