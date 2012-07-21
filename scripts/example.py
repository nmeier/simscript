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
import joysticks, phidgets, state

def pos2axis(key, pos, ticks=80):
    left, right = state.get(key, (pos, pos+ticks))
    if pos>right:
        left,right = pos-ticks,pos
    elif pos<left:
        left,right = pos,pos+ticks
    state.set(key, (left,right))
    return (pos-left) / (right-left) * 2 - 1

# encoder 1 for axis and button
encoder1 = phidgets.get(82141)
vjoy = joysticks.get('vJoy Device')
vjoy.setAxis(0, pos2axis("leftright", -encoder1.getPosition(0), 160))
vjoy.setButton(0, encoder1.getInputState(0))

# encoder 2 for axis and button
encoder2 = phidgets.get(82081)
vjoy.setAxis(1, pos2axis("updown", -encoder2.getPosition(0), 160))
vjoy.setButton(1, encoder2.getInputState(0))

# saitek axis 3 into 2 buttons
saitek = joysticks.get('Saitek Pro Flight Quadrant')
vjoy.setButton(2, saitek.getAxis(2) < 0)
vjoy.setButton(3, saitek.getAxis(2) > 0)
