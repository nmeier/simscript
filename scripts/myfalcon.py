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
import joysticks, phidgets, state, log, keyboard, falcon

vjoy = joysticks.get('vJoy Device')
combatstick = joysticks.get("CH Combatstick USB")
pedals = joysticks.get('CH Pro Pedals USB')

shift = combatstick.getButton(3)

# combatstick button for zoom axis toggle
ZOOM_MIN = 1.0
ZOOM_MAX = 0.35
ZOOM_AXIS = 2
zoomedout = state.get("zoomedout")
if state.toggle("zoom-toggle", combatstick.getButton(2) and not shift) or zoomedout == None:
    log.info("zoom in" if zoomedout else "zoom out")
    zoomedout = not zoomedout
    state.set("zoomedout", zoomedout)

if zoomedout:
    zoom = ZOOM_MIN
else: # pedals right for zoom past ZOOM_MAX
    zoom = ZOOM_MAX - (pedals.getAxis(1,0.25)+1)/2
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

# encoder 1 for hsi hdg/course inc/dec
# Note: atm the only way to click hdg/crs up or down is to send multiple subsequent keyboard presses
#       for each respective gauge modifier (-/+)1, (-/+)5 respectively
#       I'm keeping track of the desired delta from encoder rotation and send only one keystroke per
#       sync making sure that the call doesn't take too long and that (c)cw rotation stops fast if
#       changing direction. Keys for 1/5 increment allow for two speeds to catch up.  
tuner = phidgets.get(82141)
dial = 'hdg' if not tuner.getInputState(0) else 'crs'
delta = phidgets.delta(tuner, 45) + state.get(dial, 0)
if delta!=0:
    if delta>=5: inc = 5
    elif delta>=1: inc = 1
    elif delta>-5: inc = -1
    else: inc = -5
    delta -= inc
    keys = { "hdg-1":"CTRL ALT V", "hdg+1":"CTRL ALT B", "hdg-5":"SHIFT ALT V", "hdg+5":"SHIFT ALT B" ,
             "crs-1":"CTRL ALT N", "crs+1":"CTRL ALT M", "crs-5":"SHIFT ALT N", "crs+5":"SHIFT ALT M" }
    keyboard.click( keys[ "%s%+d" % (dial,inc) ]  )
state.set(dial, delta) # remaining
    

# encoder 2 for axis (one rotation) and button 
ENCODER_2_AXIS = 1
ENCODER_2_BUTTON = 1

encoder = phidgets.get(82081)
vjoy.setAxis(ENCODER_2_AXIS, phidgets.Axis(encoder).getPosition())
vjoy.setButton(ENCODER_2_BUTTON, encoder.getInputState(0))

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



