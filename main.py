"""
Toothbrush Timer for Pimoroni Pico Unicorn Pack (PIM546)
========================================================
Press Button A to start the timer.
Press Button B at any time to cancel and reset.

Sequence:
  1. 3-second countdown (3... 2... 1... GO!)
  2. 2-minute brushing timer split into 4 x 30-second quadrants
     - Each quadrant gets a distinct colour theme
     - Progress bar counts down across the 16 columns
     - Quadrant change is signalled with a flash burst
  3. Last 10 seconds: faster flashing
  4. Last 5 seconds: even faster flashing
  5. Finish: celebratory rainbow animation

Requires: Pimoroni custom MicroPython firmware with picounicorn module.
Save this file as main.py on your Pico to auto-run on power-up.
"""

import picounicorn
import time
import math

picounicorn.init()

W = picounicorn.get_width()   # 16
H = picounicorn.get_height()  # 7

# --- Colour helpers ---

def hsv_to_rgb(h, s, v):
    """Convert HSV (0-1 range) to RGB (0-255)."""
    if s == 0.0:
        iv = int(v * 255)
        return iv, iv, iv
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    vals = [
        (v, t, p), (q, v, p), (p, v, t),
        (p, q, v), (t, p, v), (v, p, q)
    ]
    r, g, b = vals[i]
    return int(r * 255), int(g * 255), int(b * 255)


def clear():
    """Turn off all LEDs."""
    for x in range(W):
        for y in range(H):
            picounicorn.set_pixel(x, y, 0, 0, 0)


def fill(r, g, b):
    """Set all LEDs to one colour."""
    for x in range(W):
        for y in range(H):
            picounicorn.set_pixel(x, y, r, g, b)


def button_a():
    return picounicorn.is_pressed(picounicorn.BUTTON_A)


def button_b():
    return picounicorn.is_pressed(picounicorn.BUTTON_B)


# --- Quadrant colours (bright, kid-friendly) ---
# Each quadrant of the mouth gets a distinct colour theme
QUADRANT_COLOURS = [
    (0,   180, 255),  # Cyan / blue   - top-left teeth
    (255, 100, 0),    # Orange        - top-right teeth
    (0,   255, 80),   # Green         - bottom-left teeth
    (200, 0,   255),  # Purple        - bottom-right teeth
]

QUADRANT_LABELS = [
    "Top Left",
    "Top Right",
    "Bottom Left",
    "Bottom Right",
]


# --- Animation helpers ---

def flash_burst(r, g, b, flashes=3, on_ms=80, off_ms=80):
    """Quick flash burst to grab attention."""
    for _ in range(flashes):
        if button_b():
            return False
        fill(r, g, b)
        time.sleep_ms(on_ms)
        clear()
        time.sleep_ms(off_ms)
    return True


