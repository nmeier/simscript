import logging, inspect

def info(*args):
    log(logging.INFO, *args)
        
def warn(*args):
    log(logging.WARN, *args)
        
def debug(*args):
    log(logging.DEBUG, *args)
        
def log(level, *args):        
    frm = inspect.currentframe().f_back
    name = None
    while frm:
        if 'script' in frm.f_globals:
            name = frm.f_globals['script'].name
            break
        frm = frm.f_back
    logging.getLogger(name).log(level, *args)

def sync():
    pass