from __future__ import print_function

import sys

try:
    from winreg import *
except ImportError:
    from _winreg import *

# tweak as necessary
version = sys.version[:3]
installpath = sys.prefix

regpath = "SOFTWARE\\Python\\Pythoncore\\{0}\\".format(version)
installkey = "InstallPath"
pythonkey = "PythonPath"
pythonpath = "{0};{1}\\Lib\\;{2}\\DLLs\\".format(
    installpath, installpath, installpath)


def RegisterPy():
    try:
        reg = OpenKey(HKEY_CURRENT_USER, regpath)
    except EnvironmentError as e:
        try:
            reg = CreateKey(HKEY_CURRENT_USER, regpath)
            SetValue(reg, installkey, REG_SZ, installpath)
            SetValue(reg, pythonkey, REG_SZ, pythonpath)
            CloseKey(reg)
        except:
            print("*** Unable to register!")
            return
        print("--- Python", version, "is now registered!")
        return
    if (QueryValue(reg, installkey) == installpath and
            QueryValue(reg, pythonkey) == pythonpath):
        CloseKey(reg)
        print("=== Python", version, "is already registered!")
        return
    CloseKey(reg)
    print("*** Unable to register!")
    print("*** You probably have another Python installation!")


if __name__ == "__main__":
    RegisterPy()