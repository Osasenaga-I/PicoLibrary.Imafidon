"""
main_kiosk.py
Main entry point for the Restaurant Satisfaction Kiosk.
Uses the PicoLibrary.Imafidon hardware classes.
"""

from Displays import LCDDisplay
from Buzzer import PassiveBuzzer
from LightStrip import LightStrip
from Button import Button
from Sensors_advanced import UltrasonicSensor
from Counters import SoftwareTimer

from FeedbackStats import FeedbackStats
from FeedbackController import FeedbackController


def main():
    print("=" * 50)
    print("Starting Restaurant Satisfaction Kiosk...")
    print("=" * 50)

    # 1. Hardware Pin Configuration
    # Ultrasonic Sensor on GP2 (Trigger) and GP3 (Echo)
    sensor = UltrasonicSensor(trigger=2, echo=3, name="uss", threshold=50.0)

    # Buttons on GP14 (Green) and GP15 (Red)
    green_btn = Button(14, "green", lowActive=True)
    red_btn = Button(15, "red", lowActive=True)

    # LCD Display on GP0 (SDA) and GP1 (SCL)
    display = LCDDisplay(sda=0, scl=1)

    # NeoPixel LightStrip on GP28 (8 LEDs)
    light_strip = LightStrip(pin=28, name="LightStrip", numleds=8)

    # Passive Buzzer on GP18
    buzzer = PassiveBuzzer(pin=18, name="PassiveBuzzer")

    # Software Timer named 'timer' (produces event 'timer_timeout')
    timer = SoftwareTimer(name="timer")

    # 2. Controller Initialization
    controller = FeedbackController(
        sensor=sensor,
        green_button=green_btn,
        red_button=red_btn,
        display=display,
        lightStrip=light_strip,
        buzzer=buzzer,
        timer=timer,
        threshold=30,  # 30% alarm threshold
    )

    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nKiosk stopped.")
        buzzer.stop()
        light_strip.setColor((0, 0, 0), 8)
        display.clear()


if __name__ == "__main__":
    main()
