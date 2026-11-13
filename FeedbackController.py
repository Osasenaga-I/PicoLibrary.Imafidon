"""
FeedbackController.py
Controller class implementing the restaurant satisfaction kiosk finite state machine.
Matches the UML class diagram attributes, methods, and Statechart specifications.
Compatible with PicoLibrary.Imafidon modules.
"""

import time

# Ensure MicroPython time methods exist if running under standard Python
if not hasattr(time, "ticks_ms"):
    time.ticks_ms = lambda: int(time.time() * 1000)
if not hasattr(time, "ticks_diff"):
    time.ticks_diff = lambda a, b: a - b
if not hasattr(time, "sleep_ms"):
    time.sleep_ms = lambda ms: time.sleep(ms / 1000.0)

# Import from PicoLibrary.Imafidon modules or local PicoLibrary
try:
    from Counters import SoftwareTimer
    from Sensors_advanced import UltrasonicSensor
    from Displays import LCDDisplay
    from LightStrip import LightStrip
    from Buzzer import PassiveBuzzer
    from Button import Button
    from StateModel import StateModel
except ImportError:
    try:
        from PicoLibrary import (
            Button,
            UltrasonicSensor,
            LCDDisplay,
            LightStrip,
            PassiveBuzzer,
            SoftwareTimer,
            StateModel,
        )
    except ImportError:
        from Button import Button
        from UltrasonicSensor import UltrasonicSensor
        from LCDDisplay import LCDDisplay
        from LightStrip import LightStrip
        from PassiveBuzzer import PassiveBuzzer
        from SoftwareTimer import SoftwareTimer
        from StateModel import StateModel

from FeedbackStats import FeedbackStats


