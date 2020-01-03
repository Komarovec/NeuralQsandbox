# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew, gstreamer
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os, pymunk, numpy

pymunk_dir = os.path.dirname(pymunk.__file__)
chipmunk_libs = [
    ('chipmunk.dll', os.path.join(pymunk_dir, 'chipmunk.dll'), 'DATA'),
]

block_cipher = None


a = Analysis(['NeuralApp.py'],
             pathex=['D:\\Entertaiment\\Programy\\Python\\NeuralSandbox2'],
             binaries=None,
             datas=collect_data_files('tensorflow_core', subdir=None, include_py_files=True),
             hiddenimports=['h5py','h5py.defs','h5py.utils','h5py.h5ac','h5py._proxy'] + collect_submodules('tensorflow_core'),
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher
             )
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='NeuralQsandbox',
          debug=True,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries + chipmunk_libs,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='NeuralQsandbox')
