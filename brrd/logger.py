# -*- coding: utf-8 -*-
"""
  brrd.logger
  ~~~~~~~~~~~

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
from __future__ import division

import bisect
import logging
import zmq

import cliff.command

from .consts import *
from .rrd import *
from .stats import *
from .utils import *


def update_rrd(rrd, window):
    """Push updates to RRD."""
    samples = {}
    for timestamp, event in window:
        for metric in METRICS:
            value = event.get(metric)
            if not value:
                continue
            values = samples.setdefault(metric, [])
            bisect.insort(values, value)

    medians = {}
    for metric in METRICS:
        values = samples.get(metric, ())
        if len(values) < SAMPLE_THRESHOLD:
            return
        medians[metric] = median(values)

    rrd.update(medians)


class MetricLogger(cliff.command.Command):
    "A simple command that prints a message."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(MetricLogger, self).get_parser(prog_name)
        parser.add_argument('endpoint', help='EventLogging endpoint URL')
        parser.add_argument('rrd', help='RRD file')
        return parser

    def create_rrd(self, rrd_path):
        sources = []
        for metric in METRICS:
            source = DS(metric, 'GAUGE', HEARTBEAT, MIN, MAX)
            sources.append(source)

        archives = []
        for period in PERIODS:
            steps = period / ROWS / STEP
            archive = RRA('AVERAGE', 0.5, steps, ROWS)
            archives.append(archive)

        rrd = RRD(rrd_path, STEP, 'N', sources, archives)

        if not rrd.exists():
            rrd.create()

        return rrd

    def take_action(self, parsed_args):
        window = SlidingWindow(WINDOW_SPAN)
        rrd = self.create_rrd(parsed_args.rrd)

        worker = PeriodicThread(interval=STEP, target=update_rrd,
                                args=(rrd, window))
        worker.daemon = True
        time_start = now()

        self.log.info('Connecting to <%s>...', parsed_args.endpoint)

        socket = zmq.Context().socket(zmq.SUB)
        socket.connect(parsed_args.endpoint)
        socket.set(zmq.LINGER, 0)
        socket.set(zmq.SUBSCRIBE, b'')

        while 1:
            meta = socket.recv_json()
            if meta['schema'] == 'NavigationTiming':
                window.add(meta['timestamp'], meta['event'])
            if not worker.is_alive() and now() - time_start >= WINDOW_SPAN:
                worker.start()
