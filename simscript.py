#!/usr/bin/env python

""" simscript main - automation of virtual inputs for simulators """

import sys,os,time,logging,traceback,getopt,windows

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
        self.name = name if name.endswith('.py') else name+'.py'
        self.file = os.path.join(os.path.abspath("scripts"), self.name)
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

    # another instance running?
    if not windows.singleton():
        return usage("already running")

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

    # script to run
    if len(args) > 1: 
        return usage()
    elif len(args) == 1:
        script = Script(args[0])
        if not script.exists():
            return usage("%s not found" % script)
    else:
        script = None

    # logging 
    logging.basicConfig(level=level, stream=sys.stdout)
    log = logging.getLogger(os.path.split(argv[0])[1])

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
    def actions():
        actions = [("Quit", None, None, lambda: tray.close())]
        for file in filter(lambda n: n.endswith('.py'), os.listdir("scripts")):
            actions.append( (file, None, script.name==file, lambda f=file: switch(f)) )
        return actions
    
    def switch(name):
        log.info("Switching to script %s" % name)
        nonlocal script
        script = Script(name)
        
    tray = windows.TrayIcon("SimScript", os.path.join(os.path.dirname(__file__), 'simscript.ico'), actions)

    # loop
    active = [True]
    while True in active:

        # take time                
        sync = (time.clock()+(1/hertz))
        
        # pump ui events
        tray.pump(False)
        
        # sync modules
        for mod in modules: 
            mod.sync()
    
        # run script 
        if script: script.run()
        
        # sync time
        wait = sync-time.clock()
        if wait>=0 : 
            time.sleep(wait)
        else:  
            if not __debug__:
                log.warning("%s executions took longer than sync frequency (%dms>%dms)" % ( script, (1/hertz-wait)*1000, 1/hertz*1000))
                
    # when we bail the loop
    return 0    


if __name__ == "__main__":
    sys.exit(main(sys.argv))

