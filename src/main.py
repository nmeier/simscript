#!/usr/bin/env python

""" siminputs main script - automation of virtual inputs for simulators """

import runpy,sys,os,time,logging,traceback,joysticks,phidgets,getopt,Phidgets

def main(argv):

    def usage(detail=None):
        print("Usage: main.py -d|--debug scriptname")
        if detail: print("***",detail)
        return 1

    # scan options
    level = logging.INFO
    hertz = 50
    try:
        opts, args =  getopt.getopt(argv, "h:d", ["hertz=","debug"])
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
    script = args[0] + '.py'   
    scripts = os.path.abspath(os.path.join("..","scripts"))
    sys.path.append(scripts)
    
    if not os.path.exists(os.path.join(scripts, script)):
        return usage("%s not found in %s" % (script, scripts))

    # logging 
    logging.basicConfig(level=level, stream=sys.stdout)
    log = logging.getLogger("falconvjoy")

    # globals
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

    scriptState = State()
    
    scriptGlobals = dict();
    scriptGlobals['joysticks'] = joysticks.Joysticks() 
    scriptGlobals['phidgets'] = phidgets.Phidgets()
    scriptGlobals['log'] = logging.getLogger(script)
    scriptGlobals['state'] = scriptState

    # loop
    lastError = 0
    while True:
  
        sync = (time.clock()+(1/hertz))
        
        for g in scriptGlobals.values(): 
            try:
                g.poll()
            except:
                pass
    
        modified = os.path.getmtime(os.path.join(scripts, script))
            
        try:
            runpy.run_module(script[:-3], scriptGlobals)
        except EnvironmentError as err:
            if lastError < modified:
                log.warning("script failed with %s" % err)
                lastError = modified
        except StopIteration:
            pass
        except Phidgets.PhidgetException.PhidgetException as pex:
            log.debug("script failed with PhidgetException: %s" % pex.details )
        except Exception as ex:
            if lastError < modified:
                log.warning("script failed with %s %s" % (ex, traceback.format_exc()) )
                lastError = modified
            
        wait = sync-time.clock()
        if wait>=0 : 
            time.sleep(wait)
        else:  
            if not __debug__:
                log.warning("script executions took longer than sync frequency (%dms>%dms)" % ( (1/hertz-wait)*1000, 1/hertz*1000))
                
    # when we bail the loop
    return 0    


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

