import mouse, log, state, keyboard

# Mouse wheel left/right for teamspeak PTT/freetrack reset
PTT_TTL = 0.5
TEAMSPEAK_KEY = 'CONTROL SHIFT ALT T'
    
ptt = state.lock("PTT", mouse.getHWheel()<0, PTT_TTL)
if ptt==True:
    log.info("start transmitting")
    keyboard.press(TEAMSPEAK_KEY)
if ptt==False:
    log.info("stop transmitting")
    keyboard.release(TEAMSPEAK_KEY)
