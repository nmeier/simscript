#!/usr/bin/env python

""" siminputs main script - automation of virtual inputs for simulators """

import runpy,sys,os,time,logging,traceback,getopt

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

def main(argv):

    def usage(detail=None):
        print("Usage: %s -d|--debug scriptname" % os.path.split(argv[0])[1])
        if detail: print("***",detail)
        return 1

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
    if len(args) != 1: 
        return usage()
    scriptName = args[0]
    scriptFile = scriptName + '.py'   
    scriptDir = os.path.abspath("scripts")
    sys.path.append(scriptDir)
    
    if not os.path.exists(os.path.join(scriptDir, scriptFile)):
        return usage("%s not found in %s" % (scriptFile, scriptDir))

    # logging 
    logging.basicConfig(level=level, stream=sys.stdout)
    log = logging.getLogger(os.path.split(argv[0])[1])

    # scriptvariables
    class State(dict):
        def __missing__(self, key):
            return None
        def __getattribute__(self, attr):
            try:
                return super().__getattribute__(attr)
            except:
                return self[attr]
        def __setattr__(self, attr, val):
            self[attr] = val
        def toggle(self,key,value):
            last = self[key]
            self[key] = value
            if last:
                return False
            return value

    scriptVars = dict();
    scriptVars['log'] = logging.getLogger(scriptFile)
    scriptVars['state'] = State()
    
    # ... all IO modules
    sys.path.append("contrib")
    sys.path.append("vars")
    for py in os.listdir("vars"):
        if not py.endswith("py"): continue
        mod = os.path.splitext(py)[0]
        try:
            scriptVars[mod] = __import__(mod).init()
        except:
            log.warning("Couldn't initialize var %s: %s" % (mod, traceback.format_exc()) )
    
    # loop
    lastError = 0
    while True:
  
        sync = (time.clock()+(1/hertz))
        
        for g in scriptVars.values(): 
            try:
                g.poll()
            except:
                pass
    
        modified = os.path.getmtime(os.path.join(scriptDir, scriptFile))
            
        try:
            runpy.run_module(scriptName, scriptVars)
        except EnvironmentError as err:
            if lastError < modified:
                log.warning("scriptFile failed with %s" % err)
                lastError = modified
        except StopIteration:
            pass
        except Exception as ex:
            if lastError < modified:
                log.warning("scriptFile failed with %s %s" % (ex, traceback.format_exc()) )
                lastError = modified
            
        wait = sync-time.clock()
        if wait>=0 : 
            time.sleep(wait)
        else:  
            if not __debug__:
                log.warning("scriptFile executions took longer than sync frequency (%dms>%dms)" % ( (1/hertz-wait)*1000, 1/hertz*1000))
                
    # when we bail the loop
    return 0    


if __name__ == "__main__":
    sys.exit(main(sys.argv))

