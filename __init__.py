"""
This project is inspired by yrlfs digiclk and base functionality (clock) is taken from there.
https://github.com/Ferdi265/card10-digiclk

Thanks to lortas for the battery rendering code
"""

import buttons
import display
import os
import utime
import light_sensor
import power


def ceil_div(a, b):
    return (a + (b - 1)) // b


def tip_height(w):
    return ceil_div(w, 2) - 1


def draw_tip(d, x, y, w, c, invert=False, swapAxes=False):
    h = tip_height(w)
    for dy in range(h):
        for dx in range(dy + 1, w - 1 - dy):
            px = x + dx
            py = y + dy if not invert else y + h - 1 - dy
            if swapAxes:
                px, py = py, px
            d.pixel(px, py, col=c)


def draw_seg(d, x, y, w, h, c, swapAxes=False):
    tip_h = tip_height(w)
    body_h = h - 2 * tip_h

    draw_tip(d, x, y, w, c, invert=True, swapAxes=swapAxes)

    px1, px2 = x, x + (w - 1)
    py1, py2 = y + tip_h, y + tip_h + (body_h - 1)
    if swapAxes:
        px1, px2, py1, py2 = py1, py2, px1, px2
    d.rect(px1, py1, px2, py2, col=c)

    draw_tip(d, x, y + tip_h + body_h, w, c, invert=False, swapAxes=swapAxes)


def draw_Vseg(d, x, y, w, l, c):
    draw_seg(d, x, y, w, l, c)


def draw_Hseg(d, x, y, w, l, c):
    draw_seg(d, y, x, w, l, c, swapAxes=True)


def draw_grid_seg(d, x, y, w, l, c, swapAxes=False):
    sw = w - 2
    tip_h = tip_height(sw)

    x = x * w
    y = y * w
    l = (l - 1) * w
    draw_seg(d, x + 1, y + tip_h + 3, sw, l - 3, c, swapAxes=swapAxes)


def draw_grid_Vseg(d, x, y, w, l, c):
    draw_grid_seg(d, x, y, w, l, c)


def draw_grid_Hseg(d, x, y, w, l, c):
    draw_grid_seg(d, y, x, w, l, c, swapAxes=True)


def draw_grid(d, x1, y1, x2, y2, w, c):
    for x in range(x1 * w, x2 * w):
        for y in range(y1 * w, y2 * w):
            if x % w == 0 or x % w == w - 1 or y % w == 0 or y % w == w - 1:
                d.pixel(x, y, col=c)


def draw_grid_7seg(d, x, y, w, segs, c):
    if segs[0]:
        draw_grid_Hseg(d, x, y, w, 4, c)
    if segs[1]:
        draw_grid_Vseg(d, x + 3, y, w, 4, c)
    if segs[2]:
        draw_grid_Vseg(d, x + 3, y + 3, w, 4, c)
    if segs[3]:
        draw_grid_Hseg(d, x, y + 6, w, 4, c)
    if segs[4]:
        draw_grid_Vseg(d, x, y + 3, w, 4, c)
    if segs[5]:
        draw_grid_Vseg(d, x, y, w, 4, c)
    if segs[6]:
        draw_grid_Hseg(d, x, y + 3, w, 4, c)


DIGITS = [
    (True, True, True, True, True, True, False),
    (False, True, True, False, False, False, False),
    (True, True, False, True, True, False, True),
    (True, True, True, True, False, False, True),
    (False, True, True, False, False, True, True),
    (True, False, True, True, False, True, True),
    (True, False, True, True, True, True, True),
    (True, True, True, False, False, False, False),
    (True, True, True, True, True, True, True),
    (True, True, True, True, False, True, True)
]

MONTH_STRING = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_STRING = ["Mo-", "Tu-", "We-", "Th-", "Fr-", "Sa-", "Su-"]

BATTERY_COLOR_GOOD = [0, 230, 0]
BATTERY_COLOR_OK = [255, 215, 0]
BATTERY_COLOR_BAD = [255, 0, 0]


def get_bat_color(v):
    if v > 3.8:
        return BATTERY_COLOR_GOOD
    if v > 3.6:
        return BATTERY_COLOR_OK
    return BATTERY_COLOR_BAD


def render_battery(display, v):
    c = get_bat_color(v)
    if not c:
        return
    display.rect(140, 72, 155, 79, filled=True, col=c)
    display.rect(155, 74, 157, 77, filled=True, col=c)
    if v < 4.0:
        display.rect(151, 73, 154, 78, filled=True, col=[0, 0, 0])
    if v < 3.8:
        display.rect(146, 73, 151, 78, filled=True, col=[0, 0, 0])
    if v < 3.6:
        display.rect(141, 73, 146, 78, filled=True, col=[0, 0, 0])


