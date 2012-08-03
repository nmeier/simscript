'''

 A FSX Sim Connect abstraction layer that allows simscripts to read and write simulator variables
 
 An understanding of http://msdn.microsoft.com/en-us/library/cc526981.aspx is required.

'''
import logging,time,ctypes.wintypes,sys,traceback,decimal,tempfile

_SIMCONNECT_OBJECT_ID_USER = 0

_SIMCONNECT_EVENT_FLAG_DEFAULT                  = 0x00000000      
_SIMCONNECT_EVENT_FLAG_FAST_REPEAT_TIMER        = 0x00000001      # set event repeat timer to simulate fast repeat
_SIMCONNECT_EVENT_FLAG_SLOW_REPEAT_TIMER        = 0x00000002      # set event repeat timer to simulate slow repeat
_SIMCONNECT_EVENT_FLAG_GROUPID_IS_PRIORITY      = 0x00000010      # interpret GroupID parameter as priority value

(_SIMCONNECT_DATATYPE_INVALID,
 _SIMCONNECT_DATATYPE_INT32,
 _SIMCONNECT_DATATYPE_INT64,
 _SIMCONNECT_DATATYPE_FLOAT32,
 _SIMCONNECT_DATATYPE_FLOAT64,
 _SIMCONNECT_DATATYPE_STRING8,
 _SIMCONNECT_DATATYPE_STRING32,
 _SIMCONNECT_DATATYPE_STRING64,
 _SIMCONNECT_DATATYPE_STRING128,
 _SIMCONNECT_DATATYPE_STRING256,
 _SIMCONNECT_DATATYPE_STRING260,
 _SIMCONNECT_DATATYPE_STRINGV,
 _SIMCONNECT_DATATYPE_INITPOSITION,
 _SIMCONNECT_DATATYPE_MARKERSTATE,
 _SIMCONNECT_DATATYPE_WAYPOINT,
 _SIMCONNECT_DATATYPE_LATLONALT,
 _SIMCONNECT_DATATYPE_XYZ ) = range(17)

(_SIMCONNECT_PERIOD_NEVER, 
 _SIMCONNECT_PERIOD_ONCE, 
 _SIMCONNECT_PERIOD_VISUAL_FRAME, 
 _SIMCONNECT_PERIOD_SIM_FRAME, 
 _SIMCONNECT_PERIOD_SECOND) = range(5)

(_SIMCONNECT_RECV_ID_NULL,
 _SIMCONNECT_RECV_ID_EXCEPTION,
 _SIMCONNECT_RECV_ID_OPEN,
 _SIMCONNECT_RECV_ID_QUIT,
 _SIMCONNECT_RECV_ID_EVENT,
 _SIMCONNECT_RECV_ID_EVENT_OBJECT_ADDREMOVE,
 _SIMCONNECT_RECV_ID_EVENT_FILENAME,
 _SIMCONNECT_RECV_ID_EVENT_FRAME,
 _SIMCONNECT_RECV_ID_SIMOBJECT_DATA,
 _SIMCONNECT_RECV_ID_SIMOBJECT_DATA_BYTYPE,
 _SIMCONNECT_RECV_ID_CLOUD_STATE,
 _SIMCONNECT_RECV_ID_WEATHER_OBSERVATION,
 _SIMCONNECT_RECV_ID_ASSIGNED_OJBECT_ID,
 _SIMCONNECT_RECV_ID_RESERVED_KEY,
 _SIMCONNECT_RECV_ID_CUSTOM_ACTION,
 _SIMCONNECT_RECV_ID_SYSTEM_STATE,
 _SIMCONNECT_RECV_ID_CLIENT_DATA,
 _SIMCONNECT_RECV_ID_EVENT_WEATHER_MODE,
 _SIMCONNECT_RECV_ID_AIRPORT_LIST,
 _SIMCONNECT_RECV_ID_VOR_LIST,
 _SIMCONNECT_RECV_ID_NDB_LIST,
 _SIMCONNECT_RECV_ID_WAYPOINT_LIST,
 _SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_SERVER_STARTED,
 _SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_CLIENT_STARTED,
 _SIMCONNECT_RECV_ID_EVENT_MULTIPLAYER_SESSION_ENDED,
 _SIMCONNECT_RECV_ID_EVENT_RACE_END,
 _SIMCONNECT_RECV_ID_EVENT_RACE_LAP) = range(27)
    
