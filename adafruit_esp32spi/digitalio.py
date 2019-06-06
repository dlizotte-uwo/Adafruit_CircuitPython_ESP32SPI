# The MIT License (MIT)
#
# Copyright (c) 2019 Brent Rubell for Adafruit
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`digitalio`
==============================
DigitalIO for ESP32 over SPI.

* Author(s): Brent Rubell
"""
from micropython import const

class Pin:
    IN = const(0x00)
    OUT = const(0x01)
    LOW = const(0x00)
    HIGH = const(0x01)
    _value = LOW
    _mode = IN
    id = None

    ESP32_GPIO_PINS = set([0, 1, 2, 4, 5,
                            12, 13, 14, 15,
                            16, 17, 18, 19,
                            21, 22, 23, 25,
                            26, 27, 32, 33])
    """
    Implementation of CircuitPython API Pin Handling
    for ESP32SPI.

    :param int esp_pin: Valid ESP32 GPIO Pin, predefined in ESP32_GPIO_PINS.
    :param ESP_SPIcontrol esp: The ESP object we are using.

    NOTE: This class does not currently implement reading digital pins
    or the use of internal pull-up resistors.
    """
    def __init__(self, esp_pin, esp):
        if esp_pin in self.ESP32_GPIO_PINS:
            self.id = esp_pin
        else:
            raise AttributeError("Pin %d is not a valid ESP32 GPIO Pin."%esp_pin)
        self._esp = esp

    def init(self, mode=IN):
        """Initalizes a pre-defined pin.
        :param mode: Pin mode (IN, OUT, LOW, HIGH). Defaults to IN.
        """
        if mode != None:
            if mode == self.IN:
                self._mode = self.IN
                self._esp.set_pin_mode(self.id, 0)
            elif mode == self.OUT:
                self._mode = self.OUT
                self._esp.set_pin_mode(self.id, 1)
            else:
                raise RuntimeError("Invalid mode defined")

    def value(self, val=None):
        """Sets ESP32 Pin GPIO output mode.
        :param val: Pin output level (LOW, HIGH)
        """
        if val != None:
            if val == self.LOW:
                self._value = val
                self._esp.set_digital_write(self.id, 0)
            elif val == self.HIGH:
                self._value = val
                self._esp.set_digital_write(self.id, 1)
            else:
                raise RuntimeError("Invalid value for pin")
        else:
            raise NotImplementedError("digitalRead not currently implemented in esp32spi")

    def __repr__(self):
        return str(self.id)


class DriveMode():
    PUSH_PULL = None
    OPEN_DRAIN = None
DriveMode.PUSH_PULL = DriveMode()
DriveMode.OPEN_DRAIN = DriveMode()


class Direction():
    INPUT = None
    OUTPUT = None
Direction.INPUT = Direction()
Direction.OUTPUT = Direction()


class DigitalInOut():
    """Implementation of DigitalIO module for ESP32SPI.

    :param ESP_SPIcontrol esp: The ESP object we are using.
    :param int pin: Valid ESP32 GPIO Pin, predefined in ESP32_GPIO_PINS.
    """
    _pin = None
    def __init__(self, esp, pin):
        self._esp = esp
        self._pin = Pin(pin, self._esp)
        self.direction = Direction.INPUT

    def __exit__(self):
        self.deinit()

    def deinit(self):
        self._pin = None

    def switch_to_output(self, value=False, drive_mode= DriveMode.PUSH_PULL):
        """Set the drive mode and value and then switch to writing out digital values.
        :param bool value: Default mode to set upon switching.
        :param DriveMode drive_mode: Drive mode for the output.
        """
        self.direction = Direction.OUTPUT
        self.value = value
        self._drive_mode = drive_mode
    
    def switch_to_input(self, pull=None):
        """Sets the pull and then switch to read in digital values.
        :param Pull pull: Pull configuration for the input.
        """
        raise NotImplementedError("Digital reads are not currently supported in ESP32SPI.")

    @property
    def direction(self):
        """Returns the pin's direction."""
        return self.__direction

    @direction.setter
    def direction(self, dir):
        """Sets the direction of the pin.
        :param Direction dir: Pin direction (Direction.OUTPUT or Direction.INPUT)
        """
        self.__direction = dir
        if dir is Direction.OUTPUT:
            self._pin.init(mode=Pin.OUT)
            self.value = False
            self.drive_mode = DriveMode.PUSH_PULL
        elif dir is Direction.INPUT:
            self._pin.init(mode=Pin.IN)
        else:
            raise AttributeError("Not a Direction")

    @property
    def value(self):
        """Returns the digital logic level value of the pin."""
        return self._pin.value() is 1

    @value.setter
    def value(self, val):
        """Sets the digital logic level of the pin.
        :param type value: Pin logic level.
        :param int value: Pin logic level. 1 is logic high, 0 is logic low.
        :param bool value: Pin logic level. True is logic high, False is logic low.
        """
        if self.direction is Direction.OUTPUT:
            self._pin.value(1 if val else 0)
        else:
            raise AttributeError("Not an output")

    @property
    def drive_mode(self):
        """Returns pin drive mode."""
        if self.direction is Direction.OUTPUT:
            return self.__drive_mode
        else:
            raise AttributeError("Not an output")

    @drive_mode.setter
    def drive_mode(self, mode):
        """Sets the pin drive mode.
        :param DriveMode mode: Defines the drive mode when outputting digital values.
        Either PUSH_PULL or OPEN_DRAIN
        """
        self.__drive_mode = mode
        if mode is DriveMode.OPEN_DRAIN:
            self._pin.init(mode=Pin.OPEN_DRAIN)
        elif mode is DriveMode.PUSH_PULL:
            self._pin.init(mode=Pin.OUT)
