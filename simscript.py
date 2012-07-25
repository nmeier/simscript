#!/usr/bin/env python

""" simscript main - automation of virtual inputs for simulators """

import sys,os,time,logging,traceback,getopt

def classbyname(name):
    parts = name.split('.')
    m = __import__(".".join(parts[:-1]))
    for p in parts[1:]:
        m = getattr(m, p)            
    return m

def modulo(value,start,end):
    if value!=value: #NaN check
        return value
    value = (value - start) % (end-start)
    value = start+value if value>=0 else end+value
    return value

class Script():
    def __init__(self, name):
        self.name = name if not name.endswith('.py') else name[:-3]
        self.file = os.path.join(os.path.abspath("scripts"), self.name+'.py')
        self.lastError = 0
        self.lastCompile = 0
        self.code = None
        self.log = logging.getLogger(self.name)
    def __str__(self):
        return self.name
    def exists(self):
        return os.path.exists(self.file)
    def modified(self):
        return os.path.getmtime(self.file)
    def run(self):
        if self.modified()>self.lastCompile:
            self.lastCompile = self.modified()
            try:
                with open(self.file, 'r') as file:
                    self.code = compile(file.read(), self.file, 'exec', dont_inherit=True)
            except:
                self.log.warning("compilation failed with %s" % traceback.format_exc())
                self.code = None
                
        # run script
        try:
            if self.code: exec(self.code)
        except EnvironmentError as err:
            if self.lastError < self.lastCompile:
                self.log.warning(err)
                self.lastError = self.lastCompile
        except StopIteration:
            pass
        except Exception:
            if self.lastError < self.lastCompile:
                self.log.warning(traceback.format_exc())
                self.lastError = self.lastCompile
        
def usage(detail=None):
    print("Usage: %s -d|--debug [scriptname]" % os.path.split(sys.argv[0])[1])
    if detail: print("***",detail)
    return 1

def main(argv):

    global script, active

    # scan options
    level = logging.INFO
    hertz = 50
    try:
        opts, args =  getopt.getopt(argv[1:], "h:d", ["hertz=","debug"])
        for opt, arg in opts:
            if opt in ("-d", "--debug"):
                level = logging.DEBUG
            if opt in ("-h", "-hertz"):
                hertz = int(arg)
                pass
    except Exception as e:
        return usage(str(e))

    # logging 
    logging.basicConfig(level=level, stream=sys.stdout)
    log = logging.getLogger(os.path.splitext(os.path.basename(argv[0]))[0])
    
    # windows support?
    try:
        import windows
    except:
        log.info("Windows integration unavailable (e.g., System Tray Icon) - install http://www.lfd.uci.edu/~gohlke/pythonlibs/#pywin32")
        windows = None

    # another instance running?
    if windows and not windows.singleton():
        log.info("instance already running - exiting")
        return usage("already running")
    

    # script to run
    if len(args) > 1: 
        return usage()
    elif len(args) == 1:
        script = Script(args[0])
        if not script.exists():
            return usage("%s not found" % script)
    else:
        script = None

    # ... load all modules
    modules = []
    sys.path.append("contrib")
    sys.path.append("modules")
    for py in os.listdir("modules"):
        if not py.endswith("py"): continue
        mod = os.path.splitext(py)[0]
        try:
            modules.append(__import__(mod))
        except Exception as e:
            log.warning("Couldn't initialize module %s: %s" % (mod, e) )
            log.debug(traceback.format_exc())
            
    # prep ui
    def switch(name):
        log.info("Switching to script %s" % name)
        global script
        script = Script(name)
        
    def quit():
        log.info("Quitting")
        global active
        active = False
        
    def actions():
        actions = [("Quit", None, None, quit)]
        for file in filter(lambda n: n.endswith('.py'), os.listdir("scripts")):
            actions.append( (file, None, os.path.basename(script.file)==file, lambda f=file: switch(f)) )
        return actions
    
    tray = windows.TrayIcon("SimScript", os.path.join(os.path.dirname(__file__), 'simscript.ico'), actions) if windows else None

    # loop
    active = True
    while active:

        # take time                
        sync = (time.clock()+(1/hertz))
        
        # pump ui events
        if tray: tray.pump(False)
        
        # sync modules
        for mod in modules: mod.sync()
    
        # run script 
        if script: script.run()
        
        # sync time
        wait = sync-time.clock()
        if wait>=0 : 
            time.sleep(wait)
        else:  
            if not __debug__:
                log.warning("%s executions took longer than sync frequency (%dms>%dms)" % ( script, (1/hertz-wait)*1000, 1/hertz*1000))
                
    # done
    return 0    


if __name__ == "__main__":
    sys.exit(main(sys.argv))

