"""
MIT License

Copyright (c) 2021 ricardo4nic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from micropython import const
from utime import sleep_ms
try:
    from max7219_map import SYMBOLS_MAP
except:
    SYMBOLS_MAP = {}

try:
    from max7219_map import CHAR_MAP
except:
    CHAR_MAP = {}

NOOP = const(0x0)  # Used when cascading Max7219
DIGIT0 = const(0x1)
DIGIT1 = const(0x2)
DIGIT2 = const(0x3)
DIGIT3 = const(0x4)
DIGIT4 = const(0x5)
DIGIT5 = const(0x6)
DIGIT6 = const(0x7)
DIGIT7 = const(0x8)
DECODEMODE = const(0x9)  # (0 = no decode/raw segment values, 1 = decode only digit 0, 0xFF = decode on all digits)
INTENSITY = const(0xA)  # (0 = lowest intensity, 0xF = max intensity)
SCANLIMIT = const(0xB)  # (0 = display digit 0 only, 7 = display all 7 digits)
SHUTDOWN = const(0xC)  # (0 = shutdown, 1 = normal operation)
DISPLAYTEST = const(0xF)  # (0 = normal mode, 1 = test mode)

HEX_MAP = {0x0: 0b1111110, 0x1: 0b0110000, 0x2: 0b1101101, 0x3: 0b1111001, 0x4: 0b0110011, 0x5: 0b1011011,
           0x6: 0b1011111, 0x7: 0b1110000, 0x8: 0b1111111, 0x9: 0b1111011, 0xA: 0b1110111, 0xB: 0b0011111,
           0xC: 0b1001110, 0xD: 0b0111101, 0xE: 0b1001111, 0xF: 0b1000111}


class MAX7219:
    CONST_TEST = const(255)
    
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.cs.init(cs.OUT, True)
        self.init()

    def register(self, command, data):
        self.cs.off()
        self.spi.write(bytearray([command, data]))
        self.cs.on()

    def init(self):
        for command, data in (
                (DISPLAYTEST, 0),
                (SCANLIMIT, 7),  # Display all 7 digits
                (DECODEMODE, 0xFF),  # Decode all digits
                (INTENSITY, 0x3),  # Set brightness to 3
                (SHUTDOWN, 1),  # Turn display on
        ):
            self.register(command, data)
            # self.clear()


    def test(self, t=500):
        self.register(DISPLAYTEST, 1)
        sleep_ms(t)
        self.register(DISPLAYTEST, 0)

    def brightness(self, value):
        if 0 <= value <= 15:
            self.register(INTENSITY, value)
        else:
            return -1

    def clear(self, decoder_mode=None):
        """
        Set DECODEMODE and clear display
        """

        self.register(SHUTDOWN, 0)  # avoid flash in change mode

        if decoder_mode is None:
            self.register(DECODEMODE, 0x00)
            value = 0x00  # blank
        else:
            self.register(DECODEMODE, 0xFF)
            value = 0x0F  # blank

        for i in range(8):
            self.register(DIGIT0 + i, value)

        self.register(SHUTDOWN, 1)

    def write_byte(self, value=0, dig=DIGIT0):
        """
        write any byte directly to dig=[8..1] register
        """
        self.register(DECODEMODE, 0x00)
        if 1 <= dig <= 8:
            self.register(dig, value)
        else:
            return -1

    def write_num(self, value=0):
        """
        write int or float
        """
        self.clear(1)  # clear in DECODEMODE 0xFF

        if value < 0:
            str_value = str(abs(value))
            isneg = True
        else:
            str_value = str(value)
            isneg = False

        dp = str_value.find('.')
        if dp > 0:
            str_value = str_value.replace('.','')
            if not str_value.isdigit():
                self.register(DIGIT0, 0x0B)  # ERROR
                return -1
            value = int(str_value)
            if isneg:
                value = -value
            dp = len(str_value) - dp


        if -9999999 <= value <= 99999999:
            if value < 0:
                value = -value
            for i in range(8):
                if i == dp:
                    self.register(DIGIT0 + i, (value % 10) | 128)
                else:
                    self.register(DIGIT0 + i, value % 10)
                value = value // 10
                if (value == 0 and i >= dp) or (value == 0 and dp == -1):
                    if isneg:
                        self.register(DIGIT0 + i + 1, 0x0A)  # MINUS
                    break
        else:
            self.register(DIGIT0, 0x0B)  # ERROR
            return -1


    def write_hex(self, value):
        """
        write positive number in hex format
        """
        self.clear()

        if 0 <= value <= 0xFFFFFFFF:
            for i in range(8):
                self.register(DIGIT0 + i, HEX_MAP[value % 16])
                value = value // 16
                if value == 0:
                    break
        else:
            self.register(DIGIT2, 0x4F)  # E
            self.register(DIGIT1, 0x05)  # r
            self.register(DIGIT0, 0x05)  # r
            return -1

    def write_text(self, msg, dig=DIGIT7, clear=None):
        """
        write string
        dig = [8..1] represents DIGIT to start write
        """

        if clear is None:
            self.register(DECODEMODE, 0)
        else:
            self.clear()

        if dig < 1 or dig > 8:  # or (len(msg) > dig):
            return -1

        buf = self._str_to_buf(msg)

        limit = dig if len(buf) > dig else len(buf)

        for i in range(limit):
            self.register(dig - i, buf[i])


    def write_text_scroll(self, msg, start='        ', end='        ', delay=200):
        """
        write string with scroll
        """
        self.register(DECODEMODE, 0)
        msg = start + msg + end

        if len(msg) < 8:
            return -1

        buf = self._str_to_buf(msg)

        for r in range(len(buf) - 7):
            for i in range(8):
                self.register(DIGIT7 - i, buf[i])
            sleep_ms(delay)
            buf.pop(0)
            buf.append(0)

    def _str_to_buf(self, msg):
        buf = []
        idx = 0
        for char in msg:
            if char.isdigit():
                c = HEX_MAP[int(char)]
            else:
                c = CHAR_MAP.get(char)
                if c is None:
                    c = SYMBOLS_MAP.get(ord(char), ord(char))
            if char == '.' and idx > 0:
                buf[idx-1] |= 128
            else:
                buf.append(c)
                idx += 1

        return buf
