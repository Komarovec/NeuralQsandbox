
"""The following code is required to make the dependency binaries available to
kivy when it imports this package.
"""

import sys
import os
from os.path import join, isdir, dirname

__all__ = ('dep_bins', )

__version__ = '0.1.17'

from os import environ

dep_bins = []
"""A list of paths that contain the binaries of this distribution.
Can be used e.g. with pyinstaller to ensure it copies all the binaries.
"""

_root = sys.prefix
dep_bins = [join(_root, 'share', 'gstreamer', 'bin')]
if isdir(dep_bins[0]):
    os.environ["PATH"] = dep_bins[0] + os.pathsep + os.environ["PATH"]
else:
    dep_bins = []


if dep_bins and isdir(dep_bins[0]):
    if environ.get('GST_PLUGIN_PATH'):
        environ['GST_PLUGIN_PATH'] = '{};{}'.format(environ['GST_PLUGIN_PATH'], dep_bins[0])
    else:
        environ['GST_PLUGIN_PATH'] = dep_bins[0]

    if not environ.get('GST_REGISTRY'):
        environ['GST_REGISTRY'] = join(dirname(dep_bins[0]), 'registry.bin')

