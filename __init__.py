"""
This project is inspired by yrlfs digiclk and base functionality (clock) is taken from there.
https://github.com/Ferdi265/card10-digiclk

Thanks to lortas for the battery rendering code
"""

import os
import display
import leds
import buttons
import utime

def ceilDiv(a, b):
    return (a + (b - 1)) // b

def tipHeight(w):
    return ceilDiv(w, 2) - 1

def drawTip(d, x, y, w, c, invert = False, swapAxes = False):
    h = tipHeight(w)
    for dy in range(h):
        for dx in range(dy + 1, w - 1 - dy):
            px = x + dx
            py = y + dy if not invert else y + h - 1 - dy
            if swapAxes:
                px, py = py, px
            d.pixel(px, py, col = c)

def drawSeg(d, x, y, w, h, c, swapAxes = False):
    tip_h = tipHeight(w)
    body_h = h - 2 * tip_h

    drawTip(d, x, y, w, c, invert = True, swapAxes = swapAxes)

    px1, px2 = x, x + w
    py1, py2 = y + tip_h, y + tip_h + body_h
    if swapAxes:
        px1, px2, py1, py2 = py1, py2, px1, px2
    d.rect(px1, py1, px2, py2, col = c)

    drawTip(d, x, y + tip_h + body_h, w, c, invert = False, swapAxes = swapAxes)

def drawVSeg(d, x, y, w, l, c):
    drawSeg(d, x, y, w, l, c)

def drawHSeg(d, x, y, w, l, c):
    drawSeg(d, y, x, w, l, c, swapAxes = True)

def drawGridSeg(d, x, y, w, l, c, swapAxes = False):
    sw = w - 2
    tip_h = tipHeight(sw)

    x = x * w
    y = y * w
    l = (l - 1) * w
    drawSeg(d, x + 1, y + tip_h + 3, sw, l - 3, c, swapAxes = swapAxes)

def drawGridVSeg(d, x, y, w, l, c):
    drawGridSeg(d, x, y, w, l, c)

def drawGridHSeg(d, x, y, w, l, c):
    drawGridSeg(d, y, x, w, l, c, swapAxes = True)

def drawGrid(d, x1, y1, x2, y2, w, c):
    for x in range(x1 * w, x2 * w):
        for y in range(y1 * w, y2 * w):
            if x % w == 0 or x % w == w - 1 or y % w == 0 or y % w == w - 1:
                d.pixel(x, y, col = c)

def drawGrid7Seg(d, x, y, w, segs, c):
    if segs[0]:
        drawGridHSeg(d, x, y, w, 4, c)
    if segs[1]:
        drawGridVSeg(d, x + 3, y, w, 4, c)
    if segs[2]:
        drawGridVSeg(d, x + 3, y + 3, w, 4, c)
    if segs[3]:
        drawGridHSeg(d, x, y + 6, w, 4, c)
    if segs[4]:
        drawGridVSeg(d, x, y + 3, w, 4, c)
    if segs[5]:
        drawGridVSeg(d, x, y, w, 4, c)
    if segs[6]:
        drawGridHSeg(d, x, y + 3, w, 4, c)

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

BATTERY_COLOR_GOOD = [  0,230,0]
BATTERY_COLOR_OK   = [255,215,0]
BATTERY_COLOR_BAD  = [255,  0,0]

def get_bat_color(v):
    """
    Function determines the color of the battery indicator. Colors can be set in config.
    Voltage threshold's are currently estimates as voltage isn't that great of an indicator for
    battery charge.
    :return: false if old firmware, RGB color array otherwise
    """
    if v > 3.8:
        return BATTERY_COLOR_GOOD
    if v > 3.6:
        return BATTERY_COLOR_OK
    return BATTERY_COLOR_BAD

