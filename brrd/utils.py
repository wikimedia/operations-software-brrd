# -*- coding: utf-8 -*-
"""
  brrd.utils
  ~~~~~~~~~~

  Copyright 2015 Ori Livneh <ori@wikimedia.org>

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
  implied.  See the License for the specific language governing
  permissions and limitations under the License.

"""
from __future__ import absolute_import, division

import calendar
import ctypes
import ctypes.util
import datetime
import os
import threading


__all__ = ('monotonic_clock', 'now', 'PeriodicThread')

CLOCK_MONOTONIC_RAW = 4


class PeriodicThread(threading.Thread):
    """Represents a threaded job that runs repeatedly at a regular interval."""

    def __init__(self, interval, *args, **kwargs):
        """Initialize. `interval` specifies how often thread runs."""
        self.interval = interval
        self.ready = threading.Event()
        self.stopping = threading.Event()
        super(PeriodicThread, self).__init__(*args, **kwargs)

    def run(self):
        """Invoke the thread's primary function at regular intervals."""
        while not self.stopping.is_set():
            time_start = monotonic_clock()
            self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
            time_stop = monotonic_clock()
            run_duration = time_stop - time_start
            time_to_next_run = self.interval - run_duration
            if self.ready.wait(time_to_next_run):
                self.ready.clear()

    def stop(self):
        """Graceful stop: stop once the current iteration is complete."""
        self.stopping.set()


def now():
    """Get current UTC epoch time."""
    utc_now = datetime.datetime.utcnow()
    return calendar.timegm(utc_now.utctimetuple())


class TimeSpec(ctypes.Structure):
    """Time specification, as described in clock_gettime(3)."""
    _fields_ = ('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long)


libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
ts = TimeSpec()
ts_ptr = ctypes.pointer(ts)


def monotonic_clock():
    """Monotonic clock, cannot go backward."""
    if libc.clock_gettime(CLOCK_MONOTONIC_RAW, ts_ptr):
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    return ts.tv_sec + ts.tv_nsec / 1.0e9

try:
    monotonic_clock()
except Exception:
    monotonic_clock = now
