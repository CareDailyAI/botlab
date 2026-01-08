"""
Created on July 3, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

from collections.abc import Iterator


class MessagesCounter(Iterator):
    def __init__(self, start=0, step=1):
        self._current = start - step  # Initialize so first __next__ returns 'start'
        self._step = step

    def __next__(self):
        self._current += self._step
        return self._current

    def get_current_value(self):
        return self._current