def render_battery(d, v):
    """
    Adds the battery indicator to the display. Does not call update or clear so it can be used in addition to
    other display code.
    :param disp: open display
    """
    c = get_bat_color(v)
    if not c:
        return
    d.rect(140, 71, 155, 78, filled=True, col=c)
    d.rect(155, 73, 157, 76, filled=True, col=c)
    if v < 4.0:
        d.rect(151, 72, 154, 77, filled=True, col=[0, 0, 0])
    if v < 3.8:
        d.rect(146, 72, 151, 77, filled=True, col=[0, 0, 0])
    if v < 3.6:
        d.rect(141, 72, 146, 77, filled=True, col=[0, 0, 0])

def get_current_day():
    ltime = utime.localtime()
    wday = ltime[6]
    return DAY_STRING[months]

def renderNum(d, num, x):
    drawGrid7Seg(d, x, 0, 7, DIGITS[num // 10], (255, 255, 255))
    drawGrid7Seg(d, x + 5, 0, 7, DIGITS[num % 10], (255, 255, 255))

def renderColon(d):
    drawGridVSeg(d, 11, 2, 7, 2, (255, 255, 255))
    drawGridVSeg(d, 11, 4, 7, 2, (255, 255, 255))

def renderText(d, text, blankidx = None):
    bs = bytearray(text)

    if blankidx != None:
        bs[blankidx:blankidx+1] = b'_'
    # replace ---(MODE) with wday here --> tenary if --- wday else MODE
    # mode !--- make fg color red

    #global MODE
    if MODE == DISPLAY:
        ltime = utime.localtime()
        wday = ltime[6]
        d.print(DAY_STRING[wday] + bs.decode(), fg = (128, 128, 128), bg = None, posx = 0, posy = 7 * 8)
        else:
        fg_color = (0, 255, 128) if MODE in (CHANGE_YEAR, CHANGE_MONTH, CHANGE_DAY) else (0, 128, 128)
        d.print(MODES[MODE], fg = fg_color, bg = None, posx = 0, posy = 7 * 8)

def renderBar(d, num):
    d.rect(0, 72, 0 + num * 2, 80, col = (int(255 // 52) * num, int(255 // 52) * num, int(255 // 52) * num))

def render(d):
    d.clear()

    ltime = utime.localtime()
    years = ltime[0]
    months = ltime[1]
    days = ltime[2]
    hours = ltime[3]
    mins = ltime[4]
    secs = ltime[5]

    if MODE == CHANGE_YEAR:
        renderNum(d, years // 100, 1)
        renderNum(d, years % 100, 13)
    elif MODE == CHANGE_MONTH:
        renderNum(d, months, 13)
    elif MODE == CHANGE_DAY:
        renderNum(d, days, 13)
    else:
        renderNum(d, hours, 1)
        renderNum(d, mins, 13)

    if MODE not in (CHANGE_YEAR, CHANGE_MONTH, CHANGE_DAY) and secs % 2 == 0:
        renderColon(d)

    formatted_date = "{:02}.".format(days)+MONTH_STRING[months]+str(years)[2:]
    renderText(d, formatted_date, None)
    #renderText(d, NAME, None)
    render_battery(d, os.read_battery())
    renderBar(d, secs)

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
    new = utime.mktime((ltime[0] + yrs, ltime[1] + mth, ltime[2] + day, ltime[3] + hrs, ltime[4] + mns, ltime[5] + sec, None, None))
    utime.set_time(new + WORKAROUND_OFFSET)

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

WORKAROUND_OFFSET = None
def detect_workaround_offset():
    global WORKAROUND_OFFSET

    old = utime.time()
    utime.set_time(old)
    new = utime.time()

    WORKAROUND_OFFSET = old - new
    utime.set_time(old + WORKAROUND_OFFSET)

NAME = None
FILENAME = 'nickname.txt'
def load_nickname():
    global NAME
    if FILENAME in os.listdir('.'):
        with open("nickname.txt", "rb") as f:
            name = f.read().strip()
    else:
        name = b'no nick'

    if len(name) > 7:
        name = name[0:7]
    else:
        name = b' ' * (7 - len(name)) + name

    NAME = name

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
    try:
        detect_workaround_offset()
        load_nickname()
        with display.open() as d:
            while True:
                bs = checkButtons()
                CTRL_FNS[MODE](bs)
                render(d)
    except KeyboardInterrupt:
        pass

main()