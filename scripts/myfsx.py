import state, log, joysticks, fsx, phidgets

saitek = joysticks.get('Saitek Pro Flight Quadrant')

# Saitek axis 3 into gear handle operation
#
# GEAR HANDLE POSITION | True if gear handle is applied | Bool | Y | All aircraft
#
# see http://msdn.microsoft.com/en-us/library/cc526981.aspx#AircraftLandingGearData
#  | GEAR HANDLE POSITION | True if gear handle is applied | Bool | Y | All aircraft |
#
gearup = state.toggle("gearup", saitek.getAxis(2) < 0)
if gearup is None:
    pass # ignore no change in handle
elif gearup:
    log.info("Moving gear handle up!")
    fsx.set("GEAR HANDLE POSITION", 0)
else:
    log.info("Moving gear handle down!")
    fsx.set("GEAR HANDLE POSITION", 1)

handle = fsx.get("GEAR HANDLE POSITION", "Bool", bool)
if state.set("handle", handle) != handle:
    log.info("Current gear handle IS %d" % "down" if handle else "up")

#
# phidget 1&2 for increasing COM active frequency 
#
# see http://msdn.microsoft.com/en-us/library/cc526981.aspx#Frequency
#  | KEY_COM_RADIO_WHOLE_DEC | COM_RADIO_WHOLE_DEC | Decrements COM by one MHz | All aircraft |
#  | KEY_COM_RADIO_WHOLE_INC | COM_RADIO_WHOLE_INC | Increments COM by one MHz | All aircraft |
#  | KEY_COM_RADIO_FRACT_DEC | COM_RADIO_FRACT_DEC | Decrements COM by 25 KHz  | All aircraft |
#  | KEY_COM_RADIO_FRACT_INC | COM_RADIO_FRACT_INC | Increments COM by 25 KHz  | All aircraft |
#
encoder1 = phidgets.get(82141)
increments = phidgets.encoder2increment(encoder1)
for i in range(0,abs(increments)):
    fsx.set("COM_RADIO_WHOLE_INC" if increments>0 else "COM_RADIO_WHOLE_DEC")

encoder2 = phidgets.get(82081)
increments = phidgets.encoder2increment(encoder2)
for i in range(0,abs(increments)):
    fsx.set("COM_RADIO_FRACT_INC" if increments>0 else "COM_RADIO_FRACT_DEC")

#
# Report current frequency
#
# | COM | ACTIVE FREQUENCY:index | Com frequency. Index is 1 or 2 | Frequency | BCD16 | N | All aircraft |
freq = fsx.get("COM ACTIVE FREQUENCY:1","Frequency BCD16", fsx.bcd2khz)
if state.set("freq", freq) != freq:
    log.info("Current frequency %s" % freq)


