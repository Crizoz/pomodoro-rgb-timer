
import array, time
from machine import Pin
import rp2


NUM_LEDS = 16
PIN_NUM = 16
brightness = 0.2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

sm.active(1)

ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        time.sleep(wait)
        pixels_show()
    time.sleep(0.2)
 
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
 
 
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(wait)

# Cambia los colores del gradiente progresivamente
def cambiando_color(lista_colores, segundos):
    timer_s = time.time()
    total = len(lista_colores) - 1
    each_time = segundos // total
    iterador = 0
    while iterador < len(lista_colores) - 1:
        r_dif = (lista_colores[iterador + 1][0] - lista_colores[iterador][0]) / each_time
        g_dif = (lista_colores[iterador + 1][1] - lista_colores[iterador][1]) / each_time
        b_dif = (lista_colores[iterador + 1][2] - lista_colores[iterador][2]) / each_time
        r = lista_colores[iterador][0]
        g = lista_colores[iterador][1]
        b = lista_colores[iterador][2]
        for n in range(each_time):
            timer_f = time.time()
            if timer_f - timer_s >= segundos:
                break
            else:
                time.sleep(1)
            color = (int(r), int(g), int(b))
            pixels_fill(color)
            pixels_show()
            r += r_dif
            g += g_dif
            b += b_dif
        iterador += 1
    timer_f = time.time()
    if (timer_f - timer_s) < segundos:
        time.sleep(segundos - (timer_f - timer_s))


def standar_pomodoro(color1, color2):
    times = [25, 5] * 4 + [10]
    for t in times:
        cambiando_color(color1 if t == 25 else color2, t)

start = time.time()
standar_pomodoro(
    [(0, 81, 135), (51, 108, 165), (85, 137, 196), (116, 167, 228), (152, 192, 246)],
    [(229, 43, 80), (244, 74, 108), (249, 106, 134), (250, 137, 159 ), (255, 163, 182)]
)
stop = time.time()
print(stop-start)
