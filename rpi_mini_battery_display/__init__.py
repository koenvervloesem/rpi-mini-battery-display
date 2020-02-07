"""Library for the 10 LED mini battery display using the TM1651 chip.

Copyright (C) 2020 Koen Vervloesem

SPDX-License-Identifier: MIT
"""
# pragma pylint: disable=no-member,no-name-in-module
from time import sleep

import RPi.GPIO as GPIO
from RPi.GPIO import HIGH, IN, LOW, OUT

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

# Chip commands
# Data commands
ADDR_FIXED = 0x44  # Set fixed address mode
# Display control commands
DISPLAY_OFF = 0x80  # Set display off
DISPLAY_ON = 0x88  # Set display on
# Address commands
ADDR_START = 0xC0  # Set address of the display register

# The TM1651's maximum frequency is 500 kHz with a 50% duty cycle.
# We take a conservative clock cycle here.
TM1651_CYCLE = 0.000050  # 50 microseconds


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
    """Class to control the TM1651 battery display.

    The TM1651 chip communicates using a two-line serial bus interface.

    Pins SEG1 to SEG7 (2-8) are connected to segments 1 to 7 of the display.

    From pins GRID4 to GRID1 (9-12), only GRID1 is connected to the display.

    Pin K1 (for key input) is not connected.
    """

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
        GPIO.setup(clock_pin, OUT)
        GPIO.setup(data_pin, OUT)

        self.set_brightness(BRIGHT_TYPICAL)
        self.clear_display()

    def set_clock(self, state):
        """Set the state of the clock pin: HIGH or LOW."""
        GPIO.output(self.clock_pin, state)

    def set_data(self, state):
        """Set the state of the data pin: HIGH or LOW."""
        GPIO.output(self.data_pin, state)

    def set_brightness(self, brightness):
        """Set a command to take effect the next time it displays.

        brightness should be an integer from 0 to 7."""
        if brightness not in range(8):
            raise InvalidBrightnessError(brightness)
        self.brightness = brightness

    def send_command(self, *data):
        """Send a command and optional data to the TM1651."""
        self.start()
        for byte in data:
            self.write_byte(byte)
        self.stop()

    def clear_display(self):
        """Clear the display."""
        self.set_level(0)

    def set_level(self, level):
        """Display a level on the battery display.

        level should be an integer from 0 to 7."""
        if level not in range(8):
            raise InvalidLevelError(level)

        self.send_command(ADDR_FIXED)
        self.send_command(ADDR_START, LEVEL_TAB[level])
        self.send_command(DISPLAY_ON + self.brightness)

    def write_byte(self, write_data):
        """Write a byte to the TM1651."""
        # Send 8 data bits, LSB first
        for _ in range(8):
            # CLK low
            self.set_clock(LOW)
            sleep(TM1651_CYCLE)

            # Write data bit
            if write_data & 0x01:
                self.set_data(HIGH)
            else:
                self.set_data(LOW)
            sleep(TM1651_CYCLE)

            # CLK high
            self.set_clock(HIGH)
            sleep(TM1651_CYCLE)

            # Next bit
            write_data = write_data >> 1

        # Wait for the ACK: CLK low, DIO high
        self.set_clock(LOW)
        self.set_data(HIGH)
        sleep(TM1651_CYCLE)

        # CLK high, set DIO to input
        self.set_clock(HIGH)
        GPIO.setup(self.data_pin, IN)
        sleep(TM1651_CYCLE)

        ack = GPIO.input(self.data_pin)
        GPIO.setup(self.data_pin, OUT)

        if not ack:
            self.set_data(LOW)

        sleep(TM1651_CYCLE)
        self.set_clock(LOW)
        sleep(TM1651_CYCLE)

    def delineate_transmission(self, begin):
        """Delineate a data transmission to the TM1651.

        The begin parameter is a boolean with the start value of DIO.
        """
        # DIO changes its value while CLK is HIGH.
        self.set_data(begin)
        sleep(TM1651_CYCLE / 2)

        self.set_clock(HIGH)
        sleep(TM1651_CYCLE / 4)

        self.set_data(not begin)
        sleep(TM1651_CYCLE / 4)

    def start(self):
        """Start a data transmission to the TM1651."""
        # DIO changes from HIGH to low while CLK is high.
        # CLK ____████
        # DIO ██████__
        self.delineate_transmission(HIGH)

    def stop(self):
        """Stop a data transmission to the TM1651."""
        # DIO changes from LOW to HIGH while CLK is HIGH.
        # CLK ____████
        # DIO ______██
        self.delineate_transmission(LOW)
