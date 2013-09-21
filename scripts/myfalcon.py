# 
# My setup consists of:
#
#  CH Combatstick USB
#   Map zoom toggle button #3 into FOV axis w/two positions (long press for Freetrack Reset)
#   Map push button #3 into Teamspeak PTT
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
import joysticks, phidgets, state, log, keyboard, falcon, time, mouse

# Throttle Quadrant
CURSOR_WE_AXIS_OUT = 0
CURSOR_NS_AXIS_OUT = 1
GEAR_AXIS_IN = 2
RADAR_ELEVATION_AXIS_OUT = 3
RANGE_AXIS_OUT = 4
MSL_VOLUME_AXIS_OUT = 5

CMS_BUTTON_IN = 1
CMS_FORWARD_BUTTON_OUT = 8
CMS_RIGHT_BUTTON_OUT = 9
CMS_DOWN_BUTTON_OUT = 10
CMS_DOWNRIGHT_HOLD_SECONDS = 0.25

MSL_UNCAGE_BUTTON_OUT = 1

AIRBREAK_AXIS_IN = 1 # in
AIRBREAK_EXTEND_BUTTON_OUT = 2
AIRBREAK_RETRACT_BUTTON_OUT = 3
ZOOM_BUTTON_IN = 2 # in
ZOOM_AXIS_OUT = 2
GEAR_UP_BUTTON_OUT = 4
GEAR_DOWN_BUTTON_OUT = 5
OVERRIDE_UP_BUTTON_IN = 0 # in
OVERRIDE_DOWN_BUTTON_IN = 1 # in
OVERRIDE_MRM_BUTTON_OUT = 6
OVERRIDE_DOG_BUTTON_OUT = 7
OVERRIDE_HOLD_SECONDS = 0.1

# sticks
vjoy = joysticks.get('vJoy Device')
combatstick = joysticks.get("CH Combatstick USB")
pedals = joysticks.get('CH Pro Pedals USB')
throttle = joysticks.get('Saitek Pro Flight Quadrant')

# combatstick button long press for CMS down/right toggle and CMS forward
cms = combatstick.getButton(CMS_BUTTON_IN)
if state.toggle("cms-downright", cms, CMS_DOWNRIGHT_HOLD_SECONDS):
    cmsdown = state.get("cms-down", False)
    vjoy.setButton(CMS_DOWN_BUTTON_OUT, not cmsdown)
    vjoy.setButton(CMS_RIGHT_BUTTON_OUT, cmsdown)
    state.set("cms-down", not cmsdown)
    vjoy.setButton(CMS_FORWARD_BUTTON_OUT, False)
    state.set("cms-up", True)   # fake toggle cms forward
else:
    vjoy.setButton(CMS_RIGHT_BUTTON_OUT, False)
    vjoy.setButton(CMS_DOWN_BUTTON_OUT, False)
    if not state.get("cms-downright"):
        vjoy.setButton(CMS_FORWARD_BUTTON_OUT, state.toggle("cms-up", not cms))   

# combatstick button for zoom axis toggle and right pedal for custom zoom
FREETRACK_KEY = "CONTROL SHIFT ALT F"
ZOOMED_OUT = 1.0
ZOOM_IN = 0.50

zoomButton = combatstick.getButton(ZOOM_BUTTON_IN)
zoom = state.get("zoom")
if state.toggle("zoom-toggle", zoomButton) or zoom == None:
    log.info("zoom in" if zoom==ZOOMED_OUT else "zoom out")
    zoom = ZOOM_IN if zoom==ZOOMED_OUT else ZOOMED_OUT
    state.set("zoom", zoom)


zoom = zoom - (pedals.getAxis(1,0.1)+1)/2    
try:
    flightData = falcon.getFlightData()
    if flightData.gearPos and flightData.vt>0: # might be taxiing w/brakes
        zoom = state.get("zoom")
    
    # if we're in Falcon we assume left handed mouse
    mouse.swapMouseButtons()
except:
    pass
    
zoomHistory = state.get("zoom-history", [])
zoomHistory.append(zoom)
if len(zoomHistory)>10:
    zoomHistory.pop(0)
vjoy.setAxis(ZOOM_AXIS_OUT, sum(zoomHistory)/len(zoomHistory))

# combatstick zoom axis button long press for Freetrack reset
if state.toggle("freetrack-reset", zoomButton, 1):
    log.info("reset freetrack")
    keyboard.click(FREETRACK_KEY)

# combatstick button for Teamspeak PTT
TEAMSPEAK_KEY = 'CONTROL SHIFT ALT T'
pttButton = combatstick.getButton(3)
if pttButton != state.set("pttButton", pttButton):
    log.info("PTT %d" % pttButton)
    if pttButton: keyboard.press(TEAMSPEAK_KEY)
    else: keyboard.release(TEAMSPEAK_KEY)

