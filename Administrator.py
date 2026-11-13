"""
Administrator.py
Administrator employee model with calendar-driven automatic availability.
"""
from Employee import Employee
from Calendar import Calendar
from Log import Log

class Administrator(Employee):
    """
    Represents an administrator whose availability is automatically derived from a Calendar.
    """
    def __init__(self, name: str, position: str, department: str, email: str, phoneNumber: str,
                 calendar: Calendar = None):
        super().__init__(name, position, department, email, phoneNumber)
        # Composition: 1 Administrator owns 1 Calendar
        self._calendar = calendar if calendar is not None else Calendar()
        Log.i(f"Administrator created: {self.name}")

    def getAvailability(self) -> str:
        """
        Returns availability dynamically retrieved from the calendar.
        """
        return self._calendar.getStatus()

    def showInfo(self) -> list:
        """
        Returns display lines for administrator:
        Line 1: Name
        Line 2: Position/Department
        """
        line1 = f"{self.name}"
        line2 = f"{self.position}"
        return [line1, line2]

    def cycleAvailability(self) -> bool:
        """
        Administrator availability is automatic and driven by the calendar.
        Manual cycling is not allowed; returns False.
        """
        Log.i(f"Administrator {self.name}: manual cycle rejected (calendar-managed)")
        return False
