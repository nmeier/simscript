'''
Diagnoses available simulator input and outputs 
'''
import joysticks,state,log,phidgets

# debug joysticks
for j in range(0, joysticks.numJoysticks()) :
    
    joy = joysticks.get(j)
    
    for b in range(0, joy.numButtons()) :
        key = "joysticks.get('%s').button(%d)" % (joy.name, b)
        now = joy.getButton(b)
        was = state.set(key, now)
        if now and not was:
            log.info("joystick button pressed - %s = True" % (key))

    for a in range(0, joy.numAxis()) :
        key = "joysticks.get('%s').axis(%d)" % (joy.name, a)
        now = joy.getAxis(a)
        was = state.get(key, 0)
        if abs(was-now) > 0.1 :
            log.info("joystick axis moved - %s = %.1f" % (key, now) )
            state.set(key, now)

# debug phidgets 
for p in phidgets.all():
    
    if not p.isAttached(): continue
    
    dtype = p.getDeviceType().decode("utf-8") 
    
    # encoder
    if dtype == 'PhidgetEncoder':
        
        key = "phidgets.get('%s').getInputState(0)" % p.getSerialNum()
        now = p.getInputState(0)
        was = state.set(key, now)
        if now and not was:
            log.info("Encoder pushed - %s = %s" % (key, now) )

        key = "phidgets.get('%s').getPosition(0)" % p.getSerialNum()
        now = p.getPosition(0)
        was = state.set(key, now)
        if was != now:
            log.info("Encoder rotated - %s = %s" % (key, now) )

        
    # more phidget devices we can debug log?
    
    