# encoder 1 for two axis parallel output 
encoder = phidgets.get(82141)

vjoy.setAxis(RADAR_ELEVATION_AXIS_OUT, -phidgets.getAxis(encoder, "radar-elevation", 3, 0.0))
vjoy.setAxis(RANGE_AXIS_OUT, phidgets.getAxis(encoder, "range", 1, 0.0))
    
# encoder 2 for axis and button 
encoder = phidgets.get(82081)

vjoy.setAxis(MSL_VOLUME_AXIS_OUT, phidgets.getAxis(encoder, "msl-volume", 1, 1.0))
vjoy.setButton(MSL_UNCAGE_BUTTON_OUT, encoder.getInputState(0))


# encoder 1 for hsi hdg/course inc/dec
# Note: the only way to click hdg/crs up or down is to send multiple subsequent keyboard presses
#       for each respective gauge modifier (-/+)1, (-/+)5 respectively. By sending only one 
#       keystroke per sync the call doesn't take too long and it stays responsive while remembering
#       remaining delta.  
#tuner = phidgets.get(82141)
#dial = 'hdg' if not tuner.getInputState(0) else 'crs'
#delta = phidgets.delta(tuner, 45) + state.get(dial, 0)
#if delta!=0:
#    if delta>=5: inc = 5
#    elif delta>=1: inc = 1
#    elif delta>-5: inc = -1
#    else: inc = -5
#    delta -= inc
#    keys = { "hdg-1":"CTRL ALT V", "hdg+1":"CTRL ALT B", "hdg-5":"SHIFT ALT V", "hdg+5":"SHIFT ALT B" ,
#             "crs-1":"CTRL ALT N", "crs+1":"CTRL ALT M", "crs-5":"SHIFT ALT N", "crs+5":"SHIFT ALT M" }
#    keyboard.click( keys[ "%s%+d" % (dial,inc) ]  )
#state.set(dial, delta) # remaining
    
# saitek axis 2 into 2 buttons (AFBrakesOut/AFBrakesIn)
saitek = joysticks.get('Saitek Pro Flight Quadrant')
speedbrake = saitek.getAxis(AIRBREAK_AXIS_IN)
retract = speedbrake < -0.5
extend = speedbrake > 0.5
if state.toggle("sbe", extend):
    log.info("extending speed brakes")
if state.toggle("sbr", retract):
    log.info("retracting speed brakes")
vjoy.setButton(AIRBREAK_EXTEND_BUTTON_OUT, extend)
vjoy.setButton(AIRBREAK_RETRACT_BUTTON_OUT, retract)


# saitek axis 3 into 2 buttons (AFGearUp, AFGearDown)
handle = saitek.getAxis(GEAR_AXIS_IN)
handleDown = handle > 0.25
handleUp = handle < -0.25
if state.toggle("gear-down", handleDown):
    log.info("gear handle down")
if state.toggle("gear-up", handleUp):
    log.info("gear handle up")
vjoy.setButton(GEAR_DOWN_BUTTON_OUT, handleDown)
vjoy.setButton(GEAR_UP_BUTTON_OUT, handleUp)

# Missile/Dogfight override for
#    g_bHotasDgftSelfCancel 1  // SRM and MRM override callbacks call the override cancel callback when depressed
override = state.get("override", 0)
if override>=0 and state.toggle("override-up", throttle.getButton(OVERRIDE_UP_BUTTON_IN), OVERRIDE_HOLD_SECONDS):
    override -= 1
if override<=0 and state.toggle("override-down", throttle.getButton(OVERRIDE_DOWN_BUTTON_IN), OVERRIDE_HOLD_SECONDS):
    override += 1
if override != state.set("override", override):
    log.info("Override %d" % override)
vjoy.setButton(OVERRIDE_MRM_BUTTON_OUT, override<0)
vjoy.setButton(OVERRIDE_DOG_BUTTON_OUT, override>0)

# hat for radar cursor (supporting diagonals)
hat = combatstick.getHat(0)
was = state.set("radar-hat", hat)
if not hat:
    delta = 0.1
else:
    delta = min(1, state.get("radar-delta", 0) + 0.05)
state.set("radar-delta", delta)
vjoy.setAxis(CURSOR_WE_AXIS_OUT,  bool(hat&joysticks.HAT_W)*-delta + bool(hat&joysticks.HAT_E)*delta )
vjoy.setAxis(CURSOR_NS_AXIS_OUT,  bool(hat&joysticks.HAT_N)*delta + bool(hat&joysticks.HAT_S)*-delta )