class _SIMCONNECT_RECV(ctypes.Structure):
    """ SimConnect's base class of received events """
    _fields_ = [
        ("dwSize", ctypes.wintypes.DWORD ), 
        ("dwVersion", ctypes.wintypes.DWORD ), 
        ("dwId", ctypes.wintypes.DWORD )
    ]

class _SIMCONNECT_RECV_SIMOBJECT_DATA(ctypes.Structure):
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

class _Value:
    def __init__(self):
        self.value = None
        self.id = None
        
_DISCONNECT_RESULTS = [ 0xC000013C, 0xC000014B, 0xC000020C, 0xC0000237, 0x80000025 ]    
_IGNORED_RESULTS = [ 0x80004005 ]
_RECONNECT_WAIT_SECONDS = 5
_READ_DATA_DEFINITION_ID = 0
_WRITE_DATA_DEFINITION_ID = 1

_log = logging.getLogger(__name__)
_datumunit2datadefinitionindex = dict()
_datumunit2value = dict()
_datumvalueWrites = []
_datum2simevent = dict()
_dll = None
_hsimconnect = ctypes.wintypes.HANDLE()
_lastconnect = 0
_nextDataDefinitionIndex = 0
_nextSimEventId = 0
        
def _init():
    
    global _dll

    # create and activate activation context
    assembly = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    assembly.write("""<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
        <assembly xmlns='urn:schemas-microsoft-com:asm.v1' manifestVersion='1.0'>
          <dependency><dependentAssembly>
              <assemblyIdentity type='win32' name='Microsoft.FlightSimulator.SimConnect ' version='10.0.61242.0' processorArchitecture='x86' publicKeyToken='67c7c14424d61b5b' />
          </dependentAssembly></dependency>
        </assembly>""")
    assembly.close()
            
    actctx = _ACTCTX();
    actctx.size = ctypes.sizeof(actctx)
    actctx.lpSource = ctypes.wintypes.LPSTR(assembly.name.encode())
    if not ctypes.windll.Kernel32.ActivateActCtx(
        ctypes.wintypes.HANDLE(ctypes.windll.Kernel32.CreateActCtxA(ctypes.byref(actctx))), 
        ctypes.byref(ctypes.wintypes.ULONG())):
        _log.debug("cannot establish activation context for Windows Side-by-side Assemblies - loading SimConnect.dll might fail") 

    # now try to load SimConnect.dll        
    try:
        _dll = ctypes.oledll.SimConnect
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
    
    if _hsimconnect : 
        return True
    
    try:
        _dll.SimConnect_Open(ctypes.byref(_hsimconnect), "FSScript", None, 0, 0, 0)
    except WindowsError: 
        return False;
    
    _datumunit2datadefinitionindex.clear()
    _datum2simevent.clear()
        
    _nextDataDefinitionIndex = 0
    _nextSimEventId = 0

    return True
    
def _disconnect():
    if not _hsimconnect:
        return; 
    try: 
        _dll.SimConnect_Close(ctypes.byref(_hsimconnect))
    except Exception: 
        pass
        
def _syncWrites():
    
    global _nextSimEventId
    
    if not _datumvalueWrites:
        return
    
    for datum, value in _datumvalueWrites:
        
        # all writes have to be mapped to sim events
        try:
            simEvent = _datum2simevent[datum]
        except KeyError:
            try:
                simEvent = _nextSimEventId
                _dll.SimConnect_MapClientEventToSimEvent(_hsimconnect, simEvent, ctypes.wintypes.LPCSTR(datum))
                _datum2simevent[datum] = simEvent;
                _nextSimEventId += 1
                _log.debug("Mapped %s to %s client event" % (datum, simEvent))
            except WindowsError:
                _log.warning("Failed to map %s to %s client event" % (datum, simEvent))
                _log.debug(traceback.format_exc())
                continue
                
        # transmit
        try:
            #SimConnect_TransmitClientEvent(self._simhandle, 0, var.id, ctypes.wintypes.DWORD(var.encode(var.value)), 1, 0x00000010)
            #_dll.SimConnect_TransmitClientEvent(_hsimconnect, 0, simEvent, ctypes.wintypes.DWORD(value), 1, _SIMCONNECT_EVENT_FLAG_GROUPID_IS_PRIORITY)
            _dll.SimConnect_TransmitClientEvent(_hsimconnect, 0, simEvent, ctypes.wintypes.DWORD(value), 1, 0x00000010)
        except:
            _log.warning("Failed to transmit client event %s for %s" % (simEvent, datum))
            _log.debug(traceback.format_exc())

    del _datumvalueWrites[:]
       
