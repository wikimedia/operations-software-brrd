# -*- coding: utf-8 -*-
"""
  brrd.rrd
  ~~~~~~~~

  Copyright 2015 Ori Livneh <ori@wikimedia.org>

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

"""
import os.path
import string

import rrdtool


__all__ = ('DS', 'RRA', 'RRD')


class Template(string.Template):
    def __str__(self):
        return self.substitute(self.__dict__)


class DS(Template):
    """Represents a data source ('DS') for a round-robin database."""

    template = 'DS:${name}:${type}:${heartbeat}:${min}:${max}'

    def __init__(self, name, type, heartbeat, min, max):
        self.name = name
        self.type = type
        self.heartbeat = heartbeat
        self.min = min
        self.max = max


class RRA(Template):
    """Represents an archive ('RRA') for a round-robin database."""

    template = 'RRA:${type}:${xff}:${steps}:${rows}'

    def __init__(self, type, xff, steps, rows):
        self.type = type
        self.xff = xff
        self.steps = steps
        self.rows = rows


class RRD(object):
    """Represents a round-robin database ('RRD') file."""

    def __init__(self, filename, step, start, sources, archives):
        self.filename = os.path.abspath(filename)
        self.step = step
        self.start = start
        self.sources = sources
        self.archives = archives

    def exists(self):
        return os.path.exists(self.filename)

    def create(self, overwrite=False):
        args = [
            self.filename,
            '--no-overwrite',
            '--step', self.step,
            '--start', self.start,
        ]
        args.extend(self.sources)
        args.extend(self.archives)
        return rrdtool.create(*map(str, args))

    def update(self, values=(), time='N'):
        if len(values) != len(self.sources):
            raise ValueError('Missing sources.')
        if isinstance(values, dict):
            values = [values[source.name] for source in self.sources]
        args = [time] + list(values)
        args = ':'.join(str(arg) for arg in args)
        return rrdtool.update(self.filename, args)