def countdown_number(n, r, g, b):
    """
    Display a large number (1-3) on the 16x7 grid.
    Simple bitmap digits designed for this resolution.
    """
    clear()

    # 3-wide digit patterns (each row is a list of 0/1), 7 rows tall
    digits = {
        3: [
            [1,1,1,1,1],
            [0,0,0,0,1],
            [0,0,0,0,1],
            [1,1,1,1,1],
            [0,0,0,0,1],
            [0,0,0,0,1],
            [1,1,1,1,1],
        ],
        2: [
            [1,1,1,1,1],
            [0,0,0,0,1],
            [0,0,0,0,1],
            [1,1,1,1,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,1],
        ],
        1: [
            [0,0,1,0,0],
            [0,1,1,0,0],
            [1,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [1,1,1,1,1],
        ],
    }

    if n not in digits:
        return

    pattern = digits[n]
    # Centre the 5-wide pattern on the 16-wide display
    x_offset = (W - 5) // 2  # = 5

    for row in range(7):
        for col in range(5):
            if pattern[row][col]:
                picounicorn.set_pixel(x_offset + col, row, r, g, b)


def rainbow_celebration(duration_s=3):
    """Celebratory rainbow sweep when done."""
    start = time.ticks_ms()
    offset = 0.0
    while time.ticks_diff(time.ticks_ms(), start) < duration_s * 1000:
        if button_b():
            return
        for x in range(W):
            for y in range(H):
                hue = ((x / W) + (y / H) / 2.0 + offset) % 1.0
                r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
                picounicorn.set_pixel(x, y, r, g, b)
        offset += 0.02
        time.sleep_ms(30)


def draw_progress_bar(elapsed_in_quadrant, quadrant_duration, quadrant_index, tick):
    """
    Draw an animated display for the current quadrant:
    - A progress bar that shrinks from right to left as time elapses
    - Sparkle / shimmer effect to keep kids engaged
    - Colour based on current quadrant
    """
    r, g, b = QUADRANT_COLOURS[quadrant_index]
    fraction_remaining = 1.0 - (elapsed_in_quadrant / quadrant_duration)
    cols_lit = max(0, int(fraction_remaining * W + 0.5))

    for x in range(W):
        for y in range(H):
            if x < cols_lit:
                # Shimmer: vary brightness with a wave pattern
                wave = math.sin((x * 0.8) + (y * 0.6) + (tick * 0.15))
                brightness = 0.55 + 0.45 * wave  # range ~0.1 to 1.0
                pr = int(r * brightness)
                pg = int(g * brightness)
                pb = int(b * brightness)
                # Clamp
                pr = min(255, max(0, pr))
                pg = min(255, max(0, pg))
                pb = min(255, max(0, pb))
                picounicorn.set_pixel(x, y, pr, pg, pb)
            else:
                # Dim background - faint trail of the quadrant colour
                picounicorn.set_pixel(x, y, r // 20, g // 20, b // 20)


def draw_flashing_progress(elapsed_in_quadrant, quadrant_duration, quadrant_index,
                           tick, flash_speed):
    """
    Same as progress bar but with a pulsing/flashing overlay.
    flash_speed: lower = faster flashing
    """
    r, g, b = QUADRANT_COLOURS[quadrant_index]
    fraction_remaining = 1.0 - (elapsed_in_quadrant / quadrant_duration)
    cols_lit = max(0, int(fraction_remaining * W + 0.5))

    # Global pulse
    pulse = (math.sin(tick * (6.28 / flash_speed)) + 1.0) / 2.0  # 0-1

    for x in range(W):
        for y in range(H):
            if x < cols_lit:
                wave = math.sin((x * 1.2) + (y * 0.9) + (tick * 0.25))
                brightness = (0.3 + 0.7 * pulse) * (0.6 + 0.4 * wave)
                brightness = min(1.0, max(0.05, brightness))
                picounicorn.set_pixel(x, y,
                                      int(r * brightness),
                                      int(g * brightness),
                                      int(b * brightness))
            else:
                picounicorn.set_pixel(x, y, 0, 0, 0)


# --- Main timer logic ---

def run_countdown():
    """3-second countdown before the timer starts."""
    colours = [
        (255, 50, 50),   # 3 = red
        (255, 200, 0),   # 2 = yellow
        (0,   255, 80),  # 1 = green
    ]
    for i, n in enumerate([3, 2, 1]):
        if button_b():
            return False
        r, g, b = colours[i]
        countdown_number(n, r, g, b)
        time.sleep_ms(900)
        clear()
        time.sleep_ms(100)

    # "GO!" flash
    if not flash_burst(0, 255, 0, flashes=4, on_ms=60, off_ms=60):
        return False
    return True


def run_timer():
    """Main 2-minute brushing timer."""
    total_duration = 120.0  # seconds
    quadrant_duration = 30.0  # seconds per quadrant
    tick = 0

    start_time = time.ticks_ms()

    while True:
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, start_time) / 1000.0

        if elapsed >= total_duration:
            break

        if button_b():
            return False

        remaining = total_duration - elapsed
        quadrant_index = min(3, int(elapsed / quadrant_duration))
        elapsed_in_quadrant = elapsed - (quadrant_index * quadrant_duration)

        # Check if we just entered a new quadrant (first 0.6s of each quadrant)
        if elapsed_in_quadrant < 0.6 and quadrant_index > 0:
            # Flash to signal quadrant change
            r, g, b = QUADRANT_COLOURS[quadrant_index]
            if not flash_burst(r, g, b, flashes=5, on_ms=60, off_ms=60):
                return False
            # Re-sync timing after the flash burst
            now = time.ticks_ms()
            elapsed = time.ticks_diff(now, start_time) / 1000.0
            remaining = total_duration - elapsed
            quadrant_index = min(3, int(elapsed / quadrant_duration))
            elapsed_in_quadrant = elapsed - (quadrant_index * quadrant_duration)

        # Choose animation style based on remaining time
        if remaining <= 5.0:
            # Final 5 seconds - very fast flashing
            draw_flashing_progress(elapsed_in_quadrant, quadrant_duration,
                                   quadrant_index, tick, flash_speed=4)
        elif remaining <= 10.0:
            # Last 10 seconds - faster flashing
            draw_flashing_progress(elapsed_in_quadrant, quadrant_duration,
                                   quadrant_index, tick, flash_speed=8)
        else:
            # Normal animated progress bar with shimmer
            draw_progress_bar(elapsed_in_quadrant, quadrant_duration,
                              quadrant_index, tick)

        tick += 1
        time.sleep_ms(50)  # ~20fps update rate

    return True


def finish_celebration():
    """Timer complete - celebrate!"""
    # Big green flash
    flash_burst(0, 255, 0, flashes=6, on_ms=100, off_ms=80)
    # Rainbow
    rainbow_celebration(duration_s=5)
    # Gentle fade out
    for brightness in range(100, -1, -2):
        b_frac = brightness / 100.0
        for x in range(W):
            for y in range(H):
                hue = (x / W + y / H / 2.0) % 1.0
                r, g, b = hsv_to_rgb(hue, 1.0, b_frac)
                picounicorn.set_pixel(x, y, r, g, b)
        time.sleep_ms(30)
    clear()


def idle_animation():
    """
    Gentle pulsing animation while waiting for button press.
    Soft breathing effect in a calm blue/teal.
    """
    tick = 0
    while True:
        if button_a():
            return True
        if button_b():
            # Easter egg: hold B to show a quick rainbow
            rainbow_celebration(2)
            clear()

        # Gentle breathing pulse
        brightness = (math.sin(tick * 0.05) + 1.0) / 2.0
        brightness = 0.02 + brightness * 0.15  # Keep it subtle (0.02 - 0.17)

        for x in range(W):
            for y in range(H):
                hue = 0.52 + 0.03 * math.sin(x * 0.4 + tick * 0.02)
                r, g, b = hsv_to_rgb(hue, 0.8, brightness)
                picounicorn.set_pixel(x, y, r, g, b)

        tick += 1
        time.sleep_ms(50)


# --- Main loop ---

print("Toothbrush Timer Ready!")
print("Press Button A to start, Button B to cancel at any time.")

while True:
    clear()

    # Wait for button A with a gentle idle animation
    idle_animation()

    # Debounce
    time.sleep_ms(200)

    # Run the countdown
    if not run_countdown():
        continue

    # Run the 2-minute timer
    if not run_timer():
        clear()
        # Cancelled - brief red flash
        flash_burst(255, 0, 0, flashes=2, on_ms=100, off_ms=100)
        continue

    # Done! Celebrate!
    finish_celebration()
