# -*- coding: utf-8 -*-
"""
  brrd.constants
  ~~~~~~~~~~~~~~

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
from __future__ import division


METRICS = (
    'responseStart',  # Time to user agent receiving first byte
    'firstPaint',     # Time to initial render
    'domComplete',    # Time to DOM Comlete event
    'loadEventEnd',   # Time to load event completion
)

# Size of sliding window, in seconds.
WINDOW_SPAN = 300

# Only push an update if we have at least this many samples.
SAMPLE_THRESHOLD = 200

# Aggregation intervals.
PERIODS = (
    60 * 60,                # Hour
    60 * 60 * 24,           # Day
    60 * 60 * 24 * 7,       # Week
    60 * 60 * 24 * 30,      # Month
    60 * 60 * 24 * 365.25,  # Year
)

# Store 120 values at each resolution. This makes graphing simpler,
# because we're always working with a fixed number of points.
ROWS = 120

# We will push an aggregate value as often as we need in order to have
# ROWS many values at the smallest PERIOD.
STEP = PERIODS[0] / ROWS

# STEP should be a whole number that divides each PERIOD.
assert STEP.is_integer()
for interval in PERIODS:
    assert (interval / ROWS / STEP).is_integer()

# Set the maximum acceptable interval between samples ("heartbeat") to a
# full day. This means RRD will record an estimate for missing samples as
# long as it has at least one sample from the last 24h to go by. If we go
# longer than 24h without reporting a measurement, RRD will record a value
# of UNKNOWN instead.
HEARTBEAT = 60 * 60 * 24

# The expected range for measurements is 0 - 60,000 milliseconds.
MIN, MAX = 0, 60 * 1000
