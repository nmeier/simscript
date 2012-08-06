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
import joysticks, phidgets, state, log

vjoy = joysticks.get('vJoy Device')

# encoder 1 for axis and button
encoder1 = phidgets.get(82141)
SimRadarElevation = phidgets.encoder2axis(encoder1, 2)
vjoy.setAxis(0, SimRadarElevation)
vjoy.setButton(0, encoder1.getInputState(0))

# encoder 2 for axis and button
encoder2 = phidgets.get(82081)
SimStepMissileVolume = phidgets.encoder2axis(encoder2, 1)
SimToggleMissileCage = encoder2.getInputState(0)
vjoy.setAxis(1, SimStepMissileVolume)
vjoy.setButton(1, SimToggleMissileCage)

# saitek axis 2 into 2 buttons
saitek = joysticks.get('Saitek Pro Flight Quadrant')
speedbrake = saitek.getAxis(1)
retract = speedbrake < -0.5
extend = speedbrake >  0.5
if state.set("sbe", extend) != extend and extend:
    log.info("extending speed brakes")
if state.set("sbr", retract) != retract and retract:
    log.info("retracting speed brakes")
vjoy.setButton(2, extend)
vjoy.setButton(3, retract)


# saitek axis 3 into 2 buttons
handleDown = saitek.getAxis(2) > 0
if handleDown: # let's not accidentially retract gear unless we've seen handle down first
    state.set("gear-seen-down", True)
handleUp = not handleDown and state.get("gear-seen-down")
if state.set("gear", handleUp) != handleUp:
    log.info("Gear handle %s", ("down" if handleDown else "up"))
vjoy.setButton(4, handleUp)
vjoy.setButton(5, handleDown)

