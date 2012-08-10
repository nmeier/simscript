from distutils.core import setup
import py2exe
 
setup(console=['tail.py'], windows=['simscript.py'],
      options={ "py2exe": {"includes": ["ctypes", "ctypes.wintypes", "decimal"],
                           "excludes": [],
                           "packages": [] }}
)