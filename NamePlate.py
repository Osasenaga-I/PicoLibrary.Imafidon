"""
NamePlate.py
Controller component managing employee list navigation, button dispatch, and view updates.
"""
from NamePlateView import NamePlateView
from Log import Log

class NamePlate:
    """
    Coordinates employee data navigation, availability cycling, button event handling,
    and updates the associated NamePlateView.
    """
    def __init__(self, employees: list, buttons: list, view: NamePlateView):
        self._employees = employees if employees is not None else []
        self._currentEmployee = 0
        self._buttons = buttons if buttons is not None else []
        self._view = view

        # Wire each button handler back to this NamePlate controller
        for btn in self._buttons:
            btn.setHandler(self)

        Log.i(f"NamePlate initialized with {len(self._employees)} employees and {len(self._buttons)} buttons")

    def _updateView(self):
        """Helper to synchronize the view with the active employee."""
        if not self._employees:
            return
        emp = self._employees[self._currentEmployee]
        self._view.render(emp.showInfo())
        self._view.showAvailability(emp.getAvailability())

    def previousEmployee(self):
        """
        Navigates to the previous employee in the list (wraps around),
        updates the display, and plays a sound.
        """
        if not self._employees:
            return
        self._currentEmployee = (self._currentEmployee - 1) % len(self._employees)
        self._updateView()
        self._view.playSound()
        Log.i(f"Navigated to previous employee (index {self._currentEmployee})")

    def nextEmployee(self):
        """
        Navigates to the next employee in the list (wraps around),
        updates the display, and plays a sound.
        """
        if not self._employees:
            return
        self._currentEmployee = (self._currentEmployee + 1) % len(self._employees)
        self._updateView()
        self._view.playSound()
        Log.i(f"Navigated to next employee (index {self._currentEmployee})")

    def cycleAvailability(self):
        """
        Cycles the availability of the current employee if permitted.
        If successful, updates the lightstrip and plays feedback.
        """
        if not self._employees:
            return
        emp = self._employees[self._currentEmployee]
        success = emp.cycleAvailability()
        if success:
            self._view.showAvailability(emp.getAvailability())
            self._view.playSound()
            Log.i(f"Availability updated to {emp.getAvailability()}")
        else:
            Log.w("Availability cannot be cycled (automatic calendar control)")
            # Optional tactile feedback for disabled action
            self._view.playSound()

    def buttonPressed(self, name: str):
        """
        Dispatches button press events from Button callbacks based on button name.
        """
        n = str(name).strip().lower()
        Log.i(f"NamePlate: buttonPressed('{name}')")
        if "next" in n:
            self.nextEmployee()
        elif "prev" in n:
            self.previousEmployee()
        elif "avail" in n or "cycle" in n:
            self.cycleAvailability()

    def buttonReleased(self, name: str):
        """
        Callback hook for button release event.
        """
        Log.i(f"NamePlate: buttonReleased('{name}')")
