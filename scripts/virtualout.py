'''
Sample script that drives a virtual joystick
'''
vjoy = joysticks.get("vJoy Device")

# counter
try: state.loop += 1
except: state.loop = 0

# rotate all axis
for a in range(0,vjoy.numAxis()):
    vjoy.setAxis(a,math.sin(state.loop/10 + a * math.pi/8))

# go through buttons
for b in range(0,vjoy.numButtons()):
    vjoy.setButton(b, False)
vjoy.setButton(int(state.loop/10 % vjoy.numButtons()), True)    
