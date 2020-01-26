# RPi Mini Battery Display

[![Continous Integration](https://github.com/koenvervloesem/rpi-mini-battery-display/workflows/Tests/badge.svg)](https://github.com/koenvervloesem/rpi-mini-battery-display/actions)
[![PyPI package version](https://img.shields.io/pypi/v/rpi-mini-battery-display.svg)](https://pypi.org/project/rpi-mini-battery-display)
[![Python versions](https://img.shields.io/pypi/pyversions/rpi-mini-battery-display.svg)](https://www.python.org)
[![GitHub license](https://img.shields.io/github/license/koenvervloesem/rpi-mini-battery-display.svg)](https://github.com/koenvervloesem/rpi-mini-battery-display/blob/master/LICENSE)

Library and command-line program to control 10-segment mini battery displays based on the TM1651 chip, such as [the ones from Open-Smart](https://aliexpress.com/item/32789343210.html), on a Raspberry Pi.

## System requirements

The rpi-mini-battery-display library is written to run on a Raspberry Pi. It uses the [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) library to communicate with the TM1651 chip and is tested on Python 3.6 and higher.

## Installation

```python
sudo pip3 install rpi-mini-battery-display
```

## Connections

The mini battery display should be connected like this to the Raspberry Pi's GPIO header:

Mini Battery Display | Raspberry Pi
-------------------- | ------------
CLK                  | BCM24
DIO                  | BCM23
VCC                  | 5 V
GND                  | GND

See [pinout.xyz](https://pinout.xyz/) for the Raspberry Pi GPIO pinout.

The CLK and DIO pin can be connected to other pins on the Raspberry Pi, but these are the default values used by the code. If you change the connections, you have to supply the other pin values as parameters to the software.

## Usage

```shell
usage: rpi-mini-battery-display [-h] [-c CLOCK_PIN] [-d DATA_PIN]
                                [-b BRIGHTNESS]
                                level

Control a 10 LED mini battery display with TM1651 chip

positional arguments:
  level                 Battery level (range: 0-7)

optional arguments:
  -h, --help            show this help message and exit
  -c CLOCK_PIN, --clock-pin CLOCK_PIN
                        Clock pin in BCM notation (default: 24, range: 0-27)
  -d DATA_PIN, --data-pin DATA_PIN
                        Data pin in BCM notation (default: 23, range: 0-27)
  -b BRIGHTNESS, --brightness BRIGHTNESS
                        Brightness (default: 2, range: 0-7)
```

## Changelog

* 0.1.0 (2020-01-26): Initial version

## TODO

* Code refactoring, as this project currently is a rather direct Python port of the original C++/Arduino code that came with the mini battery display I bought on AliExpress.
* Individually address the LED segments instead of only using them as a LED bar (fairly trivial to implement).
* Add static typing with [mypy](http://mypy-lang.org/).
* Support other versions of the mini battery displays based on the TM1651 chip, for instance [the 5-segment one](https://aliexpress.com/item/2025558433.html).
* Support other mini battery displays, such as the [Grove LED Bar](https://wiki.seeedstudio.com/Grove-LED_Bar/), which uses the MY9221 chip.

## License

This project is provided by [Koen Vervloesem](mailto:koen@vervloesem.eu) as open source software with the MIT license. See the LICENSE file for more information.