class FeedbackController:
    # State constants matching Statechart diagram (States 0 through 4)
    STATE_WELCOME = 0
    STATE_SELECTION = 1
    STATE_HAPPY = 2
    STATE_UNHAPPY = 3
    STATE_ALARM = 4

    def __init__(
        self,
        sensor: UltrasonicSensor,
        green_button: Button,
        red_button: Button,
        display: LCDDisplay,
        lightStrip: LightStrip,
        buzzer: PassiveBuzzer,
        timer: SoftwareTimer,
        threshold: int = 30,
    ):
        # Attributes matching UML Class Diagram
        self._model: StateModel = StateModel(5, self, debug=True)
        self._stats: FeedbackStats = FeedbackStats()
        self._sensor: UltrasonicSensor = sensor
        self._green_button: Button = green_button
        self._red_button: Button = red_button
        self._display: LCDDisplay = display
        self._lightStrip: LightStrip = lightStrip
        self._buzzer: PassiveBuzzer = buzzer
        self._timer: SoftwareTimer = timer
        self._threshold: int = threshold
        self._alarm_silenced: bool = False

        # Non-blocking 2-tone alarm tracking
        self._alarm_last_toggle = 0
        self._alarm_tone_high = False

        # Register event handlers for buttons and software timer
        if hasattr(self._timer, "setHandler"):
            self._timer.setHandler(self.timeout)
        self._green_button.setHandler(self._on_green_press)
        self._red_button.setHandler(self._on_red_press)

        # Register input devices with StateModel
        self._model.addButton(self._green_button)
        self._model.addButton(self._red_button)
        self._model.addSensor(self._sensor)
        if hasattr(self._model, "addTimer"):
            self._model.addTimer(self._timer)

        # Register custom event for threshold alarm if supported
        if hasattr(self._model, "addCustomEvent"):
            self._model.addCustomEvent("feedback_below_threshold")

        # Configure transitions
        self._setup_transitions()

    def _add_trans(self, from_state: int, event: str, to_state: int):
        """Helper to add transition supporting both list and string event args."""
        try:
            self._model.addTransition(from_state, [event], to_state)
        except (TypeError, ValueError):
            self._model.addTransition(from_state, event, to_state)

    def _setup_transitions(self):
        """Configures legal transitions strictly adhering to the Statechart."""
        # State 0 - Welcome: uss_trip -> State 1 (Selection)
        self._add_trans(self.STATE_WELCOME, "uss_trip", self.STATE_SELECTION)

        # State 1 - Selection:
        # green_press -> State 2 (happy)
        # red_press   -> State 3 (unhappy)
        # timer_timeout -> State 0 (Welcome)
        self._add_trans(self.STATE_SELECTION, "green_press", self.STATE_HAPPY)
        self._add_trans(self.STATE_SELECTION, "red_press", self.STATE_UNHAPPY)
        self._add_trans(self.STATE_SELECTION, "timer_timeout", self.STATE_WELCOME)

        # State 2 - happy: timer_timeout -> State 0 (Welcome)
        self._add_trans(self.STATE_HAPPY, "timer_timeout", self.STATE_WELCOME)

        # State 3 - unhappy:
        # timer_timeout -> State 0 (Welcome)
        # feedback_below_threshold -> State 4 (Alarm)
        self._add_trans(self.STATE_UNHAPPY, "timer_timeout", self.STATE_WELCOME)
        self._add_trans(self.STATE_UNHAPPY, "feedback_below_threshold", self.STATE_ALARM)

        # State 4 - Alarm:
        # ONLY green_press exits Alarm to State 0 (Welcome)
        self._add_trans(self.STATE_ALARM, "green_press", self.STATE_WELCOME)
        # Note: red_press is an in-state event and handled by stateEvent()

    # ==========================================
    # INPUT EVENT DISPATCHERS
    # ==========================================
    def _on_green_press(self):
        """Dispatched when green button is pressed."""
        self._model.processEvent("green_press")

    def _on_red_press(self):
        """Dispatched when red button is pressed."""
        # Process through model; if it's an in-state event, stateEvent handles it
        if not self._model.processEvent("red_press"):
            self.stateEvent(self._model.current_state, "red_press")

    def timeout(self, name=None):
        """Dispatched by SoftwareTimer when duration expires."""
        self._model.processEvent("timer_timeout")

    # ==========================================
    # STATE MACHINE LIFECYCLE CALLBACKS
    # ==========================================
    def stateEntered(self, state: int, event: str = None):
        """Dispatches to the corresponding state entry method."""
        if state == self.STATE_WELCOME:
            self.welcome()
        elif state == self.STATE_SELECTION:
            self.selection()
        elif state == self.STATE_HAPPY:
            self.happy()
        elif state == self.STATE_UNHAPPY:
            self.unhappy()
        elif state == self.STATE_ALARM:
            self.alarm()

    def stateLeft(self, state: int, event: str = None):
        """Implements state exit actions."""
        # States 1, 2, 3: 'exit / cancel timer'
        if state in (self.STATE_SELECTION, self.STATE_HAPPY, self.STATE_UNHAPPY):
            self._timer.cancel()

        # State 4: 'exit / stop alarm; light strip off; reset stats'
        elif state == self.STATE_ALARM:
            self._buzzer.stop()
            self._lightStrip.setColor((0, 0, 0), self._lightStrip._numleds)
            self._stats.reset()
            self._alarm_silenced = False

    def stateEvent(self, state: int, event: str):
        """Handles in-state (internal) events that do not cause a state exit."""
        # State 4: 'red_press / stop alarm/ reset stats; display 'Alarm stopped''
        if state == self.STATE_ALARM and event == "red_press":
            self._alarm_silenced = True
            self._buzzer.stop()
            self._stats.reset()
            self._display.clear()
            self._display.showText("Alarm stopped", 0, 0)
            self._display.showText("Press Grn to exit", 1, 0)

    def stateDo(self, state: int):
        """Executes sensor polling and non-blocking state tasks."""
        # State 0 - Welcome: poll ultrasonic sensor for presence
        if state == self.STATE_WELCOME:
            if self._sensor.tripped():
                self._model.processEvent("uss_trip")

        # State 4 - Alarm: 'do / play a 2 tone alarm' (unless silenced by red_press)
        elif state == self.STATE_ALARM and not self._alarm_silenced:
            now = time.ticks_ms()
            if time.ticks_diff(now, self._alarm_last_toggle) >= 250:
                self._alarm_last_toggle = now
                self._alarm_tone_high = not self._alarm_tone_high
                if self._alarm_tone_high:
                    self._buzzer.play(880)  # High tone (A5)
                else:
                    self._buzzer.play(587)  # Low tone (D5)

    # ==========================================
    # STATE ENTRY METHODS (Named as in UML Class Diagram)
    # ==========================================
    def welcome(self):
        """State 0: display 'Welcome to chilis'; light strip off."""
        self._buzzer.stop()
        self._display.clear()
        self._display.showText("Welcome to", 0, 0)
        self._display.showText("Chilis", 1, 0)
        self._lightStrip.setColor((0, 0, 0), self._lightStrip._numleds)

    def selection(self):
        """State 1: display 'How was your food service?'; start a 5 sec timer."""
        self._buzzer.stop()
        self._display.clear()
        # Split across 2 rows for 16x2 LCD
        self._display.showText("How was your", 0, 0)
        self._display.showText("food service?", 1, 0)
        self._timer.start(5)

    def happy(self):
        """State 2: display 'Thank you', play happy music, start 5 sec timer."""
        self._stats.add_happy()  # Logs vote internally in Python

        self._display.clear()
        self._display.showText("Thank you", 0, 0)

        # Play upbeat happy music (rising notes: C5, E5, G5)
        for tone in [523, 659, 784]:
            self._buzzer.play(tone)
            time.sleep_ms(120)
        self._buzzer.stop()

        self._timer.start(5)

    def unhappy(self):
        """State 3: display 'Sorry to hear that'; play sad tone; start 5 sec timer."""
        self._stats.add_unhappy()  # Logs vote internally in Python

        self._display.clear()
        self._display.showText("Sorry to", 0, 0)
        self._display.showText("hear that", 1, 0)

        # Play sad tone (descending notes: A4, F4)
        for tone in [440, 349]:
            self._buzzer.play(tone)
            time.sleep_ms(200)
        self._buzzer.stop()

        # Check satisfaction against 30% threshold
        pct = self._stats.calculate_percentage()
        if pct < self._threshold:
            self._model.processEvent("feedback_below_threshold")
        else:
            self._timer.start(5)

    def alarm(self):
        """State 4: display 'Calling manager'; light strip red."""
        self._alarm_silenced = False
        self._alarm_last_toggle = time.ticks_ms()
        self._alarm_tone_high = False

        self._display.clear()
        self._display.showText("Calling manager", 0, 0)
        self._display.showText("Press Red to stop", 1, 0)
        self._lightStrip.setColor((255, 0, 0), self._lightStrip._numleds)

    # ==========================================
    # EXECUTION RUNNER
    # ==========================================
    def run(self):
        """Main execution loop."""
        if hasattr(self._model, "start"):
            self._model.start()
        else:
            self.stateEntered(self.STATE_WELCOME)

        while True:
            if hasattr(self._timer, "check"):
                self._timer.check()

            self.stateDo(self._model.current_state if hasattr(self._model, "current_state") else self._model._curState)
            time.sleep_ms(20)
