'''
Created on 2011-02-26

@author: Nils
'''
import logging,time,os.path,ctypes.wintypes,sys,traceback,decimal

class _SimConnect:
    
    (SIMCONNECT_DATATYPE_INVALID,
     SIMCONNECT_DATATYPE_INT32,
     SIMCONNECT_DATATYPE_INT64,
     SIMCONNECT_DATATYPE_FLOAT32,
     SIMCONNECT_DATATYPE_FLOAT64,
     SIMCONNECT_DATATYPE_STRING8,
     SIMCONNECT_DATATYPE_STRING32,
     SIMCONNECT_DATATYPE_STRING64,
     SIMCONNECT_DATATYPE_STRING128,
     SIMCONNECT_DATATYPE_STRING256,
     SIMCONNECT_DATATYPE_STRING260,
     SIMCONNECT_DATATYPE_STRINGV,
     SIMCONNECT_DATATYPE_INITPOSITION,
     SIMCONNECT_DATATYPE_MARKERSTATE,
     SIMCONNECT_DATATYPE_WAYPOINT,
     SIMCONNECT_DATATYPE_LATLONALT,
     SIMCONNECT_DATATYPE_XYZ ) = range(17)
    
    (SIMCONNECT_PERIOD_NEVER, 
     SIMCONNECT_PERIOD_ONCE, 
     SIMCONNECT_PERIOD_VISUAL_FRAME, 
     SIMCONNECT_PERIOD_SIM_FRAME, 
     SIMCONNECT_PERIOD_SECOND) = range(5)
    
    (SIMCONNECT_RECV_ID_NULL,
     SIMCONNECT_RECV_ID_EXCEPTION,
     SIMCONNECT_RECV_ID_OPEN,
     SIMCONNECT_RECV_ID_QUIT,
     SIMCONNECT_RECV_ID_EVENT,
     SIMCONNECT_RECV_ID_EVENT_OBJECT_ADDREMOVE,
     SIMCONNECT_RECV_ID_EVENT_FILENAME,
     SIMCONNECT_RECV_ID_EVENT_FRAME,
     SIMCONNECT_RECV_ID_SIMOBJECT_DATA,
     SIMCONNECT_RECV_ID_SIMOBJECT_DATA_BYTYPE,
     SIMCONNECT_RECV_ID_CLOUD_STATE,
     SIMCONNECT_RECV_ID_WEATHER_OBSERVATION,
     SIMCONNECT_RECV_ID_ASSIGNED_OJBECT_ID,
     SIMCONNECT_RECV_ID_RESERVED_KEY,
     SIMCONNECT_RECV_ID_CUSTOM_ACTION,
     SIMCONNECT_RECV_ID_SYSTEM_STATE,
     SIMCONNECT_RECV_ID_CLIENT_DATA,
     SIMCONNECT_RECV_ID_EVENT_WEATHER_MODE,
     SIMCONNECT_RECV_ID_AIRPORT_LIST,
     SIMCONNECT_RECV_ID_VOR_LIST,
     SIMCONNECT_RECV_ID_NDB_LIST,
     SIMCONNECT_RECV_ID_WAYPOINT_LIST,
     SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_SERVER_STARTED,
     SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_CLIENT_STARTED,
     SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_SESSION_ENDED,
     SIMCONNECT_RECV_ID_EVENT_RACE_END,
     SIMCONNECT_RECV_ID_EVENT_RACE_LAP) = range(27)
    
    class SIMCONNECT_RECV(ctypes.Structure):
        """ SimConnect's base class of received events """
        _fields_ = [
            ("dwSize", ctypes.wintypes.DWORD ), 
            ("dwVersion", ctypes.wintypes.DWORD ), 
            ("dwId", ctypes.wintypes.DWORD )
        ]
    
    class SIMCONNECT_RECV_SIMOBJECT_DATA(ctypes.Structure):
        """ SimConnect's sim data received setevent """
        _fields_ = [
            ("dwSize", ctypes.wintypes.DWORD ), 
            ("dwVersion", ctypes.wintypes.DWORD ), 
            ("dwId", ctypes.wintypes.DWORD ),
            ("dwRequestID", ctypes.wintypes.DWORD ), 
            ("dwObjectID", ctypes.wintypes.DWORD ), 
            ("dwDefineID", ctypes.wintypes.DWORD ), 
            ("dwFlags", ctypes.wintypes.DWORD ), 
            ("dwentrynumber", ctypes.wintypes.DWORD ), 
            ("dwoutof", ctypes.wintypes.DWORD ), 
            ("dwDefineCount", ctypes.wintypes.DWORD ), 
            ("dwData", ctypes.wintypes.DOUBLE * 1 )
        ]  

        
