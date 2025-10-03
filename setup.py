from setuptools import setup

APP = ['macsnap2html_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app_icon.icns',  # Your icon file
    'plist': {
        'CFBundleName': 'MacSnap2HTML Enhanced',
        'CFBundleDisplayName': 'MacSnap2HTML Enhanced',
        'CFBundleGetInfoString': "Create interactive HTML directory listings",
        'CFBundleIdentifier': 'com.yourcompany.macsnap2html',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025',
        'NSHighResolutionCapable': True,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)