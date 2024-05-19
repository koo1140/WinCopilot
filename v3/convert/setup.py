import sys
from cx_Freeze import setup, Executable
import shutil
import os

# Hide console window on Windows (optional for other platforms)
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Hides console on Windows

setup(
    name="CopilotBeta",
    version="0.3",
    description="Windows Copilot",
    executables=[Executable("Copilot.py", base=base)],  # Apply base if set
)

shutil.copy('settings.json', 'build/exe.win-amd64-3.11/settings.json')
import os
if not os.path.exists('build/exe.win-amd64-3.11/templates'):
    os.makedirs('build/exe.win-amd64-3.11/templates')
shutil.copy('templates/index.html', 'build/exe.win-amd64-3.11/templates/index.html')

print("\n\nSuccess!🎉")

# Create a shortcut for copilot.exe on the desktop
desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
shortcut_path = os.path.join(desktop_path, 'Copilot.lnk')
shutil.copy('build/exe.win-amd64-3.11/Copilot.exe', shortcut_path)
