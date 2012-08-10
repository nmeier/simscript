import distutils.core, os, py2exe


def make_data_files(roots):
    data = []
    
    for root in roots:
        if os.path.isdir(root):
            for dirpath, dirnames, filenames in os.walk(root, True, None, False):
                if filenames:
                    data.append( (dirpath, [os.path.join(dirpath, f) for f in filenames]) )
                if '__pycache__' in dirnames:
                    dirnames.remove('__pycache__')
        else:
            data.append( ('', [root]) )
    return data



options = {
  "dist_dir": "build/dist",
  "includes": ["ctypes", "ctypes.wintypes", "decimal"], 
  "excludes": [], 
  "packages": []
}

data_files = make_data_files(['contrib', 'modules', 'simscript.ico'])
 
distutils.core.setup(console=['tail.py'], windows=[ {'script':'simscript.py', 'icon_resources':[(1,"simscript.ico")]} ], options={'py2exe' :options}, data_files=data_files)
