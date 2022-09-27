# MicroPython MAX7219 7-Segment

Micropython driver for a 8 digits 7-segment display module based on the MAX7219 

## Tested on ESP8266 (Nodemcu)

|				|				|
|-------------------------------|-------------------------------|
| ![Alt Text](/media/01.gif)	| ![Alt Text](/media/02.gif)	|
| ![Alt Text](/media/03.gif)	| ![Alt Text](/media/04.gif)	|

## Wiring:

| ESP8266        | MAX7219 |
| ---------      | ------- |
| HMOSI (GPIO13) | DIN     |
| HSCLK (GPIO14) | CLK     |
| I/O (GPIO15)   | CS      |

The I/0 pin can be moved to any other pin.

I'm using the hardware SPI, but it can be moved to any other pin using the software SPI.

## Example of use:

```python
from machine import Pin, SPI
import max7219
	
hspi = SPI(1, baudrate=10000000, polarity=0, phase=0)
d = max7219.MAX7219(hspi, Pin(15))

d.clear()
d.write_num(147)
d.write_num(-18)
d.write_num(1608.27)
d.write_hex(255)
d.write_hex(0x3ff)
d.write_hex(0x3FF)
d.clear()
d.write_byte(0x2a)
d.write_text('HELLO')
d.write_text('OPEn', dig=6, clear=1)
d.write_text("%8.1f\x01" % 17.4) 
d.write_text_scroll("HELLO Github \x2a")
 ```
    
    
I started in https://github.com/JulienBacquart/micropython-max7219
