from setuptools import setup

APP = ['macsnap2html_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,  # Changed to False to avoid menu issues
    'iconfile': 'app_icon.icns',  # Will use this if it exists
    'plist': {
        'CFBundleName': 'MacSnap2HTML Enhanced',
        'CFBundleDisplayName': 'MacSnap2HTML Enhanced',
        'CFBundleGetInfoString': "Create interactive HTML directory listings",
        'CFBundleIdentifier': 'com.noaa.macsnap2html',
        'CFBundleVersion': '2.0.1',
        'CFBundleShortVersionString': '2.0.1',
        'NSHumanReadableCopyright': 'Copyright © 2025',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13',
    },
    'packages': ['tkinter'],
    'includes': ['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
