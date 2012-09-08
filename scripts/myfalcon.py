# 
# My setup consists of:
#
#  CH Combatstick USB
#   Map zoom toggle button into FOV axis w/two positions
#   Map push button into Teamspeak PTT
#   Map shifted toggle button into Freetrack Reset
#  Saitek Thottle Quadrant
#   Split 2nd Axis into 2 Buttons (Speedbrake Extend/Retract)
#   Split 3rd Axis into 2 Buttons (Gear Up/Down)
#  Phidget Encoder 1
#   Map Push Button into Button
#   Map Rotation into Axis (Radar Elevation)
#  Phidget Encoder 2
#   Map Push Button into Button (Missile Uncage)
#   Map Rotation into Axis (Missile Acquisition Sound Level)
#
import joysticks, phidgets, state, log, keyboard

vjoy = joysticks.get('vJoy Device')
combatstick = joysticks.get("CH Combatstick USB")
shift = combatstick.getButton(3)

# combatstick button for zoom axis toggle
ZOOM_MIN = 1.0
ZOOM_MAX = 0.35
ZOOM_AXIS = 2
axis = phidgets.Axis(phidgets.get(82141))
zoomedout = state.get("zoomedout")
if state.toggle("zoom-toggle", combatstick.getButton(2) and not shift) or zoomedout == None:
    log.info("zoom in" if zoomedout else "zoom out")
    zoom = ZOOM_MAX if zoomedout else ZOOM_MIN
    axis.setPosition(zoom)
    state.set("zoomedout", not zoomedout)
else:
    zoom = axis.getPosition()
vjoy.setAxis(ZOOM_AXIS, zoom)

# combatstick shifted button for Freetrack reset
FREETRACK_KEY = "CONTROL SHIFT ALT F"
if state.toggle("freetrack-toggle", combatstick.getButton(2) and shift):
    keyboard.click(FREETRACK_KEY)

# combatstick button for Teamspeak PTT
TEAMSPEAK_KEY = 'CONTROL SHIFT ALT T'
ptt = combatstick.getButton(4)
optt = state.set("ptt", ptt)
if ptt != optt and not shift:
    if ptt: keyboard.press(TEAMSPEAK_KEY)
    else: keyboard.release(TEAMSPEAK_KEY)

# encoder 2 for axis (one rotation) and button 
ENCODER_2_AXIS = 1
ENCODER_2_BUTTON = 1

encoder = phidgets.get(82081)
vjoy.setAxis(ENCODER_2_AXIS, phidgets.Axis(encoder).getPosition())
vjoy.setButton(ENCODER_2_BUTTON, encoder.getInputState(0))

print(phidgets.delta(encoder))

# saitek axis 2 into 2 buttons (AFBrakesOut/AFBrakesIn)
AIRBREAK_OUT_BUTTON = 2
AIRBREAK_IN_BUTTON = 3

saitek = joysticks.get('Saitek Pro Flight Quadrant')
speedbrake = saitek.getAxis(1)
retract = speedbrake < -0.5
extend = speedbrake > 0.5
if state.set("sbe", extend) != extend and extend:
    log.info("extending speed brakes")
if state.set("sbr", retract) != retract and retract:
    log.info("retracting speed brakes")
vjoy.setButton(AIRBREAK_OUT_BUTTON, extend)
vjoy.setButton(AIRBREAK_IN_BUTTON, retract)


# saitek axis 3 into 2 buttons (AFGearUp, AFGearDown)
GEAR_UP_BUTTON = 4
GEAR_DOWN_BUTTON = 5

handleDown = saitek.getAxis(2) > 0.25
if handleDown: # let's not accidentially retract gear unless we've seen handle down first
    state.set("gear-seen-down", True)
handleUp = saitek.getAxis(2) < -0.25 and state.get("gear-seen-down")
gear = (handleUp,handleDown)
if state.set("gear", gear) != gear:
    log.info("Gear handle up=%s, down=%s" % (handleUp, handleDown))
vjoy.setButton(GEAR_UP_BUTTON, handleUp)
vjoy.setButton(GEAR_DOWN_BUTTON, handleDown)



