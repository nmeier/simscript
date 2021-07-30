import ctypes, ctypes.wintypes, sys, logging

FILE_MAP_COPY = 0x0001
FILE_MAP_WRITE = 0x0002
FILE_MAP_READ = 0x0004
FILE_MAP_ALL_ACCESS = 0x0008

class FLIGHTDATA(ctypes.Structure):
    _fields_ = (
        ("x", ctypes.wintypes.FLOAT), # Ownship North (Ft)
        ("y", ctypes.wintypes.FLOAT), # Ownship East (Ft)
        ("z", ctypes.wintypes.FLOAT), # Ownship Down (Ft)
        ("xDot", ctypes.wintypes.FLOAT), # Ownship North Rate (ft/sec)
        ("yDot", ctypes.wintypes.FLOAT), # Ownship East Rate (ft/sec)
        ("zDot", ctypes.wintypes.FLOAT), # Ownship Down Rate (ft/sec)
        ("alpha", ctypes.wintypes.FLOAT), # Ownship AOA (Degrees)
        ("beta", ctypes.wintypes.FLOAT), # Ownship Beta (Degrees)
        ("gamma", ctypes.wintypes.FLOAT), # Ownship Gamma (Radians)
        ("pitch", ctypes.wintypes.FLOAT), # Ownship Pitch (Radians)
        ("roll", ctypes.wintypes.FLOAT), # Ownship Pitch (Radians)
        ("yaw", ctypes.wintypes.FLOAT), # Ownship Pitch (Radians)
        ("mach", ctypes.wintypes.FLOAT), # Ownship Mach number
        ("kias", ctypes.wintypes.FLOAT), # Ownship Indicated Airspeed (Knots)
        ("vt", ctypes.wintypes.FLOAT), # Ownship True Airspeed (Ft/Sec)
        ("gs", ctypes.wintypes.FLOAT), # Ownship Normal Gs
        ("windOffset", ctypes.wintypes.FLOAT), # Wind delta to FPM (Radians)
        ("nozzlePos", ctypes.wintypes.FLOAT), # Ownship engine nozzle percent open (0-100)
        ("internalFuel", ctypes.wintypes.FLOAT), # Ownship internal fuel (Lbs)
        ("externalFuel", ctypes.wintypes.FLOAT), # Ownship external fuel (Lbs)
        ("fuelFlow", ctypes.wintypes.FLOAT), # Ownship fuel flow (Lbs/Hour)
        ("rpm", ctypes.wintypes.FLOAT), # Ownship engine rpm (Percent 0-103)
        ("ftit", ctypes.wintypes.FLOAT), # Ownship Forward Turbine Inlet Temp (Degrees C)
        ("gearPos", ctypes.wintypes.FLOAT), # Ownship Gear position 0 = up, 1 = down;
        ("speedBrake", ctypes.wintypes.FLOAT), # Ownship speed brake position 0 = closed, 1 = 60 Degrees open
        ("epuFuel", ctypes.wintypes.FLOAT), # Ownship EPU fuel (Percent 0-100)
        ("oilPressure", ctypes.wintypes.FLOAT), # Ownship Oil Pressure (Percent 0-100)
        ("lightBits", ctypes.wintypes.INT), # Cockpit Indicator Lights, one bit per bulb. See enum

        # These are inputs. Use them carefully
        # NB: these do not work when TrackIR device is enabled
        # NB2: launch falcon with the '-head' command line parameter to activate !
        ("headPitch", ctypes.wintypes.FLOAT), # Head pitch offset from design eye (radians)
        ("headRoll", ctypes.wintypes.FLOAT), # Head roll offset from design eye (radians)
        ("headYaw", ctypes.wintypes.FLOAT), # Head yaw offset from design eye (radians)

        ("lightBits2", ctypes.wintypes.INT), # Cockpit Indicator Lights, one bit per bulb. See enum
        ("lightBits3", ctypes.wintypes.INT), # Cockpit Indicator Lights, one bit per bulb. See enum
        ("ChaffCount", ctypes.wintypes.FLOAT), # Number of Chaff left
        ("FlareCount", ctypes.wintypes.FLOAT), # Number of Flare left
        ("NoseGearPos", ctypes.wintypes.FLOAT), # Position of the nose landinggear; caution: full down values defined in dat files
        ("LeftGearPos", ctypes.wintypes.FLOAT), # Position of the left landinggear; caution: full down values defined in dat files
        ("RightGearPos", ctypes.wintypes.FLOAT), # Position of the right landinggear; caution: full down values defined in dat files
        ("AdiIlsHorPos", ctypes.wintypes.FLOAT), # Position of horizontal ILS bar
        ("AdiIlsVerPos", ctypes.wintypes.FLOAT), # Position of vertical ILS bar
        ("courseState", ctypes.wintypes.INT), # HSI_STA_CRS_STATE
        ("headingState", ctypes.wintypes.INT), # HSI_STA_HDG_STATE
        ("totalStates", ctypes.wintypes.INT), # HSI_STA_TOTAL_STATES; never set
        ("courseDeviation", ctypes.wintypes.FLOAT), # HSI_VAL_CRS_DEVIATION
        ("desiredCourse", ctypes.wintypes.FLOAT), # HSI_VAL_DESIRED_CRS
        ("distanceToBeacon", ctypes.wintypes.FLOAT), # HSI_VAL_DISTANCE_TO_BEACON
        ("bearingToBeacon", ctypes.wintypes.FLOAT), # HSI_VAL_BEARING_TO_BEACON
        ("currentHeading", ctypes.wintypes.FLOAT), # HSI_VAL_CURRENT_HEADING
        ("desiredHeading", ctypes.wintypes.FLOAT), # HSI_VAL_DESIRED_HEADING
        ("deviationLimit", ctypes.wintypes.FLOAT), # HSI_VAL_DEV_LIMIT
        ("halfDeviationLimit", ctypes.wintypes.FLOAT), # HSI_VAL_HALF_DEV_LIMIT
        ("localizerCourse", ctypes.wintypes.FLOAT), # HSI_VAL_LOCALIZER_CRS
        ("airbaseX", ctypes.wintypes.FLOAT), # HSI_VAL_AIRBASE_X
        ("airbaseY", ctypes.wintypes.FLOAT), # HSI_VAL_AIRBASE_Y
        ("totalValues", ctypes.wintypes.FLOAT), # HSI_VAL_TOTAL_VALUES; never set
        ("TrimPitch", ctypes.wintypes.FLOAT), # Value of trim in pitch axis, -0.5 to +0.5
        ("TrimRoll", ctypes.wintypes.FLOAT), # Value of trim in roll axis, -0.5 to +0.5
        ("TrimYaw", ctypes.wintypes.FLOAT), # Value of trim in yaw axis, -0.5 to +0.5
        ("hsiBits", ctypes.wintypes.INT), # HSI flags
        ("DEDLines", (ctypes.c_char * 26) * 5), #25 usable chars
        ("Invert", (ctypes.c_char * 26) * 5), #25 usable chars
        ("PFLLines", (ctypes.c_char * 26) * 5), #25 usable chars
        ("PFLInvert", (ctypes.c_char * 26) * 5), #25 usable chars
        ("UFCTChan", ctypes.wintypes.INT),
        ("AUXTChan", ctypes.wintypes.INT),
        ("RwrObjectCount", ctypes.wintypes.INT),
        ("RWRsymbol", ctypes.wintypes.INT * 40),
        ("bearing", ctypes.wintypes.FLOAT * 40),
        ("missileActivity", ctypes.wintypes.ULONG * 40),
        ("missileLaunch", ctypes.wintypes.ULONG * 40),
        ("selected", ctypes.wintypes.ULONG * 40),
        ("lethality", ctypes.wintypes.FLOAT * 40),
        ("newDetection", ctypes.wintypes.ULONG * 40),
        ("fwd", ctypes.wintypes.FLOAT),
        ("aft", ctypes.wintypes.FLOAT),
        ("total", ctypes.wintypes.FLOAT),
        ("VersionNum", ctypes.wintypes.INT),
        # New values added here for header file compatibility but not implemented
        ("headX", ctypes.wintypes.FLOAT), # Head X offset from design eye (feet)
        ("headY", ctypes.wintypes.FLOAT), # Head Y offset from design eye (feet)
        ("headZ", ctypes.wintypes.FLOAT), # Head Z offset from design eye (feet)
        ("MainPower", ctypes.wintypes.INT),
    )

