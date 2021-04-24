"""Exceptions for the rpi-mini-battery-display library.

Copyright (C) 2020-2021 Koen Vervloesem

SPDX-License-Identifier: MIT
"""


class BatteryDisplayError(Exception):
    """Base class for exceptions raised by the rpi-mini-battery-display library."""


class InvalidBrightnessError(BatteryDisplayError):
    """Exception raised when we are asked to use an invalid brightness."""

    def __init__(self, brightness, message=None):
        """Initialize exception."""
        if message is None:
            message = "Brightness should be a number from 0 to 7."
        super().__init__(message)

        self.brightness = brightness


class InvalidLevelError(BatteryDisplayError):
    """Exception raised when we are asked to use an invalid level."""

    def __init__(self, level, message=None):
        """Initialize exception."""
        if message is None:
            message = "Level should be a number from 0 to the number of LED segments."
        super().__init__(message)

        self.level = level


class InvalidPinError(BatteryDisplayError):
    """Exception raised when we are asked to use an invalid pin number."""

    def __init__(self, pin, message=None):
        """Initialize exception."""
        if message is None:
            message = "Pin should be a number from 0 to 27."
        super().__init__(message)

        self.pin = pin


class InvalidSegmentsError(BatteryDisplayError):
    """Exception raised when we are asked to initialize a display with an invalid number
    of LED segments."""

    def __init__(self, segments, message=None):
        """Initialize exception."""
        if message is None:
            message = "Number of LED segments should be a number from 1 to 8."
        super().__init__(message)

        self.segments = segments


class NoDisplayFoundError(BatteryDisplayError):
    """Exception raised when there's no display found."""

    def __init__(self, clock_pin, data_pin, message=None):
        """Initialize exception."""
        if message is None:
            message = "No display found."
        super().__init__(message)

        self.clock_pin = clock_pin
        self.data_pin = data_pin
