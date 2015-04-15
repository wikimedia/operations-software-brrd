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

import argparse
import calendar
import ctypes
import ctypes.util
import datetime
import logging
import os
import sys
import threading


__all__ = ('Application', 'monotonic_clock', 'now', 'PeriodicThread')

CLOCK_MONOTONIC_RAW = 4


class Application(object):
    """Represents a command-line application."""

    log_format = '[%(asctime)s] %(message)s'

    def run(self):
        pass

    def __init__(self, args=None):
        self.args = self.get_argument_parser().parse_args(args)
        self.log = self.get_logger()

    def start(self):
        try:
            self.run()
        finally:
            self.clean_up()

    def clean_up(self):
        pass

    def get_description(self):
        return getattr(self, 'description', self.get_name())

    def get_argument_parser(self):
        parser = argparse.ArgumentParser(prog=self.get_name(),
                                         description=self.get_description())
        parser.add_argument(
            '-v', '--verbose',
            action='store_const',
            const=logging.DEBUG,
            default=logging.INFO,
            dest='log_level',
            help='Increase verbosity of output.',
        )
        parser.add_argument(
            '--log-file',
            default=None,
            help='Specify a file to log output. Disabled by default.',
            type=os.path.abspath
        )
        return parser

    def get_name(self):
        return getattr(self, 'name', self.__class__.__name__)

    def get_logger(self):
        """Get a logging.Logger instance for this application."""
        logger = logging.getLogger(self.get_name())
        handlers = [logging.StreamHandler(stream=sys.stderr)]
        if self.args.log_file:
            handlers.append(logging.handlers.RotatingFileHandler(
                self.args.log_file, backupCount=10, maxBytes=5e7))
        formatter = logging.Formatter(self.log_format)
        logger.setLevel(self.args.log_level)
        for handler in handlers:
            handler.setFormatter(formatter)
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)
        return logger


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