class _ACTCTX(ctypes.Structure):
    ''' An activation context is Windows way of handling side-by-side assembly of different DLL versions. To find
        SimConnect.dll this mechanism can find the correct version in e.g. 
             C:\windows\WinSxS\x86_Microsoft.FlightSimulator.SimConnect_TOKEN_VERSION_...\SimConnect.dll
        see http://msdn.microsoft.com/en-us/library/aa374151%28v=VS.85%29.aspx 
        see http://social.msdn.microsoft.com/Forums/en-US/vcgeneral/thread/04b6ec57-fa16-4a54-b850-23278da752fa '''
    _fields_ = [
        ("size", ctypes.wintypes.ULONG ), 
        ("dwFlags", ctypes.wintypes.DWORD ), 
        ("lpSource", ctypes.wintypes.LPSTR ), 
        ("wProcessorArchitecture", ctypes.wintypes.USHORT ), 
        ("wLangId", ctypes.wintypes.DWORD ), 
        ("lpAssemblyDirectory", ctypes.wintypes.LPSTR ), 
        ("lpResourceName", ctypes.wintypes.LPSTR ), 
        ("lpApplicationName", ctypes.wintypes.LPSTR ), 
        ("hModule", ctypes.wintypes.HMODULE )
    ]    

class _SimVar:
    
    count = 0
    
    def __init__(self, datum, unit, decode):
        self.id = _SimVar.count
        _SimVar.count+=1
        self.datum = datum
        self.unit = unit
        self.decode = decode
        self.value = None
    def __str__(self):
        return "%s: %s" % (self.datum, self.value)
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
        
_log = logging.getLogger(__name__)
_disconnecthresults = [ 0xC000013C, 0xC000014B, 0xC000020C, 0xC0000237, 0x80000025 ]    
_ignorehresults = [ 0x80004005 ]
_readid = 0
_writeid = 1
_vars = dict()
_writes = set()
_simconnect = None
_simhandle = ctypes.wintypes.HANDLE()
_reconnectwait = 5
_connectattempt = 0
        
def _makeproperty(self, datum, unit, decode, simevent=None, encode=None):
    instances = dict()
    def var(simobj):
        instance = 1 if not hasattr(simobj,"instance") else simobj.instance
        try: 
            return instances[instance]
        except KeyError:
            v = _SimVar(datum[instance-1] if type(datum)==tuple else datum.format(instance), unit, decode, simevent[instance-1] if type(simevent)==tuple else simevent.format(instance), encode)
            instances[instance] = v
            self._vars.append(v)
            return v
    def read(simobj):
        return var(simobj).get()
    def write(simobj,value):
        v = var(simobj)
        if v.get() == value:
            return
        _log.debug("Setting %s to %s" % (v.datum, value))
        v.set(value)
        self._writes.add(v)
    return property(read,write if simevent and encode else None)


def _init():
    
    global _simconnect

    # create and activate activation context
    actctx = _ACTCTX();
    actctx.size = ctypes.sizeof(actctx)
    actctx.lpSource = ctypes.wintypes.LPSTR(os.path.join(os.path.dirname(__file__), 'simconnect.manifest').encode())
    if not ctypes.windll.Kernel32.ActivateActCtx(
        ctypes.wintypes.HANDLE(ctypes.windll.Kernel32.CreateActCtxA(ctypes.byref(actctx))), 
        ctypes.byref(ctypes.wintypes.ULONG())):
        _log.info("cannot establish activation context for Windows Side-by-side Assemblies - loading SimConnect.dll might fail") 

    # now try to load SimConnect.dll        
    try:
        _simconnect = ctypes.oledll.SimConnect
    except: 
        raise EnvironmentError("Cannot initialize DLL for FSX SimConnect")
    
def bcd2int(bcd):
    bcd = int(bcd)
    result = 0
    factor = 1
    while bcd!=0:
        result += (bcd % 0x10) * factor;
        factor *= 10
        bcd = bcd >> 4;
    return result

def bcd2khz(bcd):
    decoded = decimal.Decimal(bcd2int(bcd))
    # 1802 = 118.025, 1807 = 118.75
    if decoded %5 != 0: 
        decoded += decimal.Decimal('0.5')
    return decoded/100+100

def bcd2mhz(bcd):
    return decimal.Decimal(bcd2int(bcd))/10000
        
        
def _connect():
    
    if _simhandle : 
        return True
    
    try:
        _simconnect.SimConnect_Open(ctypes.byref(_simhandle), "FSScript", None, 0, 0, 0)
    except WindowsError: 
        return False;
    
    for var in _vars:
        var.reading = False
        var.writing = False

    return True
    
def _disconnect():
    if not _simhandle:
        return; 
    try: 
        _simconnect.SimConnect_Close(ctypes.byref(_simhandle))
    except Exception: 
        pass
        
def _write():
    
    if len(_writes)==0:
        return
    
    #FSX._log.debug("Setting %s" % self._writes)

    for var in _writes:
        if not var.writing:
            try:
                _simconnect.SimConnect_MapClientEventToSimEvent(_simhandle, var.id, ctypes.wintypes.LPCSTR(var.simevent))
                _log.debug("Mapped %s to %s client event" % (var.datum, var.simevent))
                var.writing = True
            except WindowsError:
                _log.warning("Failed to map %s to %s client event" % (var.datum, var.simevent))
        try:
            _simconnect.SimConnect_TransmitClientEvent(_simhandle, 0, var.id, ctypes.wintypes.DWORD(var.encode(var.value)), 1, 0x00000010)
        except:
            _log.warning("Failed to transmit client event %s" % var.simevent)
            _log.debug("Failed to transmit client event %s" % traceback.format_exc())

    _writes.clear()