def _syncReads():
    
    global _nextDataDefinitionIndex
    
    # bail if there are no vars in data definition
    if len(_datumunit2value)==0:
        return
    
    # add to data definition where still needed
    for datumunit in _datumunit2value:
        
        try:
            _datumunit2datadefinitionindex[ datumunit ]
        except KeyError:
            datum, unit = datumunit
            try:
                _dll.SimConnect_AddToDataDefinition(
                    _hsimconnect, 
                    _READ_DATA_DEFINITION_ID, 
                    ctypes.wintypes.LPCSTR(datum), 
                    ctypes.wintypes.LPCSTR(unit), 
                    _SIMCONNECT_DATATYPE_FLOAT64, 
                    0, 
                    -1)
                _datumunit2datadefinitionindex[ datumunit ] = _nextDataDefinitionIndex
                _log.debug("Added %s to SimConnect data definition index=%d" % (datum, _nextDataDefinitionIndex))
                _nextDataDefinitionIndex += 1
            except WindowsError:
                _log.warning("Failed to add %s to SimConnect data definition" % datum)

    # request all previously defined data
    try:
        _dll.SimConnect_RequestDataOnSimObject(_hsimconnect, _READ_DATA_DEFINITION_ID, _READ_DATA_DEFINITION_ID, _SIMCONNECT_OBJECT_ID_USER, _SIMCONNECT_PERIOD_ONCE, 0, 0, 0, 0)
    except WindowsError:
        _log.warning("Failed to request read on SimConnect user aircraft object")
        _disconnect()
        return

    # wait for data 
    precv = ctypes.POINTER(_SIMCONNECT_RECV)()
    rlen = ctypes.wintypes.DWORD()

    while True:
        
        try:
            _dll.SimConnect_GetNextDispatch(_hsimconnect, ctypes.byref(precv), ctypes.byref(rlen))
            
            if precv.contents.dwId==_SIMCONNECT_RECV_ID_QUIT:
                _log.info("user quitting FSX")
                _disconnect()
                return
    
            if precv.contents.dwId==_SIMCONNECT_RECV_ID_SIMOBJECT_DATA:
                precv = ctypes.cast(precv, ctypes.POINTER(_SIMCONNECT_RECV_SIMOBJECT_DATA))
                if precv.contents.dwDefineID == _READ_DATA_DEFINITION_ID:
                    break
                
        except WindowsError:
            rc = 0x100000000 + sys.exc_info()[1].winerror
            if rc in _DISCONNECT_RESULTS:
                _log.warning("disconnected from SimConnect")
                _disconnect()
                return
            if not rc in _IGNORED_RESULTS:
                _log.debug("failed to read next dispatch from SimConnect 0x%X" % rc)

    # read data and keep 
    pdata = ctypes.cast(precv.contents.dwData, ctypes.POINTER(ctypes.wintypes.DOUBLE))
    for datumunit, index in _datumunit2datadefinitionindex.items():
        if index>=precv.contents.dwDefineCount:
            _log.debug("no data received for %s, %d>=%d" % (datumunit,index,precv.contents.dwDefineCount) )
            continue
        _datumunit2value[datumunit] = pdata[index]

def get(datum, unit, decode=lambda x: x):
    try:
        value = _datumunit2value[(datum,unit)]
        return decode(value) if value!=None else None 
    except KeyError:
        _datumunit2value[(datum,unit)] = None
        return None

def set(datum, value=0, encode=lambda x: x): #@ReservedAssignment

    _datumvalueWrites.append( (datum,encode(value)) )    

def sync(): 
    
    # active?
    if not _datumvalueWrites and not _datumunit2value:
        return
    
    global _lastconnect
    if not _hsimconnect :
        if _lastconnect > time.time() - _RECONNECT_WAIT_SECONDS:
            return
        _lastconnect = time.time()
        if not _connect() : 
            _log.info("SimConnect not established")
            return
        _log.info("SimConnect established")
        
    # do pending sets
    _syncWrites()
    
    # do reads
    _syncReads()

_init()        
        
