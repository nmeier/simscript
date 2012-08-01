# 
# My setup consists of:
#
#  Saitek Thottle Quadrant
#   Split 3rd Axis into 2 Buttons (Gear Up/Down)
#  Phidget Encoder 1
#   Map Push Button into Button
#   Map Rotation into Axis (Radar Elevation)
#  Phidget Encoder 2
#   Map Push Button into Button (Missile Uncage)
#   Map Rotation into Axis (Missile Acquisition Sound Level)
#
import joysticks, phidgets, state, keyboard, log

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

# saitek axis 3 into 2 buttons
saitek = joysticks.get('Saitek Pro Flight Quadrant')
gearUp = saitek.getAxis(2) < 0
if gearUp:
    state.set("gear-seen-up", True)
gearDown = not gearUp and state.get("gear-seen-up")
vjoy.setButton(2, gearUp)
vjoy.setButton(3, gearDown)

