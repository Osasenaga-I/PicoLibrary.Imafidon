"""
Staff.py
Staff employee model with walk-in acceptance settings.
"""
from Employee import Employee
from Log import Log

class Staff(Employee):
    """
    Represents a staff member with walk-in policy indicator.
    """
    def __init__(self, name: str, position: str, department: str, email: str, phoneNumber: str,
                 walkInAcceptance: bool = True, available: str = "available"):
        super().__init__(name, position, department, email, phoneNumber, available)
        self._walkInAcceptance = walkInAcceptance
        Log.i(f"Staff created: {self.name}, walkInAcceptance: {self._walkInAcceptance}")

    def showInfo(self) -> list:
        """
        Returns display lines for staff:
        Line 1: Name
        Line 2: Position and walk-in acceptance
        """
        line1 = f"{self.name}"
        walk_in_text = "Walk-ins: Yes" if self._walkInAcceptance else "Walk-ins: No"
        return [line1, walk_in_text]
