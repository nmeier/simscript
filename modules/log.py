import logging, inspect

def info(*args):
    log(logging.INFO, *args)
        
def warn(*args):
    log(logging.WARN, *args)
        
def debug(*args):
    log(logging.DEBUG, *args)
        
def log(level, *args):        
    try:
        frm = inspect.currentframe().f_back
        while True:
            name = frm.f_globals['__name__']
            if name != 'log': break
            frm = frm.f_back
    except:
        name = None
    logging.getLogger(name).log(level, *args)

def sync():
    pass