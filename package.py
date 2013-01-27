import distutils.core, shutil, os, py2exe, subprocess, os, re, platform


' grep imports from first line of python files in given folder '
def grepimports(dir):
    imports = set()
    IMPORT_ = 'import '
    for f in os.listdir(dir):
        p = os.path.join(dir, f)
        if not p.endswith("py"): continue
        for line in file(p):
            if line.startswith(IMPORT_):
                for i in line[len(IMPORT_):].split(','):
                    imports.add(i.strip())
            break
    return list(imports)

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
    
arch = platform.architecture()[0]

# clean up
shutil.rmtree(os.path.join("build", arch), True)

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

dist = os.path.join("build", arch , "dist")

options = {
  "dist_dir": dist,
  "includes": grepimports('modules'), 
  "excludes" : [],
  "dll_excludes": ["w9xpopen.exe"], 
  "packages": []
}

data_files = make_data_files(['contrib', 'modules', 'scripts', 'simscript.ico'])

simscript = {'script':'simscript.py', 'dest_base':'simscript',  'icon_resources':[(1,"simscript.ico")]}
tail = {'script':'tail.py'}
 
distutils.core.setup(console=[tail], windows=[simscript], options={'py2exe' :options}, data_files=data_files)

shutil.make_archive('build/simscript-%s-r%s' % (arch, svnversion), 'zip', dist, '.')
