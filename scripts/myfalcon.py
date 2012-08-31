# 
# My setup consists of:
#
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

# combatstick button for zoom axis toggle
shift = combatstick.getButton(3)

ZOOM_MIN = 1
ZOOM_MAX = 0.35
ZOOM_AXIS = 2
zoomedout = state.get("zoomedout")
if state.toggle("zoom-toggle", combatstick.getButton(2) and not shift) or zoomedout == None:
    log.info("zoom in" if zoomedout else "zoom out")
    vjoy.setAxis(ZOOM_AXIS, ZOOM_MAX if zoomedout else ZOOM_MIN)
    state.set("zoomedout", not zoomedout)

# combatstick shifted button for Freetrack reset
FREETRACK_KEY = "CTRL SHIFT ALT F"
if state.toggle("freetrack-toggle", combatstick.getButton(2) and shift):
    keyboard.click(FREETRACK_KEY)

# combatstick button for Teamspeak PTT
TEAMSPEAK_KEY = '~'
ptt = combatstick.getButton(4)
optt = state.set("ptt", ptt)
if ptt!=optt and not shift:
    if ptt: keyboard.press(TEAMSPEAK_KEY)
    else: keyboard.release(TEAMSPEAK_KEY)

# encoder 1 for axis (two rotations) and button
ENCODER_1_AXIS = 0
ENCODER_1_BUTTON = 0
encoder1 = phidgets.get(82141)
axisFromEncoder1 = phidgets.encoder2axis(encoder1, 2)
buttonFromEncoder1 = encoder1.getInputState(0)
vjoy.setAxis(ENCODER_1_AXIS, axisFromEncoder1)
vjoy.setButton(ENCODER_1_BUTTON, buttonFromEncoder1)

# encoder 2 for axis (one rotation) and button 
ENCODER_2_AXIS = 1
ENCODER_2_BUTTON = 1

encoder2 = phidgets.get(82081)
axisFromEncoder2 = phidgets.encoder2axis(encoder2, 1)
buttonFromEncoder2 = encoder2.getInputState(0)
vjoy.setAxis(ENCODER_2_AXIS, axisFromEncoder2)
vjoy.setButton(ENCODER_2_BUTTON, buttonFromEncoder2)

# saitek axis 2 into 2 buttons (AFBrakesOut/AFBrakesIn)
AIRBREAK_OUT_BUTTON = 2
AIRBREAK_IN_BUTTON = 3

saitek = joysticks.get('Saitek Pro Flight Quadrant')
speedbrake = saitek.getAxis(1)
retract = speedbrake < -0.5
extend = speedbrake >  0.5
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
if state.set("gear", handleUp) != handleUp:
    log.info("Gear handle %s", ("down" if handleDown else "up"))
vjoy.setButton(GEAR_UP_BUTTON, handleUp)
vjoy.setButton(GEAR_DOWN_BUTTON, handleDown)



