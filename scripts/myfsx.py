import state, log, keyboard, joysticks, fsx

saitek = joysticks.get('Saitek Pro Flight Quadrant')

# saitex 1 button for gear toggle
if state.toggle("gear", saitek.getButton(0)):
    log.info("Toggling gear")
    keyboard.click(keyboard.VK_G) # press/release virtual key code 
    
# saitek 1 button for PTT while pressed
ptt = state.toggle("PTT", saitek.getButton(1)) 
if ptt == None:
    pass # ignore no change
if ptt == True:
    log.info("PTT on")
    keyboard.press(keyboard.VK_SHIFT) # press virtual key code
    keyboard.press(keyboard.VK_T)
if ptt == False:
    log.info("PTT off")
    keyboard.release("shift t") # release keys (1. T, 2. Shift) 

# report COM active frequency
freq = fsx.get("COM ACTIVE FREQUENCY:1","Frequency BCD16", lambda x: x)
if state.set("freq", freq) != freq:
    log.info("Current frequency %s" % freq)

