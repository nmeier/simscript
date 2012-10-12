#!/usr/bin/env python

""" simscript main - automation of virtual inputs for simulators """

import sys,os,time,logging,tempfile,traceback,getopt,subprocess

def modulo(value,start,end):
    if value!=value: #NaN check
        return value
    value = (value - start) % (end-start)
    value = start+value if value>=0 else end+value
    return value

class Script():
    dir = os.path.abspath("scripts")
    def __init__(self, name):
        if not name: raise Exception("no such script %s" % name)
        self.name = name if not name.endswith('.py') else name[:-3]
        self.file = os.path.join(Script.dir, self.name+'.py')
        if not self.exists(): raise Exception("script % doesn't exist" % name)
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
                with open(self.file, 'r') as handle:
                    self.code = compile(handle.read(), self.file, 'exec', dont_inherit=True)
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

class LogFile(logging.FileHandler):
    def __init__(self):
        self.error = 0
        self.warn = 0
        self.file = tempfile.NamedTemporaryFile(mode='w+', suffix='.log', prefix='simscript_', delete=False)
        self._tail = None
        logging.FileHandler.__init__(self, self.file.name, 'w+')
        self.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        
    def __str__(self):
        return "Log" if self.error==0 and self.warn == 0 else "Log (%d warnings, %d errors)" % (self.warn, self.error)
        
    def emit(self, record):
        if record.levelno==logging.WARN: self.warn += 1
        elif record.levelno==logging.ERROR: self.error += 1
        logging.FileHandler.emit(self, record)
        
    def show(self):
        self.hide()
        
        # either deployed tail.exe, interpreting python (not pythonw) or fallback notepad
        tail = 'notepad "%s"' %  os.path.abspath(self.file.name)
        if os.path.isfile("tail.exe"):
            tail = 'tail.exe "%s"' %  os.path.abspath(self.file.name)
        elif 'python' in sys.executable:
            python = sys.executable.replace('pythonw', 'python')
            if os.path.isfile(python):
                tail = '"%s" "%s" "%s"' % (python, os.path.abspath("tail.py"), os.path.abspath(self.file.name))
            
        log.info("Launching %s", tail)
        self._tail = subprocess.Popen(tail, creationflags=0x00000010) # CREATE_NEW_CONSOLE
        self.reset()
        
    def hide(self):
        if not self._tail:
            return
        try:
            self._tail.terminate()
        except:
            pass
        self._tail = None
        
    def reset(self):
        self.warn = self.error = 0
        
class LoggerAsStream:
    def __init__(self, logger, level):
        self._logger = logger
        self._level = level
        self._buffer = ''
    def write(self, buf):
        for line in buf.splitlines(True):
            if '\n' in line:
                self._logger.log(self._level, self._buffer + line.rstrip())
                self._buffer = ''
            else:
                self._buffer += line
            
def main(argv):

    global script, active, log

    # scan options
    level = logging.INFO
    hertz = 20
    try:
        opts, args =  getopt.getopt(argv[1:], "h:d", ["hertz=","debug","help"])
        for opt, arg in opts:
            if opt in ("-d", "--debug"):
                level = logging.DEBUG
            if opt in ("-h", "--hertz"):
                hertz = int(arg)
                pass
            if opt in ("--help"):
                return usage()
    except Exception as e:
        return usage(str(e))

    # setup logging 
    logging.basicConfig(level=level, stream=sys.stdout)
    log = logging.getLogger(os.path.splitext(os.path.basename(argv[0]))[0])
    
    logfile = LogFile()
    log.info("Logging to %s" % logfile.file.name)
    logging.getLogger().addHandler(logfile)

    log.info("Python %s" % sys.version)

    if sys.stderr:
        sys.stderr = LoggerAsStream(logging.getLogger("STDOUT"), logging.INFO)
    if sys.stdout:
        sys.stdout = LoggerAsStream(logging.getLogger("STDERR"), logging.INFO)
       
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
    script = None
    if len(args) > 1: 
        return usage()
    elif len(args) == 1:
        try:
            script = Script(args[0])
        except:
            return usage("%s not found" % args[0])
    else:
        if not windows:
            return usage()
        try:
            script = Script(windows.recall("script"))
        except Exception as e:
            log.debug("restoring recalled script failed %s" % e)
    
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
        windows.remember("script", script)
        
    def bbye():
        log.info("Quitting")
        tray.close()
        global active
        active = False
        
    def edit():
        log.info("Edit")
        subprocess.Popen("explorer %s" % Script.dir)
        
    def actions():
        actions = [("Quit", None, None, bbye), (logfile, None, None, logfile.show), ("Edit", None, None, edit)]
        for handle in filter(lambda n: n.endswith('.py'), os.listdir("scripts")):
            actions.append( (handle, None, script and os.path.basename(script.file)==handle, lambda f=handle: switch(f)) )
        return actions
    
    tray = windows.TrayIcon("SimScript", os.path.abspath('simscript.ico'), actions) if windows else None

    # loop
    active = True
    while active:

        # take time                
        sync = (time.clock()+(1.0/hertz))
        
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
            log.info("%s executions took longer than sync frequency (%dms>%dms)" % ( script, (1.0/hertz-wait)*1000, 1.0/hertz*1000))
                
    # cleanup 
    logfile.hide()
                
    # done
    return 0    


if __name__ == "__main__":
    sys.exit(main(sys.argv))

