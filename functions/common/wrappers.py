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
import time
import sys

# Blender imports
import bpy

# Module imports
from .reporting import stopwatch


# https://github.com/CGCookie/retopoflow
def timed_call(label="Time Elapsed", precision=2):
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            time_beg = time.time()
            ret = fn(*args, **kwargs)
            stopwatch(label, time_beg, precision=precision)
            return ret
        return wrapped
    return wrapper


# corrected bug in previous version of blender_version fn wrapper
# https://github.com/CGCookie/retopoflow/commit/135746c7b4ee0052ad0c1842084b9ab983726b33#diff-d4260a97dcac93f76328dfaeb5c87688
def blender_version_wrapper(op, ver):
    self = blender_version_wrapper
    if not hasattr(self, "init"):
        major, minor, rev = bpy.app.version
        blenderver = "%d.%02d" % (major, minor)
        self.fns = {}
        self.ops = {
            "<": lambda v: blenderver < v,
            ">": lambda v: blenderver > v,
            "<=": lambda v: blenderver <= v,
            "==": lambda v: blenderver == v,
            ">=": lambda v: blenderver >= v,
            "!=": lambda v: blenderver != v,
        }
        self.init = True
    update_fn = self.ops[op](ver)
    fns = self.fns

    def wrapit(fn):
        n = fn.__name__
        if update_fn:
            fns[n] = fn

        def callit(*args, **kwargs):
            return fns[n](*args, **kwargs)

        return callit
    return wrapit


# This program shows off a python decorator(
# which implements tail call optimization. It
# does this by throwing an exception if it is
# its own grandparent, and catching such
# exceptions to recall the stack.
# https://code.activestate.com/recipes/474088-tail-call-optimization-decorator/

class TailRecurseException(Exception):
  def __init__(self, args, kwargs):
    self.args = args
    self.kwargs = kwargs

def tail_call_optimized(g):
    """
    This function decorates a function with tail call
    optimization. It does this by throwing an exception
    if it is its own grandparent, and catching such
    exceptions to fake the tail call optimization.

    This function fails if the decorated
    function recurses in a non-tail context.
    """
    def func(*args, **kwargs):
        f = sys._getframe()
        if f.f_back and f.f_back.f_back and f.f_back.f_back.f_code == f.f_code:
            raise TailRecurseException(args, kwargs)
        while True:
            try:
                return g(*args, **kwargs)
            except TailRecurseException as e:
                args = e.args
                kwargs = e.kwargs

    func.__doc__ = g.__doc__
    return func

# # USAGE:
# @tail_call_optimized
# def factorial(n, acc=1):
#   "calculate a factorial"
#   if n == 0:
#     return acc
#   return factorial(n-1, n*acc)
#
# print factorial(10000)
# # prints a big, big number,
# # but doesn't hit the recursion limit.
#
# @tail_call_optimized
# def fib(i, current = 0, next = 1):
#   if i == 0:
#     return current
#   else:
#     return fib(i - 1, next, current + next)
#
# print fib(10000)
# # also prints a big number,
# # but doesn't hit the recursion limit.
