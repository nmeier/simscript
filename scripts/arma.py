import mouse, log, state, keyboard
from time import clock

# Mouse wheel left/right for teamspeak PTT/freetrack reset
PTT_EFFECTIVE_SECONDS = 1
TEAMSPEAK_KEY = 'CONTROL SHIFT ALT T'
    
wheel = mouse.getMouseHWheel()

if wheel<0:
    if not state.set("PTT", clock()):
        log.info("start transmitting")
        keyboard.press(TEAMSPEAK_KEY)
else:
    lastxmit = state.get("PTT", None)
    if  lastxmit and lastxmit < clock()-PTT_EFFECTIVE_SECONDS:
        log.info("stop transmitting")
        state.set("PTT", None)
        keyboard.release(TEAMSPEAK_KEY)
