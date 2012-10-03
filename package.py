import distutils.core, shutil, os, py2exe, subprocess, re

# check revision
svnversion = 'XXX'
try:
    svnversion = str(subprocess.check_output("svnversion")).strip()
except:
    print("Failed to determine revision - is svnversion in path?")
    pass
try:
    svnversion = int(svnversion)
    print("Source @ revision %s" % svnversion)
except:
    svnversion = svnversion.replace(':', '-')
    print("Source @ modified revision %s" % svnversion)
    
# clean up
shutil.rmtree('build', True)

# calculate extra files
def make_data_files(roots):
    data = []
    
    for root in roots:
        if os.path.isdir(root):
            for dirpath, dirnames, filenames in os.walk(root, True, None, False):
                if filenames:
                    data.append( (dirpath, [os.path.join(dirpath, f) for f in filenames if not '.pyc' in f]) )
                if '__pycache__' in dirnames:
                    dirnames.remove('__pycache__')
                if '.svn' in dirnames:
                    dirnames.remove('.svn')
        else:
            data.append( ('', [root]) )
    return data



options = {
  "dist_dir": "build/dist",
  "includes": ["ctypes", "ctypes.wintypes", "decimal"], 
  "excludes" : [],
  "dll_excludes": ["w9xpopen.exe"], 
  "packages": []
}

data_files = make_data_files(['contrib', 'modules', 'scripts', 'simscript.ico'])

simscript = {'script':'simscript.py', 'dest_base':'simscript',  'icon_resources':[(1,"simscript.ico")]}
tail = {'script':'tail.py'}
 
distutils.core.setup(console=[tail], windows=[simscript], options={'py2exe' :options}, data_files=data_files)

shutil.make_archive('build/simscript-r%s' % svnversion, 'zip', 'build/dist', '.')
