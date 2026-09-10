# Toothbrush Timer

A 2-minute toothbrushing timer for the [Pimoroni Pico Unicorn Pack](https://shop.pimoroni.com/products/pico-unicorn-pack) (PIM546), a 16x7 RGB LED display for the Raspberry Pi Pico.

## How it works

- **Idle**: a gentle breathing animation waits for a button press.
- **Press A**: a 3-2-1 countdown, then the 2-minute brushing timer starts, split into four 30-second quadrants (top-left, top-right, bottom-left, bottom-right), each with its own colour and an animated progress bar.
- Flashing speeds up in the last 10 seconds, and again in the last 5 seconds, of each quadrant.
- **Press B**: cancel and reset at any time.
- **Finish**: a celebratory rainbow animation plays once the full 2 minutes is complete.

## Hardware

- Raspberry Pi Pico (or Pico W)
- Pimoroni Pico Unicorn Pack
- MicroPython firmware with the `picounicorn` module (Pimoroni's [custom firmware](https://github.com/pimoroni/pimoroni-pico))

## Installation

1. Flash your Pico with Pimoroni's custom MicroPython firmware (includes the `picounicorn` module).
2. Copy [`main.py`](main.py) to the Pico's filesystem, e.g. using [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) in VS Code or `rshell`/`mpremote`.
3. The Pico will run the timer automatically on power-up.

## Usage

- Press **Button A** to start.
- Press **Button B** at any time to cancel and return to idle.
