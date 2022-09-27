from machine import Pin, SPI
from utime import sleep_ms, localtime, time
import max7219
import ntptime

hspi = SPI(1, baudrate=10000000, polarity=0, phase=0)
d = max7219.MAX7219(hspi, Pin(15))

p1 = [2, 3, 5, 7, 11, 13, 17]
p2 = [19, 23, 29, 31, 37, 41, 43]

def write_int():
    for i in p1:
        d.write_num(i)
        sleep_ms(200)
    for i in p2:
        d.write_num(-i)
        sleep_ms(200)


def write_float():
    for i in range(-4, 5):
        d.write_num(i/1.618)
        sleep_ms(400)


def write_hex():
    for i in range(0xfcd08000, 0x0, -1):
        d.write_hex(i)
        sleep_ms(500)


def write_byte():
    d.clear()
    for i in range(1, 16):
        d.write_text("% 4d" % i)
        d.write_byte(i, dig=1)
        sleep_ms(200)


def write_text():
    d.clear()
    d.write_text("% 3dh%3d\x01" % (83, 23))  # degree symbol in max7219_map.py
    sleep_ms(800)
    d.write_text("%8.1f\x01" % 23.7)
    sleep_ms(800)
    d.write_text("OPEn", dig=6, clear=1)  # write at specific digit
    sleep_ms(800)
    d.write_text("SOUrCE", dig=7, clear=1)
    sleep_ms(800)


def write_text_scroll(sleep=100):
    d.clear()
    d.write_text_scroll('HELLO Github')


def timer():
    d.clear()
    for i in range(59, 56, -1):
        d.write_text("%04d" % i, dig=4)
        sleep_ms(1000)
    # d.write_text('booooooo')
    # sleep_ms(500)


def write_format_int():
    import gc
    for i in range(1, 500):
        d.write_text("%8d" % gc.mem_free())
        sleep_ms(1000)


def clock():
    try:
        ntptime.settime()
    except OSError:
        d.write_text("Error", clear=1)
        print("ntpserver fail")
        sleep_ms(500)
        return
    t = time() + 3
    while True:
        tm = localtime()
        d.write_text("%02d-%02d-%02d" % (tm[3], tm[4], tm[5]))
        if time() > t:
            break


def demo1():
    write_text_scroll()


def demo2():
    write_int()
    write_float()


def demo3():
    write_hex()
    write_byte()
    write_text()


def demo4():
    timer()
    clock()


def pulse_counter():
    btn = Pin(0, Pin.IN)
    count = 0
    d.write_num(count)
    while True:
        if not btn.value():
            count += 1
            d.write_num(count)
            while not btn.value():
                sleep_ms(1)


def counter():
    # d.clear(1)
    count = 3600
    while True:
        d.write_num(count)
        sleep_ms(1000)
        count += 1


def counter_down():
    d.clear(1)
    count = 20
    while True:
        d.write_num(count)
        sleep_ms(1000)
        count -= 1


print("\n\nRunning MAX7219_V2 Tests")
print("CTRL+C to stop")

counter()