class FLIGHTDATA2(ctypes.Structure):
    _fields_ = (
        ("nozzlePos2", ctypes.wintypes.FLOAT),
        ("rpm2", ctypes.wintypes.FLOAT),
        ("ftit2", ctypes.wintypes.FLOAT),
        ("oilPressure2", ctypes.wintypes.FLOAT),
        ("navMode", ctypes.wintypes.BYTE),
        ("AAUZ", ctypes.wintypes.FLOAT),
        ("tacanInfo", ctypes.wintypes.CHAR * 2),

        ("AltCalReading", ctypes.wintypes.INT),
        ("altBits", ctypes.wintypes.INT),
        ("powerBits", ctypes.wintypes.INT),
        ("blinkBits", ctypes.wintypes.INT),

        ("cmdsMode", ctypes.wintypes.INT),
        ("BupUhfPreset", ctypes.wintypes.INT),

        ("BupUhfFreq", ctypes.wintypes.INT),
        ("cabinAlt", ctypes.wintypes.FLOAT),
        ("hydPressureA", ctypes.wintypes.FLOAT),
        ("hydPressureB", ctypes.wintypes.FLOAT),
        ("currentTime", ctypes.wintypes.INT),
        ("vehicleACD", ctypes.wintypes.SHORT),
        ("VersionNum", ctypes.wintypes.INT),

        ("fuelFlow2", ctypes.wintypes.FLOAT),

        ("RwrInfo", ctypes.wintypes.CHAR * 512),
        ("lefPos", ctypes.wintypes.FLOAT),
        ("tefPos", ctypes.wintypes.FLOAT),

        ("vtolPos", ctypes.wintypes.FLOAT),

        ("pilotsOnline", ctypes.wintypes.CHAR),
        ("pilotsCallsign", ctypes.wintypes.CHAR * 32 * 12),
        ("pilotsStatus", ctypes.wintypes.CHAR * 32),

        ("bumpIntensity", ctypes.wintypes.FLOAT),

        ("latitude", ctypes.wintypes.FLOAT),
        ("longitude", ctypes.wintypes.FLOAT),

        ("RTT_size", ctypes.wintypes.USHORT * 2),
        ("RTT_area", ctypes.wintypes.USHORT * 7 * 4),

        ("iffBackupMode1Digit1", ctypes.wintypes.CHAR),
        ("iffBackupMode1Digit2", ctypes.wintypes.CHAR),
        ("iffBackupMode3Digit1", ctypes.wintypes.CHAR),
        ("iffBackupMode3Digit2", ctypes.wintypes.CHAR),

        ("instrLight", ctypes.wintypes.CHAR),

        ("bettyBits", ctypes.wintypes.UINT),
        ("miscBits", ctypes.wintypes.UINT),
        ("RALT", ctypes.wintypes.FLOAT),
        ("bingoFuel", ctypes.wintypes.FLOAT),
        ("caraAlow", ctypes.wintypes.FLOAT),
        ("bullseyeX", ctypes.wintypes.FLOAT),
        ("bullseyeY", ctypes.wintypes.FLOAT),
        ("BMSVersionMajor", ctypes.wintypes.INT),
        ("BMSVersionMinor", ctypes.wintypes.INT),
        ("BMSVersionMicro", ctypes.wintypes.INT),
        ("BMSBuildNumber", ctypes.wintypes.INT),
        ("StringAreaSize", ctypes.wintypes.UINT),
        ("StringAreaTime", ctypes.wintypes.UINT),
        ("DrawingAreaSize", ctypes.wintypes.UINT),

        ("turnRate", ctypes.wintypes.FLOAT),
)

