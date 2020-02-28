"""Library for the 10 LED mini battery display using the TM1651 chip.

Copyright (C) 2020 Koen Vervloesem

SPDX-License-Identifier: MIT
"""
# pragma pylint: disable=no-member,no-name-in-module
from enum import IntEnum
from time import sleep

import RPi.GPIO as GPIO
from RPi.GPIO import HIGH, IN, LOW, OUT

from rpi_mini_battery_display.exceptions import (
    InvalidBrightnessError,
    InvalidLevelError,
    InvalidPinError,
    NoDisplayFoundError,
)

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

# The TM1651's maximum frequency is 500 kHz with a 50% duty cycle.
# We take a conservative clock cycle here.
TM1651_CYCLE = 0.000050  # 50 microseconds


class Command(IntEnum):
    """An enumeration of commands for the display."""

    # Data commands
    ADDR_FIXED = 0x44  # Set fixed address mode
    # Display control commands
    DISPLAY_OFF = 0x80  # Set display off
    DISPLAY_ON = 0x88  # Set display on
    # Address commands
    ADDR_START = 0xC0  # Set address of the display register


class Brightness(IntEnum):
    """An enumeration of brightness values for the display."""

    DARKEST = 0  # 0 is actually not off!
    DARKER = 1
    DARK = 2
    TYPICAL = 3
    SEMI_BRIGHT = 4
    BRIGHT = 5
    BRIGHTER = 6
    BRIGHTEST = 7


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

        self.set_brightness(Brightness.DARK)
        ack = self.clear_display()

        # If the TM1651 hasn't returned an ACK,
        # assume that no LED controller is connected on these pins.
        if not ack:
            raise NoDisplayFoundError(clock_pin, data_pin)

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
        """Send a command and optional data to the TM1651.

        Returns True if the TM1651 has sent an ACK after each written byte."""
        ack = True

        self.start()
        for byte in data:
            ack = self.write_byte(byte) and ack
        self.stop()

        return ack

    def clear_display(self):
        """Clear the display.

        Returns True if the TM1651 has sent an ACK after the write."""
        return self.set_level(0)

    def set_level(self, level):
        """Display a level on the battery display.

        level should be an integer from 0 to 7.

        Returns True if the TM1651 has sent an ACK after every write."""
        if level not in range(8):
            raise InvalidLevelError(level)

        ack = True

        ack = self.send_command(Command.ADDR_FIXED) and ack
        ack = self.send_command(Command.ADDR_START, LEVEL_TAB[level]) and ack
        ack = self.send_command(Command.DISPLAY_ON + self.brightness) and ack

        return ack

    def half_cycle_clock_low(self, write_data):
        """Start the first half cycle when the clock is low and write a data bit."""
        self.set_clock(LOW)
        sleep(TM1651_CYCLE / 4)

        self.set_data(write_data)
        sleep(TM1651_CYCLE / 4)

    def half_cycle_clock_high(self):
        """Start the second half cycle when the clock is high."""

        self.set_clock(HIGH)
        sleep(TM1651_CYCLE / 2)

    def half_cycle_clock_high_ack(self):
        """Start the second half cycle when the clock is high and check for the ack.

        Returns the ack bit (should be LOW)."""

        # Set CLK high.
        self.set_clock(HIGH)
        sleep(TM1651_CYCLE / 4)

        # Set DIO to input mode and check the ack.
        GPIO.setup(self.data_pin, IN)
        ack = GPIO.input(self.data_pin)

        # ack (DIO) should be LOW now
        # Now we have to set it to LOW ourselves before the TM1651
        # releases the port line at the next clock cycle.
        GPIO.setup(self.data_pin, OUT)
        if not ack:
            self.set_data(LOW)

        sleep(TM1651_CYCLE / 4)
        # Set CLK to low again so it can begin the next cycle.
        self.set_clock(LOW)

        return ack

    def write_byte(self, write_data):
        """Write a byte to the TM1651.

        Returns True if the TM1651 has sent an ack after the write."""
        # Send 8 data bits, LSB first.
        # A data bit can only be written to DIO when CLK is LOW.
        # E.g. write 1 to DIO:
        # CLK ____████
        # DIO __██████
        for _ in range(8):
            self.half_cycle_clock_low(write_data & 0x01)
            self.half_cycle_clock_high()

            # Take the next bit.
            write_data >>= 1

        # After writing 8 bits, start a 9th clock ycle.
        # During the 9th half-cycle of CLK when it is LOW,
        # if we set DIO to HIGH the TM1651 gives an ack by
        # pulling DIO LOW:
        # CLK ____████
        # DIO __█_____
        # Set CLK low, DIO high.
        self.half_cycle_clock_low(HIGH)
        # Return True if the ACK was LOW.
        return not self.half_cycle_clock_high_ack()

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
