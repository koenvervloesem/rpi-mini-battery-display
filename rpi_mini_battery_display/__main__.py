"""Command-line program to control a mini battery display.

Copyright (C) 2020-2021 Koen Vervloesem

SPDX-License-Identifier: MIT
"""
import argparse
import sys
from time import sleep

from psutil import cpu_percent
from RPi.GPIO import cleanup  # pylint: disable=no-name-in-module

from rpi_mini_battery_display import BatteryDisplay
from rpi_mini_battery_display.exceptions import (
    InvalidBrightnessError,
    InvalidLevelError,
    InvalidPinError,
    InvalidSegmentsError,
    NoDisplayFoundError,
)


def main():
    """Main method."""
    parser = argparse.ArgumentParser(
        prog="rpi-mini-battery-display",
        description="Control a mini battery display with TM1651 or TM1637 chip",
    )
    parser.add_argument(
        "-c",
        "--clock-pin",
        type=int,
        default=24,
        help="Clock pin in BCM notation (default: 24, range: 0-27)",
    )
    parser.add_argument(
        "-d",
        "--data-pin",
        type=int,
        default=23,
        help="Data pin in BCM notation (default: 23, range: 0-27)",
    )
    parser.add_argument(
        "-b",
        "--brightness",
        type=int,
        default=2,
        help="Brightness (default: 2, range: 0-7)",
    )
    parser.add_argument(
        "-s",
        "--segments",
        type=int,
        default=7,
        help="Number of LED segments (default: 7, range: 1-7)",
    )

    command = parser.add_mutually_exclusive_group(required=True)

    command.add_argument(
        "-l", "--level", type=int, help="Set battery level (range: 0-segments)"
    )
    command.add_argument(
        "-p", "--processor", action="store_true", help="Show CPU percentage"
    )

    args = parser.parse_args()

    exit_code = 0
    try:
        display = BatteryDisplay(args.clock_pin, args.data_pin, args.segments)
        display.set_brightness(args.brightness)
        if args.level:
            display.set_level(args.level)
        elif args.processor:
            while True:
                # Map a percentage from 0 to 100 to a level from 0 to number of segments
                display.set_level(
                    min(int(cpu_percent() / 100 * (args.segments + 1)), args.segments)
                )
                sleep(2)
    except InvalidPinError as error:
        print("Invalid pin number: {}. {}".format(error.pin, str(error)))
        exit_code = 1
    except InvalidBrightnessError as error:
        print("Invalid brightness: {}. {}".format(error.brightness, str(error)))
        exit_code = 2
    except InvalidLevelError as error:
        print("Invalid level: {}. {}".format(error.level, str(error)))
        exit_code = 3
    except NoDisplayFoundError as error:
        print(
            "No display found on clock pin {} and data pin {}.".format(
                error.clock_pin, error.data_pin
            )
        )
        exit_code = 4
    except InvalidSegmentsError as error:
        print("Invalid number of segments: {}. {}".format(error.segments, str(error)))
        exit_code = 5
    finally:
        if exit_code != 1:
            cleanup()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
