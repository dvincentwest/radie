from win32com.client import Dispatch
import sys
import os
import pathlib

executable = pathlib.Path(sys.executable)
python = pathlib.Path(os.path.dirname(executable)) / "python.exe"
pythonw = pathlib.Path(os.path.dirname(executable)) / "pythonw.exe"

this_dir = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
icon = this_dir / "dataquick/qt/resources/icons/dataquick.ico"
usr = pathlib.Path(os.path.expanduser("~"))
desktop = usr / "Desktop"
start_menu = usr / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs"
dataquick_startmenu_dir = start_menu / "DataQuick"
shortcut_windows = dataquick_startmenu_dir / "DataQuick.lnk"
shortcut_console = dataquick_startmenu_dir / "DataQuick - Console.lnk"

if not dataquick_startmenu_dir.exists():
    os.mkdir(dataquick_startmenu_dir)

shell = Dispatch('WScript.Shell')

if python.exists():
    if shortcut_console.exists():
        os.remove(shortcut_console)
    shortcut = shell.CreateShortCut(str(shortcut_console))
    shortcut.Targetpath = str(python)
    shortcut.Arguments = '-m dataquick.qt.viewer'
    shortcut.IconLocation = str(icon)
    shortcut.save()

if pythonw.exists():
    if shortcut_windows.exists():
        os.remove(shortcut_windows)
    shortcut = shell.CreateShortCut(str(shortcut_windows))
    shortcut.Targetpath = str(pythonw)
    shortcut.Arguments = '-m dataquick.qt.viewer'
    shortcut.IconLocation = str(icon)
    shortcut.save()