class INTELLIVIBEDATA(ctypes.Structure):
    _fields_ = (
        ("AAMissileFired", ctypes.wintypes.BYTE),
        ("AGMissileFired", ctypes.wintypes.BYTE),
        ("BombDropped", ctypes.wintypes.BYTE),
        ("FlareDropped", ctypes.wintypes.BYTE),
        ("ChaffDropped", ctypes.wintypes.BYTE),
        ("BulletsFired", ctypes.wintypes.BYTE),
        ("CollisionCounter", ctypes.wintypes.INT),
        ("IsFiringGun", ctypes.wintypes.BOOLEAN),
        ("IsEndFlight", ctypes.wintypes.BOOLEAN),
        ("IsEjecting", ctypes.wintypes.BOOLEAN),
        ("In3D", ctypes.wintypes.BOOLEAN),
        ("IsPaused", ctypes.wintypes.BOOLEAN),
        ("IsFrozen", ctypes.wintypes.BOOLEAN),
        ("IsOverG", ctypes.wintypes.BOOLEAN),
        ("IsOnGround", ctypes.wintypes.BOOLEAN),
        ("IsExitGame", ctypes.wintypes.BOOLEAN),
        ("Gforce", ctypes.wintypes.FLOAT),
        ("eyex", ctypes.wintypes.FLOAT),
        ("eyey", ctypes.wintypes.FLOAT),
        ("eyez", ctypes.wintypes.FLOAT),
        ("lastdamage", ctypes.wintypes.INT),
        ("damageforce", ctypes.wintypes.FLOAT),
        ("whendamage", ctypes.wintypes.INT)
)

