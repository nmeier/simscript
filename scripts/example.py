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
import joysticks, phidgets

# encoder 1 for axis and button
encoder1 = phidgets.get(82141)
vjoy = joysticks.get('vJoy Device')
vjoy.setAxis(0, phidgets.encoder2axis(encoder1, 2))
vjoy.setButton(0, encoder1.getInputState(0))

# encoder 2 for axis and button
encoder2 = phidgets.get(82081)
vjoy.setAxis(1, phidgets.encoder2axis(encoder2, 1))
vjoy.setButton(1, encoder2.getInputState(0))

# saitek axis 3 into 2 buttons
saitek = joysticks.get('Saitek Pro Flight Quadrant')
vjoy.setButton(2, saitek.getAxis(2) < 0)
vjoy.setButton(3, saitek.getAxis(2) > 0)
