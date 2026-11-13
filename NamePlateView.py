"""
NamePlateView.py
View component managing the LCD display, passive buzzer, and NeoPixel lightstrip.
"""
from Displays import LCDDisplay
from Buzzer import PassiveBuzzer
from LightStrip import LightStrip
from Lights import GREEN, YELLOW, RED, BLACK
from Log import Log

class NamePlateView:
    """
    Handles hardware output: rendering lines of text to the LCD, displaying
    availability color codes on the LightStrip, and emitting buzzer audio feedback.
    """
    def __init__(self, display: LCDDisplay, buzzer: PassiveBuzzer, lightStrip: LightStrip):
        self._display = display
        self._buzzer = buzzer
        self._lightStrip = lightStrip
        Log.i("NamePlateView initialized")

    def render(self, lines: list):
        """
        Renders the provided text lines onto the LCD display (up to 2 lines, 16 chars each).
        """
        self._display.clear()
        for row, text in enumerate(lines[:2]):
            line_str = str(text)[:16]
            self._display.showText(line_str, row=row, col=0)
        Log.i(f"NamePlateView: displayed lines {lines}")

    def showAvailability(self, status: str):
        """
        Updates the LightStrip based on availability status:
        - available -> Green
        - away -> Yellow
        - busy -> Red
        """
        s = str(status).strip().lower()
        if s == "available":
            self._lightStrip.setColor(GREEN)
        elif s == "away":
            self._lightStrip.setColor(YELLOW)
        elif s == "busy":
            self._lightStrip.setColor(RED)
        else:
            self._lightStrip.off()
        Log.i(f"NamePlateView: availability color set for '{status}'")

    def playSound(self):
        """
        Emits an audible feedback chime on the passive buzzer.
        """
        self._buzzer.beep(tone=800, duration=80)