_log = logging.getLogger(__name__)
_pFlightData = None
_pFlightData2 = None
_pIntellivibeData = None
_pOSBData = None

def getFlightData():
    global _pFlightData

    if _pFlightData == None:

        handle = ctypes.windll.kernel32.OpenFileMappingA(FILE_MAP_READ|FILE_MAP_WRITE, False, "FalconSharedMemoryArea".encode())
        if handle:
            ctypes.windll.kernel32.MapViewOfFile.restype = ctypes.POINTER(FLIGHTDATA)
            _pFlightData = ctypes.windll.kernel32.MapViewOfFile(handle, FILE_MAP_READ|FILE_MAP_WRITE, 0, 0, 0)

    if _pFlightData == None:
        raise EnvironmentError("can't access falcon shared memory area")

    return _pFlightData.contents

def getOSBData():
    global _pOSBData

    if _pOSBData == None:

        handle = ctypes.windll.kernel32.OpenFileMappingA(FILE_MAP_READ|FILE_MAP_WRITE, False, "FalconSharedOsbMemoryArea".encode())
        if handle:
            ctypes.windll.kernel32.MapViewOfFile.restype = ctypes.POINTER(OSBDATA)
            _pOSBData = ctypes.windll.kernel32.MapViewOfFile(handle, FILE_MAP_READ|FILE_MAP_WRITE, 0, 0, 0)

    if not _pOSBData:
        raise EnvironmentError("can't access falcon shared memory area")

    return _pOSBData.contents

def getFlightData2():
    global _pFlightData2

    if _pFlightData2 == None:

        handle = ctypes.windll.kernel32.OpenFileMappingA(FILE_MAP_READ|FILE_MAP_WRITE, False, "FalconSharedMemoryArea2".encode())
        if handle:
            ctypes.windll.kernel32.MapViewOfFile.restype = ctypes.POINTER(FLIGHTDATA2)
            _pFlightData2 = ctypes.windll.kernel32.MapViewOfFile(handle, FILE_MAP_READ|FILE_MAP_WRITE, 0, 0, 0)

    if not _pFlightData2:
        raise EnvironmentError("can't access falcon shared memory area")

    return _pFlightData2.contents

def getIntellivibeData():
    global _pIntellivibeData

    if _pIntellivibeData == None:

        handle = ctypes.windll.kernel32.OpenFileMappingA(FILE_MAP_READ|FILE_MAP_WRITE, False, "FalconIntellivibeSharedMemoryArea".encode())
        if handle:
            ctypes.windll.kernel32.MapViewOfFile.restype = ctypes.POINTER(INTELLIVIBEDATA)
            _pIntellivibeData = ctypes.windll.kernel32.MapViewOfFile(handle, FILE_MAP_READ|FILE_MAP_WRITE, 0, 0, 0)

    if not _pIntellivibeData:
        raise EnvironmentError("can't access falcon shared memory area")

    return _pIntellivibeData.contents

def init():
    pass

init()
