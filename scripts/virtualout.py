'''
Sample script that drives a virtual joystick
'''
import joysticks,math,state

vjoy = joysticks.get("vJoy Device")

# counter
loop = state.inc("loop")

# rotate all axis
for a in range(0,vjoy.numAxis()): 
    vjoy.setAxis(a,math.sin(loop/10 + a * math.pi/8))

# go through buttons
for b in range(0,vjoy.numButtons()):
    vjoy.setButton(b, False)
vjoy.setButton(int(loop/10 % vjoy.numButtons()), True)    

