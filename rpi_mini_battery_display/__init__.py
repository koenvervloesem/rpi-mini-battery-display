"""Library for the 10 LED mini battery display using the TM1651 chip.

Copyright (C) 2020 Koen Vervloesem

SPDX-License-Identifier: MIT
"""
# pragma pylint: disable=no-member
from time import sleep

import RPi.GPIO as GPIO

LEVEL_TAB = [
    0x00,  #
    0x01,  # 01
    0x03,  # 012
    0x07,  # 0123
    0x0F,  # 01234
    0x1F,  # 0123456
    0x3F,  # 012345678
    0x7F,  # 0123456789
]

BRIGHT_DARKEST = 0
BRIGHT_TYPICAL = 2
BRIGHTEST = 7

ADDR_AUTO = 0x40
ADDR_FIXED = 0x44
STARTADDR = 0xC0

TM1651_DELAY = 0.000050  # 50 microseconds


class InvalidBrightnessError(Exception):
    """Exception raised when we are asked to use an invalid brightness."""

    def __init__(self, brightness, message=None):
        """Initialize exception."""
        if message is None:
            message = "Brightness should be a number from 0 to 7."
        super().__init__(message)

        self.brightness = brightness


class InvalidLevelError(Exception):
    """Exception raised when we are asked to use an invalid level."""

    def __init__(self, level, message=None):
        """Initialize exception."""
        if message is None:
            message = "Level should be a number from 0 to 7."
        super().__init__(message)

        self.level = level


class InvalidPinError(Exception):
    """Exception raised when we are asked to use an invalid pin number."""

    def __init__(self, pin, message=None):
        """Initialize exception."""
        if message is None:
            message = "Pin should be a number from 0 to 27."
        super().__init__(message)

        self.pin = pin


class BatteryDisplay:
    """Class to control the TM1651 battery display."""

    def __init__(self, clock_pin=24, data_pin=23):
        """Initialize the TM1651 battery display object.

        clock_pin and data_pin should be BCM pin numbers from 0 to 27."""
        if clock_pin not in range(28):
            raise InvalidPinError(
                clock_pin, "Clock pin should be a number from 0 to 27."
            )
        self.clock_pin = clock_pin

        if data_pin not in range(28):
            raise InvalidPinError(data_pin, "Data pin should be a number from 0 to 27.")
        self.data_pin = data_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(clock_pin, GPIO.OUT)
        GPIO.setup(data_pin, GPIO.OUT)

        self.set_brightness(BRIGHT_TYPICAL)
        self.clear_display()

    def set_brightness(self, brightness):
        """Set a command to take effect the next time it displays.

        brightness should be an integer from 0 to 7."""
        if brightness not in range(8):
            raise InvalidBrightnessError(brightness)
        self.command_display_control = 0x88 + brightness

    def clear_display(self):
        """Clear the display."""
        self.set_level(0)
        self.frame(False)

    def set_level(self, level):
        """Display a level on the battery display.

        level should be an integer from 0 to 7."""
        if level not in range(8):
            raise InvalidLevelError(level)

        # Start signal sent to TM1651
        self.start()
        self.write_byte(ADDR_FIXED)
        self.stop()

        self.start()
        self.write_byte(0xC0)
        self.write_byte(LEVEL_TAB[level])
        self.stop()

        self.start()
        self.write_byte(self.command_display_control)
        self.stop()

    def frame(self, frame_on):
        """Turn a frame on or off."""
        if frame_on:
            seg_data = 0x40
        else:
            seg_data = 0x00

        # Start signal sent to TM1651
        self.start()
        self.write_byte(ADDR_AUTO)
        self.stop()

        self.start()
        self.write_byte(0xC1)
        for _ in range(3):
            self.write_byte(seg_data)
        self.stop()

        self.start()
        self.write_byte(self.command_display_control)
        self.stop()

    def write_byte(self, write_data):
        """Write a byte to the TM1651."""
        # Send 8 data bits, LSB first
        for _ in range(8):
            # CLK low
            GPIO.output(self.clock_pin, GPIO.LOW)
            sleep(TM1651_DELAY)

            # Write data bit
            if write_data & 0x01:
                GPIO.output(self.data_pin, GPIO.HIGH)
            else:
                GPIO.output(self.data_pin, GPIO.LOW)
            sleep(TM1651_DELAY)

            # CLK high
            GPIO.output(self.clock_pin, GPIO.HIGH)
            sleep(TM1651_DELAY)

            # Next bit
            write_data = write_data >> 1

        # Wait for the ACK: CLK low, DIO high
        GPIO.output(self.clock_pin, GPIO.LOW)
        GPIO.output(self.data_pin, GPIO.HIGH)
        sleep(TM1651_DELAY)

        # CLK high, set DIO to input
        GPIO.output(self.clock_pin, GPIO.HIGH)
        GPIO.setup(self.data_pin, GPIO.IN)
        sleep(TM1651_DELAY)

        ack = GPIO.input(self.data_pin)
        GPIO.setup(self.data_pin, GPIO.OUT)

        if not ack:
            GPIO.output(self.data_pin, GPIO.LOW)

        sleep(TM1651_DELAY)
        GPIO.output(self.clock_pin, GPIO.LOW)
        sleep(TM1651_DELAY)

    def start(self):
        """Send start signal to TM1651."""
        GPIO.output(self.data_pin, GPIO.LOW)
        sleep(TM1651_DELAY)

    def stop(self):
        """End of transmission."""
        GPIO.output(self.data_pin, GPIO.LOW)
        sleep(TM1651_DELAY)
        GPIO.output(self.clock_pin, GPIO.HIGH)
        sleep(TM1651_DELAY)
        GPIO.output(self.data_pin, GPIO.HIGH)
        sleep(TM1651_DELAY)
