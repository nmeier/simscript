'''
Diagnoses available simulator input and outputs 
'''

# debug joysticks
if not state.joys: state.joys = {}

for j in range(0, joysticks.numJoysticks()) :
    
    joy = joysticks.get(j)
    
    for b in range(0, joy.numButtons()) :
        key = "joysticks.get('%s').button(%d)" % (joy.name, b)
        now = joy.getButton(b)
        was = state.joys.get(key, False)
        if now and not was:
            log.info("joystick button pressed - %s = True" % (key))
        state.joys[key] = now

    for a in range(0, joy.numAxis()) :
        key = "joysticks.get('%s').axis(%d)" % (joy.name, a)
        now = joy.getAxis(a)
        was = state.joys.get(key, 0)
        if abs(was-now) > 0.1 :
            log.info("joystick axis moved - %s = %.1f" % (key, now) )
            state.joys[key] = now

# debug phidgets 
if not state.phidgets: state.phidgets = {}

for p in phidgets.all():
    
    if not p.isAttached(): continue
    
    dtype = p.getDeviceType() 
    
    # encoder
    if dtype == 'PhidgetEncoder':
        
        key = "phidgets.get('%s').getInputState(0)" % p.getSerialNum()
        now = p.getInputState(0)
        was = state.phidgets.get(key, False)
        if (now and not was):
            log.info("Encoder pushed - %s = %s" % (key, now) )
        state.phidgets[key] = now

        key = "phidgets.get('%s').getPosition(0)" % p.getSerialNum()
        now = p.getPosition(0)
        was = state.phidgets.get(key)
        if was != now:
            log.info("Encoder rotated - %s = %s" % (key, now) )
        state.phidgets[key] = now

        
    # more phidget devices we can debug log?
    
    
