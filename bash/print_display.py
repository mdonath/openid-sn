#!/usr/bin/env python3

from Adafruit_LED_Backpack import SevenSegment
import sys

value = sys.argv[1]

display = SevenSegment.SevenSegment()
display.begin()
display.set_brightness(1)
display.print_number_str(str(value))
display.write_display()