def render_charging(display):
    v_in = power.read_chargein_voltage()
    if v_in > 4.0:
        c = [255, 255, 255]
        c_shade = [120, 120, 120]
        display.pixel(134, 72, col=c)
        display.pixel(135, 72, col=c_shade)
        display.pixel(134, 73, col=c)
        display.pixel(133, 73, col=c_shade)
        display.pixel(134, 74, col=c)
        display.pixel(133, 74, col=c)
        display.pixel(133, 75, col=c)
        display.pixel(134, 75, col=c)
        display.pixel(135, 75, col=c)
        display.pixel(136, 75, col=c_shade)
        display.pixel(135, 76, col=c)
        display.pixel(136, 76, col=c)
        display.pixel(137, 76, col=c)
        display.pixel(134, 76, col=c_shade)
        display.pixel(136, 77, col=c)
        display.pixel(137, 77, col=c)
        display.pixel(136, 78, col=c)
        display.pixel(137, 78, col=c_shade)
        display.pixel(136, 79, col=c)
        display.pixel(135, 79, col=c_shade)


def render_num(d, num, x):
    draw_grid_7seg(d, x, 0, 7, DIGITS[num // 10], (255, 255, 255))
    draw_grid_7seg(d, x + 5, 0, 7, DIGITS[num % 10], (255, 255, 255))


def render_colon(d):
    draw_grid_Vseg(d, 11, 2, 7, 2, (255, 255, 255))
    draw_grid_Vseg(d, 11, 4, 7, 2, (255, 255, 255))


def render_text(d, text, blankidx=None):
    bs = bytearray(text)

    if blankidx is not None:
        bs[blankidx:blankidx + 1] = b'_'
    if MODE == DISPLAY:
        ltime = utime.localtime()
        wday = ltime[6]
        d.print(DAY_STRING[wday] + bs.decode(), fg=(128, 128, 128), bg=None, posx=0, posy=7 * 8)
    else:
        fg_color = (0, 255, 128) if MODE in (CHANGE_YEAR, CHANGE_MONTH, CHANGE_DAY) else (0, 128, 128)
        d.print(MODES[MODE], fg=fg_color, bg=None, posx=0, posy=7 * 8)


def render_bar(d, num):
    d.rect(0, 72, 0 + num * 2, 80, col=(int(255 // 52) * num, int(255 // 52) * num, int(255 // 52) * num))


def render(d):
    d.clear()

    year, month, mday, hour, min, sec, wday, yday = utime.localtime()

    if MODE == CHANGE_YEAR:
        render_num(d, year // 100, 1)
        render_num(d, year % 100, 13)
    elif MODE == CHANGE_MONTH:
        render_num(d, month, 13)
    elif MODE == CHANGE_DAY:
        render_num(d, mday, 13)
    else:
        render_num(d, hour, 1)
        render_num(d, min, 13)

    if MODE not in (CHANGE_YEAR, CHANGE_MONTH, CHANGE_DAY) and sec % 2 == 0:
        render_colon(d)

    formatted_date = "{:02}.".format(mday) + MONTH_STRING[month - 1] + str(year)[2:]
    render_text(d, formatted_date, None)
    render_battery(d, os.read_battery())
    render_charging(d)
    render_bar(d, sec)

    d.update()


BUTTON_SEL = 1 << 0
BUTTON_UP = 1 << 1
BUTTON_DOWN = 1 << 2
BUTTON_SEL_LONG = 1 << 3
BUTTON_UP_LONG = 1 << 4
BUTTON_DOWN_LONG = 1 << 5
pressed_prev = 0
button_sel_time = 0
button_up_time = 0
button_down_time = 0


def checkButtons():
    global pressed_prev, button_sel_time, button_up_time, button_down_time

    t = utime.time()
    pressed = buttons.read(buttons.BOTTOM_LEFT | buttons.TOP_RIGHT | buttons.BOTTOM_RIGHT)
    cur_buttons = 0

    if pressed & buttons.BOTTOM_LEFT and not pressed_prev & buttons.BOTTOM_LEFT:
        button_sel_time = t
    elif not pressed & buttons.BOTTOM_LEFT and pressed_prev & buttons.BOTTOM_LEFT:
        if button_sel_time < t:
            cur_buttons |= BUTTON_SEL_LONG
        else:
            cur_buttons |= BUTTON_SEL

    if pressed & buttons.TOP_RIGHT and not pressed_prev & buttons.TOP_RIGHT:
        button_sel_time = t
    elif not pressed & buttons.TOP_RIGHT and pressed_prev & buttons.TOP_RIGHT:
        if button_sel_time < t:
            cur_buttons |= BUTTON_UP_LONG
        else:
            cur_buttons |= BUTTON_UP

    if pressed & buttons.BOTTOM_RIGHT and not pressed_prev & buttons.BOTTOM_RIGHT:
        button_sel_time = t
    elif not pressed & buttons.BOTTOM_RIGHT and pressed_prev & buttons.BOTTOM_RIGHT:
        if button_sel_time < t:
            cur_buttons |= BUTTON_DOWN_LONG
        else:
            cur_buttons |= BUTTON_DOWN

    pressed_prev = pressed
    return cur_buttons


def modTime(yrs, mth, day, hrs, mns, sec):
    ltime = utime.localtime()
    new = utime.mktime(
        (ltime[0] + yrs, ltime[1] + mth, ltime[2] + day, ltime[3] + hrs, ltime[4] + mns, ltime[5] + sec, None, None))
    utime.set_time(new)


def ctrl_display(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = CHANGE_HOURS


def ctrl_chg_hrs(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_MINUTES
    if bs & BUTTON_UP or bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 1, 0, 0)
    if bs & BUTTON_DOWN or bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, -1, 0, 0)


def ctrl_chg_mns(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_SECONDS
    if bs & BUTTON_UP or bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 0, 1, 0)
    if bs & BUTTON_DOWN or bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, 0, -1, 0)


def ctrl_chg_sec(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_YEAR
    if bs & BUTTON_UP or bs & BUTTON_UP_LONG:
        modTime(0, 0, 0, 0, 0, 1)
    if bs & BUTTON_DOWN or bs & BUTTON_DOWN_LONG:
        modTime(0, 0, 0, 0, 0, -1)


def ctrl_chg_yrs(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_MONTH
    if bs & BUTTON_UP or bs & BUTTON_UP_LONG:
        modTime(1, 0, 0, 0, 0, 0)
    if bs & BUTTON_DOWN or bs & BUTTON_DOWN_LONG:
        modTime(-1, 0, 0, 0, 0, 0)


def ctrl_chg_mth(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_DAY
    if bs & BUTTON_UP or bs & BUTTON_UP_LONG:
        modTime(0, 1, 0, 0, 0, 0)
    if bs & BUTTON_DOWN or bs & BUTTON_DOWN_LONG:
        modTime(0, -1, 0, 0, 0, 0)


def ctrl_chg_day(bs):
    global MODE
    if bs & BUTTON_SEL_LONG:
        MODE = DISPLAY
    if bs & BUTTON_SEL:
        MODE = CHANGE_HOURS
    if bs & BUTTON_UP or bs & BUTTON_UP_LONG:
        modTime(0, 0, 1, 0, 0, 0)
    if bs & BUTTON_DOWN or bs & BUTTON_DOWN_LONG:
        modTime(0, 0, -1, 0, 0, 0)


def ctrl_backlight(d):
    brightness = light_sensor.get_reading()
    if brightness > 30:
        d.backlight(100)
    if brightness <= 30 & brightness > 25:
        d.backlight(50)
    if brightness <= 25 & brightness > 20:
        d.backlight(40)
    if brightness <= 20 & brightness > 18:
        d.backlight(30)
    if brightness <= 18 & brightness > 12:
        d.backlight(15)
    if brightness <= 12:
        d.backlight(1)

    d.update()


# MODE values
DISPLAY = 0
CHANGE_HOURS = 1
CHANGE_MINUTES = 2
CHANGE_SECONDS = 3
CHANGE_YEAR = 4
CHANGE_MONTH = 5
CHANGE_DAY = 6

MODE = DISPLAY
MODES = {
    DISPLAY: '---',
    CHANGE_HOURS: '>-----HOURS',
    CHANGE_MINUTES: '>---MINUTES',
    CHANGE_SECONDS: '>---SECONDS',
    CHANGE_YEAR: '>------YEAR',
    CHANGE_MONTH: '>-----MONTH',
    CHANGE_DAY: '>-------DAY',
}

CTRL_FNS = {
    DISPLAY: ctrl_display,
    CHANGE_HOURS: ctrl_chg_hrs,
    CHANGE_MINUTES: ctrl_chg_mns,
    CHANGE_SECONDS: ctrl_chg_sec,
    CHANGE_YEAR: ctrl_chg_yrs,
    CHANGE_MONTH: ctrl_chg_mth,
    CHANGE_DAY: ctrl_chg_day,
}


def main():
    light_sensor.start()
    with display.open() as d:
        while True:
            bs = checkButtons()
            CTRL_FNS[MODE](bs)
            ctrl_backlight(d)
            render(d)
            utime.sleep_ms(200)


main()
