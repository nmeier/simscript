# 
# My setup consists of:
#
#  Saitek Thottle Quadrant
#   Map 3rd Axis to 2 Buttons (Gear Up/Down)
#  Phidget Encoder 1
#   Use Push Button as shift
#   Map Rotation to 2 Step Buttons (Radar Range increase/decrease)
#   Map Shifted Rotation to Axis (Radar Elevation)
#  Phidget Encoder 2
#   Map Push Button (Missile Uncage)
#   Map Rotation to Axis (Missile Acquisition Sound Level)
#

vjoy = joysticks.get("vJoy Device")

vjoy.setAxis(0,16000)
vjoy.setButton(0,True)
