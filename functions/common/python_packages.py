# Copyright (C) 2025 Christopher Gearhart
# christopher@bricksbroughttolife.com
# http://bricksbroughttolife.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import importlib.util as getutil
import os
import subprocess
import sys
from os.path import dirname, exists, join

# Blender imports
# NONE!

# Module imports
from .blender import get_addon_directory


def get_blend_python_path():
    python_dir = join(os.__file__.split("lib" + os.sep)[0], "bin")
    python_name = next((f for f in os.listdir(python_dir) if f.startswith("python")), None)
    assert python_name is not None
    return join(python_dir, python_name)


def verify_package_installation(package_name:str, spec_name:str=None, version:str=None):
    """ Install package via pip if necessary (use specific version number if passed) """
    python_path = get_blend_python_path()
    # check if already installed
    if getutil.find_spec(spec_name or package_name):
        return
    # ensure pip is installed
    if not getutil.find_spec("pip"):
        subprocess.call([python_path, "-m", "ensurepip"])
    # get target folder to install package to (avoids write permissions issues)
    target_folder = join(dirname(get_addon_directory()), "modules")
    if not exists(target_folder):
        os.makedirs(target_folder)
    # install package
    package_param = package_name + ("=={}".format(version) if version is not None else "")
    subprocess.call([python_path, "-m", "pip", "install", "--disable-pip-version-check", "--target={}".format(target_folder), package_param, "--ignore-install"])


def uninstall_package(package_name):
    python_path = get_blend_python_path()
    subprocess.call([python_path, "-m", "pip", "uninstall", "-y", package_name])
