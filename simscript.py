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
    scriptFile = os.path.join(os.path.abspath("scripts"), scriptName + '.py')   
    
    #sys.path.append(scriptDir)
    
    if not os.path.exists(scriptFile):
        return usage("%s not found" % scriptFile)

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

    # loop
    lastError = 0
    lastCompile = 0
    while True:

        # compile
        lastModified = os.path.getmtime(scriptFile)
        if lastModified>lastCompile:
            lastCompile = lastModified
            try:
                with open(scriptFile, 'r') as file:
                    code = compile(file.read(), scriptFile, 'exec', dont_inherit=True)
            except:
                log.warning("%s compilation failed with %s" % (scriptFile, traceback.format_exc()))
                
        # take time                
        sync = (time.clock()+(1/hertz))
        
        # run modules
        for mod in modules: 
            mod.sync()
    
        # run script
        try:
            if code: exec(code)
        except EnvironmentError as err:
            if lastError < lastCompile:
                log.warning("%s failed with %s" % (scriptFile,err))
                lastError = lastCompile
        except StopIteration:
            pass
        except Exception:
            if lastError < lastCompile:
                log.warning("%s failed with %s" % (scriptFile, traceback.format_exc()) )
                lastError = lastCompile
            
        # sync time
        wait = sync-time.clock()
        if wait>=0 : 
            time.sleep(wait)
        else:  
            if not __debug__:
                log.warning("%s executions took longer than sync frequency (%dms>%dms)" % ( scriptFile, (1/hertz-wait)*1000, 1/hertz*1000))
                
    # when we bail the loop
    return 0    


if __name__ == "__main__":
    sys.exit(main(sys.argv))

