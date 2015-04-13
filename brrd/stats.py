# -*- coding: utf-8 -*-
"""
  brrd.stats
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
from __future__ import division

import heapq
import os
import threading
import time


__all__ = ('SlidingWindow', 'median')


class SlidingWindow(object):
    """Represents a sliding window of measurements."""

    def __init__(self, span):
        """Initialize. `span` is the size of the window, in seconds."""
        self.heap = []
        self.span = span
        self.lock = threading.Lock()

    def add(self, timestamp, data):
        """Add an item to the window."""
        cutoff = time.time() - self.span
        with self.lock:
            heapq.heappush(self.heap, (timestamp, data))
            while self.heap and self.heap[0][0] < cutoff:
                heapq.heappop(self.heap)

    def items(self):
        """Returns a copy of the list of items in the window."""
        cutoff = time.time() - self.span
        items = list(self.heap)
        while items and items[0][0] < cutoff:
            heapq.heappop(items)
        return items

    def __len__(self):
        return len(self.heap)

    def __iter__(self):
        return self.items().__iter__()


def median(population):
    """Compute the median of a sorted list."""
    length = len(population)
    if not length:
        raise ValueError('Cannot compute median of empty list.')
    index = (length - 1) // 2
    if length % 2:
        return population[index]
    return sum(population[index:index + 2]) / 2
