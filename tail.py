import time, sys, os.path

if __name__ == '__main__':

    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("usage: tail.py filename")
        sys.exit(1)
        
    handle = open(os.path.abspath(sys.argv[1]),'r')

    try:
        while 1:
            where = handle.tell()
            line = handle.readline()
            if not line:
                time.sleep(0.5)
                handle.seek(where)
            else:
                sys.stdout.write(line)
    except:
        pass
