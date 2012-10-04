import state, log, joysticks, fsx, phidgets

saitek = joysticks.get('Saitek Pro Flight Quadrant')

# Saitek axis 2 into gear handle operation
#
# variable - see http://msdn.microsoft.com/en-us/library/cc526981.aspx#AircraftLandingGearData
#  | GEAR HANDLE POSITION | True if gear handle is applied | Bool | Y | All aircraft |
#
# event - see http://msdn.microsoft.com/en-us/library/cc526980.aspx#AircraftMiscellaneousSystemsIDs
#  | GEAR_SET             | Sets gear handle position up/down (0,1) | All aircraft
#
gearup = state.toggle("gearup", saitek.getAxis(1) < 0)
if gearup is None:
    pass # ignore no change in handle
elif gearup:
    log.info("Moving gear handle up!")
    fsx.set("GEAR HANDLE POSITION", "Bool", 0)  # uset settable variable approach
else:
    log.info("Moving gear handle down!")
    fsx.send("GEAR_SET", 1) # use send (key) event

handle = fsx.get("GEAR HANDLE POSITION", "Bool", bool)
if state.set("handle", handle) != handle:
    log.info("Current gear handle IS %s" % ("down" if handle else "up"))
    
#
# phidget 1&2 for increasing COM active frequency 
#
# events - see http://msdn.microsoft.com/en-us/library/cc526981.aspx#Frequency
#  | KEY_COM_RADIO_WHOLE_DEC | COM_RADIO_WHOLE_DEC | Decrements COM by one MHz | All aircraft |
#  | KEY_COM_RADIO_WHOLE_INC | COM_RADIO_WHOLE_INC | Increments COM by one MHz | All aircraft |
#  | KEY_COM_RADIO_FRACT_DEC | COM_RADIO_FRACT_DEC | Decrements COM by 25 KHz  | All aircraft |
#  | KEY_COM_RADIO_FRACT_INC | COM_RADIO_FRACT_INC | Increments COM by 25 KHz  | All aircraft |
#  | KEY_COM_RADIO_SWAP      | COM_STBY_RADIO_SWAP | Swaps COM 1 freq/standby  | All aircraft | 
#
encoder1 = phidgets.get(82141)
delta = phidgets.getDelta(encoder1)
for i in range(0,abs(delta)):
    fsx.send("COM_RADIO_WHOLE_INC" if delta>0 else "COM_RADIO_WHOLE_DEC")

encoder2 = phidgets.get(82081)
delta = phidgets.getDelta(encoder2)
for i in range(0,abs(delta)):
    fsx.send("COM_RADIO_FRACT_INC" if delta>0 else "COM_RADIO_FRACT_DEC")

if state.toggle("swap_radio", encoder1.getInputState(0)):
    fsx.send("COM_STBY_RADIO_SWAP")

#
# Report current frequency
#
# variable - 
#  | COM | ACTIVE FREQUENCY:index | Com frequency. Index is 1 or 2 | Frequency | BCD16 | N | All aircraft |
freq = fsx.get("COM ACTIVE FREQUENCY:1","Frequency BCD16", fsx.bcd2khz)
if state.set("freq", freq) != freq:
    log.info("Current frequency %s" % freq)

