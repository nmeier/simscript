import time, sys, os.path

if __name__ == '__main__':

    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("usage: tail.py filename")
        sys.exit(1)
        
    file = os.path.abspath(sys.argv[1]) 
    
    handle = open(file,'r')

    try:
        while 1:
            where = handle.tell()
            line = handle.readline()
            if not line:
                time.sleep(0.5)
                handle.seek(where)
            else:
                print(line, end='')
    except:
        print("Exiting")
