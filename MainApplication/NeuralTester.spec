# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew, gstreamer
import os, pymunk
pymunk_dir = os.path.dirname(pymunk.__file__)
chipmunk_libs = [
    ('chipmunk.dll', os.path.join(pymunk_dir, 'chipmunk.dll'), 'DATA'),
]

block_cipher = None


a = Analysis(['NeuralApp.py'],
             pathex=['D:\\Entertaiment\\Programy\\Python\\NeuralSandbox2\\MainApplication'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='NeuralTester',
          debug=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe,
               a.binaries + chipmunk_libs,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='NeuralTester')