# the almost unsupported SetDataOnSimObject
#        try:
#            self._simconnect.SimConnect_ClearDataDefinition(self._simhandle, FSX._writeid)
#        except WindowsError:
#            FSX._log.warning("Failed to clear data definition for write of %s (%s)" % (self._setvars, sys.exc_info()))
#            return
#        class Data(ctypes.Structure):
#            _fields_ = [ ("values", ctypes.wintypes.DOUBLE * len(self._setvars)) ] 
#        data = Data()
#        i = 0
#        for var in self._setvars:
#            try:
#                self._simconnect.SimConnect_AddToDataDefinition(self._simhandle, FSX._writeid, ctypes.wintypes.LPCSTR(var.datum), ctypes.wintypes.LPCSTR(var.unit), _SimConnect.SIMCONNECT_DATATYPE_FLOAT64, 0, -1)
#            except WindowsError:
#                FSX._log.warning("Failed to add data definition for %s (%s)" % (var, sys.exc_info()))
#                return
#            data.values[i] = var.encode(var.value)
#            i += 1
#        try:
#            self._simconnect.SimConnect_SetDataOnSimObject(self._simhandle, FSX._writeid, 0, 0, i, ctypes.sizeof(ctypes.wintypes.DOUBLE), ctypes.byref(data))
#        except WindowsError:
#            FSX._log.warning("Failed to set data on sim object (%s)" % sys.exc_info())
        
def _read(self):
    
    # bail if there are no vars to read
    if len(self._vars)==0:
        return

    # add simvar to data definition where still needed
    for var in self._vars:
        if not var.reading:
            try:
                self._simconnect.SimConnect_AddToDataDefinition(self._simhandle, _readid, ctypes.wintypes.LPCSTR(var.datum), ctypes.wintypes.LPCSTR(var.unit), _SimConnect.SIMCONNECT_DATATYPE_FLOAT64, 0, -1)
                _log.debug("Added %s to SimConnect data definition" % var.datum)
                var.reading = True
            except WindowsError:
                _log.warning("Failed to add %s to SimConnect data definition" % var.datum)

    # request data
    try:
        self._simconnect.SimConnect_RequestDataOnSimObject(self._simhandle, _readid, _readid, 0, _SimConnect.SIMCONNECT_PERIOD_ONCE, 0, 0, 0, 0)
    except WindowsError:
        _log.warning("Failed to request read on SimConnect user aircraft object")
        self._disconnect()
        return

    # wait for data 
    precv = ctypes.POINTER(_SimConnect.SIMCONNECT_RECV)()
    rlen = ctypes.wintypes.DWORD()

    while True:
        
        try:
            self._simconnect.SimConnect_GetNextDispatch(self._simhandle, ctypes.byref(precv), ctypes.byref(rlen))
            
            if precv.contents.dwId==_SimConnect.SIMCONNECT_RECV_ID_QUIT:
                _log.info("user quitting FSX")
                self._disconnect()
                return
    
            if precv.contents.dwId==_SimConnect.SIMCONNECT_RECV_ID_SIMOBJECT_DATA:
                precv = ctypes.cast(precv, ctypes.POINTER(_SimConnect.SIMCONNECT_RECV_SIMOBJECT_DATA))
                if precv.contents.dwDefineID == _readid:
                    break
                
        except WindowsError:
            rc = 0x100000000 + sys.exc_info()[1].winerror
            if rc in _disconnecthresults:
                _log.warning("disconnected from SimConnect")
                self._disconnect()
                return
            if not rc in _ignorehresults:
                _log.debug("failed to read next dispatch from SimConnect 0x%X" % rc)

    # read data
    pdata = ctypes.cast(precv.contents.dwData, ctypes.POINTER(ctypes.wintypes.DOUBLE))
    for i,var in enumerate(self._vars):
        if i==precv.contents.dwDefineCount: break
        var.set(var.decode(pdata[i]))

def get(datum, unit, decode):
    key = (datum,unit,decode)
    try:
        var = _vars[key]
    except KeyError:
        var = _SimVar(datum,unit,decode)
        _vars[key] = var
    result = var.get()
    return decode(result) if result!=None else None 

def sync(): 
    
    # active?
    if len(_writes)==0 and len(_vars)==0:
        return
    
    global _connectattempt
    if not _simhandle :
        if _connectattempt > time.time() - _reconnectwait:
            return
        _connectattempt = time.time()
        if not _connect() : 
            _log.info("SimConnect not established")
            return
        _log.info("SimConnect established")
        
    # do pending sets
    _write()
    
    # do reads
    _read()

_init()        
        
